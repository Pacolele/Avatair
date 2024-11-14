<script lang="ts">
    import Slider from "./sliderRating";
    import Stars from "./starRating";
    import { api } from "$lib/API";
    import type { AxiosResponse } from "axios";

    //import Ratings from "@skeletonlabs/skeleton";
    let userID = "";
    let surveyId: string | null = "";
    let currIteration: number = 0;
    let ratings: number[] = [];
    let cards:  any[] = [];
    let survey: any;
    let canGoToNextPage:boolean = true;

    let trigger: boolean = true; // Update to trigger nextIteration

    async function getSurvey() {
        const urlParams = new URLSearchParams(window.location.search);
        surveyId = urlParams.get("survey");

        if (!surveyId) window.location.replace("/not_found");
        console.log("id: " + surveyId);
        
        const response = await api.fetch('survey' + '/' + surveyId)

        console.log("resp", response);
        if (response.status == 400 || response.status == 401)
            window.location.replace("/not_found");

        
        survey = response.data;
        console.log("survey parameters: " + JSON.stringify(survey));

        if (survey.parameters.welcomePage) currIteration = -1;

        for (let i = 0; i < survey.parameters.avatarsPerPage; i++) {
            ratings[i] = 0;
        }

        return survey;
    }

    async function initialize(retry = true) {
        let responseSuccessCode = 201;

        async function tryAgain(response:AxiosResponse<any, any>){
            console.log("Error initializing; " + response.status.toString() + " " +  response.statusText);
            return await initialize(false)
        }

        await api.fetch(
                    "response/create", 
                    "post", 
                    {"Content-Type": "application/json",},
                    {surveyId: surveyId,})
                    .then(async function (response) {
                        if (response.status == responseSuccessCode)
                        {
                            userID = response.data.responseid;
                            await api.fetch(
                                "response/initialize", 
                                "post", 
                                {"Content-Type": "application/json",},
                                {
                                    responseId: userID,
                                    prompt: survey.prompt,
                                })
                                .then(async function (response) {
                                    if (!(response.status == responseSuccessCode) && retry)
                                    {
                                        return await tryAgain(response)
                                    }
                                })
                        }
                        else 
                        {
                            if (retry)
                            {
                                return await tryAgain(response);
                            }
                        }

                    }) 
    }
    async function nextIteration(trigger: boolean) {
        canGoToNextPage = false;
        let images:any[] = [];
        try{
            if (currIteration == 0) {
                await initialize();
            } else {
                await optimize();
            }
            config.score = 0.0; // Reset star-rating
            resetSliderValues()
            canGoToNextPage = true;
            images = await getImages();
        }catch(e:any){
            console.log((e as Error).message);
            canGoToNextPage = true;
        }  
        return images
    }
    async function optimize(retry = true) {
        let responseSuccessCode = 200;
        let success = false;
        await api.fetch(
                    "response/optimize", 
                    "patch", 
                    {"Content-Type": "application/json",},
                    {
                        ratings: ratings,
                        responseId: userID,
                    })
                    .then(async function (response) {
                        if (response.status == responseSuccessCode) 
                        {
                            success = true;
                        }
                        else 
                        {
                            console.log("Error sending ratings; " + response.status.toString() + " " +  response.statusText);
                            if (retry)
                            {
                                success = await optimize(false);
                            }
                        }
                    }
                )
        return success
    }

    const config = {
        readOnly: false,
        countStars: 5,
        range: {
            min: 0,
            max: 5,
            step: 0.5,
        },
        score: 0.0,
        showScore: false,
        scoreFormat: function () {
            return `(${this.score.toFixed(0)}/${this.countStars})`;
        },
        name: "",
        starConfig: {
            size: 30,
            fillColor: "#83BBFD",
            strokeColor: "#222FA8",
            unfilledColor: "#D9D9D9",
            strokeUnfilledColor: "#000",
        },
    };

    async function finalImage(trigger: boolean) {
        let image: any[] = [];
        let responseSuccessCode = 201;
        await optimize()
        .then(async function(result) {
            if (result) 
            {
                await api.fetch(
                    "response/result", 
                    "post",
                    {"Content-Type": "application/json",},
                    {responseId: userID,},
                    "blob"
                )
                .then((response) => {
                    if (response.status == responseSuccessCode) 
                    {
                        image[0] = window.URL.createObjectURL(response.data);
                    }
                    else
                    {
                        console.log("Error getting result image; " + response.status.toString() + " " +  response.statusText);
                    }
                });
            }
        })
        return image;
    }
    async function getAvatar(index: number) {
        const response = await api.fetch(
            "avatar/generate", 
            "post",
            {"Content-Type": "application/json",},
            {
                responseId: userID,
                iterations: index,
            },
            "blob"
        );
        return window.URL.createObjectURL(response.data);
    }
    async function getImages() {
        let images = []
        for (let i = 0; i < survey.parameters.avatarsPerPage; i++) 
        {
            images[i] = await getAvatar(i);
        }
        return images;
    }

    //TEMP VARS FOR PRESENTATION
    let tempStars = [];

    function saveSliderRating(index: number, rating: number[]) {
        try{
            ratings[index] = rating[0]/100;
        }catch(e){
            /* Weird error, 
            don't really understand how sliders have been setup to track current value,
            but can see that it's the left value in rating array that is the current position
            of the slider. Taking rating[0] sometimes gives an error.
            */
           console.log(e)
           ratings[index] = 0;
        }
    }

    function increaseIteration() {
        // Prevents user from proceeding while waiting for result
        if (!canGoToNextPage) {
            return
        }
        currIteration++;
        trigger = !trigger;
    }
    function resetSliderValues() {
        for (let i = 0; i < ratings.length; i++){
            ratings[i] = 0
        }
    }
</script>

<main>
    {#await getSurvey()}
        <p>Loading...</p>
    {:then survey}
        {#if currIteration == -1}
            <h1>{survey.welcomePage.title}</h1>
            <p>{@html survey.welcomePage.content}</p>

            <button
                id="next-button"
                class="button button-purple"
                on:click={increaseIteration}>Next Page</button
            >
        {:else if currIteration > survey.parameters.maxIterations}
            <h1>{survey.endPage.title}</h1>
            <p>{@html survey.endPage.content}</p>
        {:else if currIteration < survey.parameters.maxIterations}
            <h1>{survey.title}</h1>
            <div class="card-container">
                {#await nextIteration(trigger)}
                    <p>Loading...</p>
                {:then images}
                    {#each { length: images.length } as _, card}
                        <div class="avatar-card">
                            <img
                                class="picture"
                                alt="avatair portrait"
                                src={images[card]}
                            />
                            {#each { length: survey.ratingScales.length } as _, rating}
                                {#if survey.ratingScales[rating].type == "Slider"}
                                    <div class="rating slider">
                                        <h3>
                                            {survey.ratingScales[rating].name}
                                        </h3>
                                        <div class="labels">
                                            <p>
                                                {survey.ratingScales[rating]
                                                    .labelBad}
                                            </p>
                                            <p>
                                                {survey.ratingScales[rating]
                                                    .labelGood}
                                            </p>
                                        </div>
                                        <Slider
                                            bind:componentRating={cards[card]}
                                            on:input={(e) =>
                                                saveSliderRating(
                                                    card,
                                                    e.detail,
                                                )}
                                        />
                                        {#if survey.ratingScales[rating].text != ""}
                                            <p>
                                                {survey.ratingScales[rating]
                                                    .text}
                                            </p>
                                        {/if}
                                    </div>
                                {:else if survey.ratingScales[rating].type == "Star Rating"}
                                    <div class="rating stars">
                                        <h3>
                                            {survey.ratingScales[rating].name}
                                        </h3>
                                        <div class="labels">
                                            <p>
                                                {survey.ratingScales[rating]
                                                    .labelGood}
                                            </p>
                                            <p>
                                                {survey.ratingScales[rating]
                                                    .labelBad}
                                            </p>
                                        </div>
                                        <Stars
                                            config={{
                                                readOnly: false,
                                                countStars: 5,
                                                range: {
                                                    min: 0,
                                                    max: 5,
                                                    step: 0.5,
                                                },
                                                score: 0.0,
                                                showScore: false,
                                                scoreFormat: function () {
                                                    return `(${this.score.toFixed(0)}/${this.countStars})`;
                                                },
                                                name: "",
                                                starConfig: {
                                                    size: 30,
                                                    fillColor: "#83BBFD",
                                                    strokeColor: "#222FA8",
                                                    unfilledColor: "#D9D9D9",
                                                    strokeUnfilledColor: "#000",
                                                },
                                            }}
                                            bind:componentRating={tempStars[
                                                rating
                                            ]}
                                        />
                                        {#if survey.ratingScales[rating].text != ""}
                                            <p>
                                                {survey.ratingScales[rating]
                                                    .text}
                                            </p>
                                        {/if}
                                    </div>
                                {/if}
                            {/each}
                        </div>
                    {/each}
                {/await}
            </div>

            <p>{currIteration + 1} / {survey.parameters.maxIterations}</p>

            <button
                id="next-button"
                class="button button-purple"
                on:click={() => {
                    increaseIteration();
                }}>Next Page</button
            >
        {:else}
            <h1>This is your result:</h1>
            <!-- New function finalImage() that generates -->
            {#await finalImage(trigger)}
                <p>Loading...</p>
            {:then images}
                <img id="final-picture" class="picture" src={images[0]} />
            {/await}

            {#if survey.parameters.endPage}
                <button
                    id="next-button"
                    class="button button-purple"
                    on:click={() => {
                        currIteration++;
                        trigger = !trigger;
                    }}>Next Page</button
                >
            {/if}
        {/if}
    {/await}
</main>

<style>
    @import "/static/css/fonts.css";
    @import "/static/css/button.css";
    @import "/static/css/survey.css";
</style>
