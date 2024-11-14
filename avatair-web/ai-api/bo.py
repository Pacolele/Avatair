import random

import warnings
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from bolib.ComputeSpace import *
from bolib.Dimension import *
from bolib.Float01 import *
from bolib.Normalizer import *
from bolib.Parameter import *
from botorch.acquisition.monte_carlo import qExpectedImprovement
from botorch.fit import fit_gpytorch_mll
from botorch.models import SingleTaskGP
from botorch.optim import optimize_acqf
from botorch.sampling.normal import SobolQMCNormalSampler
from botorch.utils import standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from prompter import Prompter


class Bo:
    def __init__(self, values: dict, string_list: str, picture_amount: int, rating_scale: range = range(0, 10)) -> None:
        """
        Generates an image from specified string prompt.
        
        Args
        ----
            values dict: Dict of sorted lists with values to change the string_list variable.
            string_list str: String used for prompt where '@' is used to indicate what words should swap with what key from the values variable.
            picture_amount int: Int to indicate how many prompts should be created for each iteration.
            rating_scale range: Range to indicate what ratings are allowed.
        """
        if(not isinstance(values, dict)):
            raise Exception(f"values must be of the type {type(dict())}, but is {type(values)}")
        if(not isinstance(string_list, str)):
            raise Exception(f"string_list must be of the type {type(str())}, but is {type(string_list)}")
        if(not isinstance(picture_amount, (int))):
            try:
                picture_amount = int(picture_amount)
            except:
                raise Exception(f"picture_amount must be of the type {type(int())}, but is {type(picture_amount)}")
            
        self.BATCH_SIZE = picture_amount
        self.prompter = Prompter(values, string_list)
        self.compSpace, self.dimensions = self._get_space(values, rating_scale)
        self.rating_scale = rating_scale
        self.candidates: list[ParamList]
        self._init_candidates()

    def _init_candidates(self):
        """ Creates random initial candidates and updates candidates """
        normalized_candidates = []
        for _ in range(self.BATCH_SIZE):
            normalized_candidates.append(
                [random.random() for _ in self.dimensions])

        self._update_candidates(normalized_candidates)

    def _get_space(self, values: dict[str, (range, list[any])], rating_scale: range) -> tuple[ComputeSpace, list[DiscreteDimension]]:
        """
        Calculates the dimensions and creates a ComputeSpcace
        
        Args
        ----
            values dict: Dict of sorted lists with values to change the string_list variable.
            rating_scale range: Range to indicate what ratings are allowed.

        Returns
        -------
            ComputeSpace: ComputeSpace used for calculations
            List[Dimension]: Dimension used to indicate all different options for values.
        """
        dimensions = []
        for key in values:
            value = values[key]
            if isinstance(value, range):
                dimension = NumericDimension(
                    min=value.start, max=value.stop, name=key)
                dimensions.append(dimension)
            elif isinstance(value, list):
                dimension = DiscreteDimension(elements=value, name=key)
                dimensions.append(dimension)
            else:
                raise Exception(
                    "'values' should be a dict with either range or list as values: dict[str, (range, list[any])]")

        ranking_y = NumericDimension(
            min=rating_scale.start, max=rating_scale.stop, name="Rating")

        compSpace = ComputeSpace(x=dimensions, y=[ranking_y])
        return compSpace, dimensions

    def _probAQF(self, best_f, model) -> qExpectedImprovement:
        """
        Creates a qExpectedImprovement.
        
        Args
        ----
            best_f: The currently best rating.
            model: The model used for optimization.

        Returns
        -------
            qExpectedImprovement: the function used for optimization
        """
        sampler = SobolQMCNormalSampler(1024)
        qEI = qExpectedImprovement(model, best_f, sampler)
        return qEI

    def optimize(self, ratings: list[float]) -> list[str]:
        """
        Links the ratings to the last candidates and optimizes the model
        
        Args
        ----
            ratings list: The ratings of the previous prompts.
        """
        if not isinstance(ratings, list):
            raise Exception(f"rating must be of the type {type(list())}, but is {type(ratings)}")
        if len(ratings) > self.BATCH_SIZE:
            raise Exception(f"ratings must only hold less than or equal to {self.BATCH_SIZE} items, but holds {len(ratings)} items")
        
        for i in range(len(ratings)):
            if(not isinstance(ratings[i], (float, int))):
                try:
                    start_type = type(ratings[i])
                    ratings[i] = float(ratings[i])
                    warnings.warn(f"All vales in rating should be of type {type(float())}, but holds {start_type}")
                except:
                    raise Exception(f"All values in ratings must be of type {type(float())}, but is {type(ratings[i])}")
            if not (self.rating_scale.start <= ratings[i] and ratings[i] <= self.rating_scale.stop):
                raise Exception(f"Values in ratings must be between {self.rating_scale.start} and {self.rating_scale.stop} but is {ratings[i]}")


            candidate = self.candidates[i]
            rating = ratings[i]
            self.compSpace.add_value(candidate, rating)

        self._optimize()

    def _get_training_data(self) -> tuple[torch.Tensor, SingleTaskGP, torch.Tensor]:
        """
        Initiates the data for training

        Returns
        -------
            torch.Tensor: Tensor of the current train_Y
            botorch.models.gp_regressions.SingleTaskGP: A new model used for optimization
            torch.Tensor: Tensor of the current train_X
        """
        xn, yn = self.compSpace.normalized

        xt = torch.tensor(xn, dtype=torch.double)
        yt = torch.tensor(yn, dtype=torch.double)
        train_Y = standardize(yt)

        gp = SingleTaskGP(xt, train_Y)
        mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
        fit_gpytorch_mll(mll)
        return train_Y, gp, xt

    def _optimize(self):
        """
        Optimizes the model
        """
        bounds = torch.stack(
            [torch.zeros(self.compSpace.xdim), torch.ones(self.compSpace.xdim)])
        train_Y, gp, _ = self._get_training_data()
        best_f = torch.max(train_Y)
        af = self._probAQF(best_f, gp)
        candidate, _ = optimize_acqf(
            af, bounds=bounds, q=self.BATCH_SIZE, num_restarts=20, raw_samples=30)

        normalized_candidates = candidate.detach().cpu().numpy().tolist()
        self._update_candidates(normalized_candidates)

    def _update_candidates(self, normalized_candidates):
        """
        Denormalizes candidates and updates the attribute

        args
        ----
            normalized_candidates list: The new candidates. 

        """
        self.candidates = [self.compSpace.denormalize(
            candidate) for candidate in normalized_candidates]

    def get_prompts(self) -> list[str]:
        """
        Returns the prompts from the latest candidates

        return
        ------
            list: list of all prompts generated from the current candidates.

        """
        prompts = []

        for candidate in self.candidates:
            prompt = self.prompter.generate_prompt(candidate.normalized)
            prompts.append(prompt)
        return prompts

    def get_optimal_image(self) -> str:
        """
        Calculates the optimal image based on the trained model

        return
        ------
            str: The currently best prompt in the model.

        """
        train_Y, gp, X = self._get_training_data()
        with torch.no_grad():
            predictions = gp.posterior(
                X).mean.squeeze().cpu().numpy()
        best_index = np.argmax(predictions)
        best_features = X[best_index]
        best_prompt = self.prompter.generate_prompt(best_features)
        return best_prompt

    def plot(self):
        """
        Plot the current training data.
        """
        plt.figure(figsize=(8, 6))

        COLORS = ["red", "blue", "pink", "orange",
                  "green", "purple", "brown", "olive", "cyan"]

        train_X = self.compSpace.normalized[0]

        nr_of_dimension = len(self.dimensions)
        nr_of_data_points = len(train_X)

        print("Dimensions:", nr_of_dimension)
        print("nr of data points:", nr_of_data_points)

        for i in range(nr_of_dimension):
            plot_X = []
            for j in range(nr_of_data_points):
                plot_X.append(train_X[j][i])

            plt.scatter(plot_X, self.compSpace.normalized[1],
                        color=COLORS[i % 8], label=self.prompter.keys[i])

        plt.xlabel('Target')
        plt.ylabel('Input')
        plt.title('Training Data')
        plt.legend()
        plt.grid(True)

        plt.figure()
        x = list(range(0, (len(self.compSpace.normalized[0]))))
        y = list(self.compSpace.normalized[0])
        plt.plot(x, y)
        plt.show()


def normalize_value(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


def get_rating(data, variance=0):
    MAX = 10
    MIN = -3
    SPLITTER = ","

    data = data.split(SPLITTER)
    rating = int(data[0]) * int(data[1]) - int(data[2])
    return normalize_value(rating, MIN, MAX) * 10
    # -- Simulate human error -- DOESNT WORK
    normalized_rating = simulate_human_error(rating, MIN, MAX, variance)
    return normalized_rating


def simulate_human_error(value, min_value, max_value, error_range):
    noisy_value = value + random.uniform(-error_range, error_range)
    noisy_value = min(max_value, max(min_value, noisy_value))
    normalized_value = normalize_value(noisy_value, min_value, max_value)

    return normalized_value


def main():
    torch.set_printoptions(sci_mode=False)
    values = {
        "value_1": ["1", "2", "3"],
        "value_2": ["1", "2", "3", "4"],
        "value_3": ["2", "3", "4"],
    }
    string_list = "@value_1, @value_2, @value_3"

    optimizer = Bo(values, string_list, picture_amount="5")

    VARIANCE = 0
    ITERATIONS = 5
    for _ in range(ITERATIONS):
        denormalized_guessess = optimizer.get_prompts()
        ratings = []
        for guess in denormalized_guessess:
            print("Guess:", guess, end=" ")
            try:
                rating = get_rating(guess, VARIANCE)
                print("Rating:", rating)
            except:
                print("BREAKS")
                break

            ratings.append(rating)

        optimizer.optimize(ratings)
        denormalized_guessess = optimizer.get_prompts()

    prompt = optimizer.get_optimal_image()
    print("Prediction:", prompt, "Rating:", get_rating(prompt))
    # optimizer.plot()


if __name__ == "__main__":
    main()
