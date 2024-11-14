import re
import warnings
from math import floor

from torch import Tensor


class Prompter:

    def __init__(self, values, prompt) -> None:
        """
            Creates a Prompter class object.
            Args:
                values dict: Dictionary where keys are variable names and values are what values the variable name can be. Values have to be a list of string or a range object.
                string_list list[string]: A list of strings where "variables" have a '@' as identifier.

        """
        if (not isinstance(values, dict)):
            raise Exception(
                "values parameter must be a dictionary with key as a variable name and it's value as a list or a range object.")
        # Check string_list so that it only includes the correct instance.
        elif (not isinstance(prompt, str)):
            raise Exception(
                "prompt parameter must be a string")
        self.values = values
        self.prompt = prompt
        self.keys = list(values.keys())

    def generate_prompt(self, data):
        """
            Generates a string prompt from data values.
            Args:
                data list[float]: List of float values to translate.
            Returns:
                string: A full string from string_list where variables have been assigned.
        """
        if not (isinstance(data, (list, Tensor))):
            raise Exception("data parameter must be a list of floats")

        variable_identifier = "@"
        result = (self.prompt + ".")[:-1]

        for i in range(len(self.keys)):
            pattern = r'@' + re.escape(self.keys[i])
            result = re.subn(pattern, self.value_to_string(
                data[i], self.values.get(self.keys[i])), result)
            if(result[1] == 0):
                warnings.warn("The prompt does not have all the corresponding values.")
            result = result[0]
        if re.search(r'@', result):
            warnings.warn("Some values in the prompt does not contain a corresponding value.")

        return result

    def value_to_string(self, value, variable_values):
        """
            Generates a string from a value in a list or range.
            Args:
                value float: Value to be converted. Value can be between 0.0 and 1.0 (both inclusive).
                variable_values list[string] or range object: Objects to find string from.
            Returns:
                A string from variable_values.
        """
        if (value > 1) or (value < 0):
            raise Exception(
                f"Value ({value}) must be between 0.0 and 1.0 (inclusive).")

        if not (isinstance(variable_values, (list, range))):
            raise Exception("Variable_values must be a list or range object.")

        item_range = 1 / len(variable_values)
        item_index = floor(value / item_range)
        if item_index == len(variable_values):            # for when tensor == 1
            item_index -= 1

        item = variable_values[item_index]
        return str(item)


if __name__ == "__main__":
    values = {"value_1": ["small", "medium", "large"], "value_2": [
        "green", "red", "blue", "yellow"], "value_3": range(10, 20)}

    string_list = "@value_1, @value_2, @value_3"
    a = Prompter(values, string_list)

    data = [1, 1, 0.00]
    print(a.generate_prompt(data))

    data = [0.9, 1, 0.09]
    print(a.generate_prompt(data))

    data = [0.9, 1, 0.1]
    print(a.generate_prompt(data))
