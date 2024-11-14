import base64
import json
from io import BytesIO
from typing import Dict
import uvicorn
from avatargenerator import AvatarGenerator
import base64
import json
from datetime import datetime, timedelta
import config
from bo import Bo
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
USER_TIMEOUT_TIME = timedelta(hours = config.user_timeout_hours, 
                         minutes = config.user_timeout_minutes)    # If a user has been inactive for this amount of time they will be removed.


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to the appropriate origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "FETCH", "PATCH"],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin"],
)

class User:
    def __init__(self, user_id : str, BO_instance : Bo):
        """
            Creates a new User object.

            Parameters
            ----------
            user_id : str 
                String representing id for user.
            BO_instance: BO
                A unique instance of BO object.
        """    
        self.user_id = user_id
        self.BO_instance = BO_instance
        self.iteration = 0
        self.last_time_accessed = datetime.now()


    def get_iteration(self) -> int:
        """
            Get current iteration value of user.

            Returns
            -------
            int
                Value of current iteration step.
        """
        return self.iteration
    
    def get_user_id(self) -> str:
        """
            Get user id of user.

            Returns
            -------
            str
                String of the user id.
        """
        return self.user_id

    def get_BO_instance(self) -> Bo:
        """
            Get BO instance of user.

            Returns
            -------
            BO
                User's BO instance.
        """
        return self.BO_instance
    
    def get_last_time_accessed(self) -> datetime:
        """
            Get datetime representing last time user accessed the api application.

            Returns
            -------
            Datetime
                Datetime object of last time user accessed this application.
        """
        return self.last_time_accessed
    
    def get_prompts(self) -> list[str]:
        """
            Get prompts from BO instance.

            Returns
            -------
            list[str]
                A list of strings, each string is a prompt representing an avatar.
        """
        return self.BO_instance.get_prompts()
    
    def get_result(self) -> str:
        """
            Get prompt which is the optimal result the BO object has produced.

            Returns
            -------
            str
                String of optimal prompt for avatar.
        """
        return self.BO_instance.get_optimal_image()
    
    def run_optimize(self, ratings : list) -> None:
        """
            Runs an optimization step with provided ratings.

            Parameters
            ----------
            ratings : list 
                List of values for every avatar that has been presented.
        """
        self.BO_instance.optimize(ratings)
        self.iteration += 1

    def update_last_time_accessed(self) -> None:
        """
            Updates user's last time accessed to current time.
        """
        self.last_time_accessed = datetime.now()




@app.on_event("startup")
def startup():
    """
        Initializes the application.
    """
    app.AvatarGenerator = AvatarGenerator()
    app.active_users = {}
    app.last_time_cleaned_up = datetime.now()


# Test function to write the content of AvatarPrompt


@app.get("/")
def index():
    return "Hello world"


@app.post("/survey")
async def start_survey(request : Request):
    """
        Path for POST /survey. Setups a new user with provided survey data in request.

        Parameters
        ----------
        request : Request 
            The HTTP request with survey information included in body, see :meth:`setup_new_user` and :meth:`validateVariables`.

    """
    survey_info = await request.json()    
    
    user = setup_new_user(survey_info)

    return {"message": "Survey started successfully", 
            "user_id": user.get_user_id, 
            "prompts": user.get_prompts}

@app.post("/optimize")
async def optimize(request : Request):
    """
        Path for POST /optimize. Performs an optimization iteration with provided ratings from a user.

        Parameters
        ----------
        request : Request 
            The HTTP request, body should include field:
                "responseId": Survey response id (will be equivalent to user_id in this context).
                "ratings": List of rating (each rating should be a value between 0-1).

    """
    
    body = await request.json()
    print("==================================")
    user_id = body.get("responseId")
    ratings = body.get("ratings")
    print("ratings: " + str(ratings))  

    user = get_user(user_id)
    user.run_optimize(ratings)
    new_prompts = user.get_prompts()
    print(new_prompts)

    user.update_last_time_accessed()

    return {"result": new_prompts}


@app.post("/result")
async def finalResult(request : Request):
    """
        Path for POST /result. Returns a response with prompt and related image.\n
        Will remove the user after prompt and image has been generated since the survey response is done at this stage.

        Parameters
        ----------
        request : Request 
            The HTTP request, body should include field:
                "responseId": Survey response id (will be equivalent to user_id in this context).

        Returns
        -------
        Response
            A HTTP response with JSON object including:
                "prompt": Prompt for image generated.
                "image": Image generated.
    """
    body = await request.json()
    user_id = body.get("responseId")
    # bo_instance = getBoInstance(user_id)
    # prompt = bo_instance.get_optimal_image()

    user = get_user(user_id)
    prompt = user.get_result()

    image = app.AvatarGenerator.generate_image_from_prompt(prompt)
    img_byte_array = BytesIO()
    image.save(img_byte_array, format="PNG")

    # Get the bytes of the image
    img_bytes = img_byte_array.getvalue()
    image_base64 = base64.b64encode(img_bytes).decode('utf-8', 'ignore')

    delete_user(user_id)

    # Return the image as a response with appropriate content type
    return Response(content=json.dumps({"prompt": prompt, "image": image_base64}), media_type="application/json")


@app.post("/avatar")
async def get_avatar(request : Request):
    """
        Path for POST /avatar. Returns a response with prompt and related image.

        Parameters
        ----------
        request : Request
            The HTTP request, body should include fields:
                "iterations":   Index for prompt & image generation.
                "responseId":  Survey response id (will be equivalent to user_id in this context).

        Returns
        -------
        Response
            A HTTP response with JSON object including:
                "prompt": Prompt for image generated.
                "image": Image generated.
    """
    body = await request.json()
    index = body.get("iterations")
    user_id = body.get("responseId")

    user = get_user(user_id)
    prompts = user.get_prompts()

    image = app.AvatarGenerator.generate_image_from_prompt(prompts[index])
    img_byte_array = BytesIO()
    image.save(img_byte_array, format="PNG")

    # Get the bytes of the image
    img_bytes = img_byte_array.getvalue()

    # Convert and decode image to base64.
    image_base64 = base64.b64encode(img_bytes).decode('utf-8', 'ignore')

    # Return the image as a response with appropriate content type
    return Response(content=json.dumps({"prompt": prompts[index], "image": image_base64}), media_type="application/json")

def get_user(userId : str) -> User:
    """
        Retrieves a user from app.active_users

        Parameters
        ----------
        userId : str 
            String of the user id for the user that should be retrieved.

        Returns
        -------
        user : User
            A User object.
    """
    user = app.active_users[userId]
    if (user): 
        user.update_last_time_accessed()
    return user


def delete_user(userId : str) -> None:
    """
        Removes a user from app.active_users dictionary.

        Parameters
        ----------
        userId : str 
            String of the user id that should be removed.

    """
    del app.active_users[userId]
    return


def remove_inactive_users() -> None:
    """
        Removes inactive users from app.active_users dictionary.
    """
    inactive_users = []
    for user in app.active_users.values():
        if (user.get_last_time_accessed() + USER_TIMEOUT_TIME) < datetime.now():
            inactive_users.append(user.get_user_id())
    for inactive_user in inactive_users:
        delete_user(inactive_user)
    return


def setup_new_user(survey_info : dict) -> User:
    """
        Creates a new user from provided survey.

        Parameters
        ----------
        survey_info : dict 
            Dictionary with information about the survey.

        Returns
        -------
        user : User
            A new User object.
    """
    # Before making a new user we check for inactive users and remove them.
    remove_inactive_users()


    # Extract survey info variables
    values = survey_info.get("preVariables")
    if survey_info.get("genVariables"):
        values = values | survey_info.get("genVariables")
    values = validateVariables(values)
    prompt = survey_info.get("prompt")
    print(prompt)
    size = int(survey_info.get("size"))         # Change name of size variable to picture amount or something more fitting
    
    # Create BO instance with variables above
    print(f"Size: {size}")
    bo_instance = Bo(values, prompt, picture_amount=size, rating_scale=range(1))

    # Create new user with the ID and save it in active users
    user_id = survey_info.get("responseId")
    print(f"Creating user with id: {user_id}.")
    user = User(user_id = user_id, BO_instance = bo_instance)
    app.active_users[user_id] = user

    return user


def validateVariables(values : dict) -> dict:
    """
        Validates and cleans up variables in dictionary.

        Parameters
        ----------
        values : dict 
            Dictionary with variables and their values.

        Returns
        -------
        values : dict
            Cleaned up and validated dictionary of values.
    """
    print(f" =========== VALUES =========\n{values}")
    keys_to_remove = [key for key,
                      val in values.items() if val == [] or key == "_id"]
    # Remove the keys from the dictionary
    for key in keys_to_remove:
        values.pop(key)

    # Convert values that are strings representing ranges to a range object for BO
    val = values.get("agerange")
    values["agerange"] = range(val[0], val[1] + 1)
    print(f" =========== AFTER =========\n{values}")
    return values



if __name__ == "__main__":
    uvicorn.run("main:app", port=3333, log_level="info", reload=True)
