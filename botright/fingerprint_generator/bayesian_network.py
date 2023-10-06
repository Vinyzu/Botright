from __future__ import annotations

import json
import random
from typing import Optional, List

# Ported/Translated From: https://github.com/apify/fingerprint-suite/blob/master/packages/generative-bayesian-network/src/bayesian-network.ts
class BayesianNode:
    def __init__(self, node_definition: dict) -> None:
        """
        Initialize a BayesianNode instance.

        Args:
            node_definition (dict): The definition of the Bayesian node.
        """
        self.node_definition = node_definition

    def get_probabilities_given_known_values(self, parent_values: Optional[dict] = None) -> dict:
        """
        Get conditional probabilities given known parent values.

        Args:
            parent_values (Optional[dict]): Dictionary of known parent values.

        Returns:
            dict: Conditional probabilities.
        """
        parent_values = parent_values or {}

        probabilities = self.node_definition['conditionalProbabilities']
        for parent_name in self.parent_names:
            parent_value = parent_values.get(parent_name, None)
            if parent_value in probabilities.get('deeper', {}):
                probabilities = probabilities['deeper'][parent_value]
            else:
                probabilities = probabilities['skip']

        return probabilities

    def sample_random_value_from_possibilities(self, possible_values: List[str], total_probability_of_possible_values: float, probabilities: dict) -> str:
        """
        Sample a random value from possibilities based on probabilities.

        Args:
            possible_values (List[str]): List of possible values.
            total_probability_of_possible_values (float): Total probability of possible values.
            probabilities (dict): Probability distribution.

        Returns:
            str: Chosen value.
        """
        chosen_value = possible_values[0]
        anchor = random.random() * total_probability_of_possible_values
        cumulative_probability = 0
        for possible_value in possible_values:
            cumulative_probability += probabilities[possible_value]
            if cumulative_probability > anchor:
                chosen_value = possible_value
                break
        return chosen_value

    def sample(self, parent_values: Optional[dict] = None) -> str:
        """
        Sample a value for the node.

        Args:
            parent_values (Optional[dict]): Dictionary of known parent values.

        Returns:
            str: Sampled value.
        """
        parent_values = parent_values or {}

        probabilities = self.get_probabilities_given_known_values(parent_values)
        possible_values = list(probabilities.keys())
        return self.sample_random_value_from_possibilities(possible_values, 1.0, probabilities)

    @property
    def name(self) -> str:
        """
        Get the name of the Bayesian node.

        Returns:
            str: Node name.
        """
        return self.node_definition['name']

    @property
    def parent_names(self) -> List[str]:
        """
        Get the names of parent nodes.

        Returns:
            List[str]: List of parent node names.
        """
        return self.node_definition['parentNames']


class BayesianNetwork:
    def __init__(self, path: str) -> None:
        """
        Initialize a BayesianNetwork instance.

        Args:
            path (str): Path to the network definition file.
        """
        self.nodes_in_sampling_order = []
        self.nodes_by_name = {}
        with open(path, 'r', encoding='utf-8') as file:
            network_definition = json.load(file)
            self.nodes_in_sampling_order = [BayesianNode(node_definition) for node_definition in network_definition['nodes']]
            self.nodes_by_name = {node.name: node for node in self.nodes_in_sampling_order}

    def generate_sample(self, input_values: Optional[dict] = None) -> dict:
        """
        Generate a sample based on input values.

        Args:
            input_values (Optional[dict]): Dictionary of input values.

        Returns:
            dict: Generated sample.
        """
        input_values = input_values or {}

        generated_sample = input_values.copy()
        for node in self.nodes_in_sampling_order:
            if node.name not in generated_sample:
                generated_sample[node.name] = node.sample(generated_sample)
        return self.process_stringified_result(generated_sample)

    def process_stringified_result(self, data: dict) -> dict:
        """
        Process a stringified result.

        Args:
            data (dict): Data to be processed.

        Returns:
            dict: Processed data.
        """
        def process_value(value):
            if value.startswith('*STRINGIFIED*'):
                return json.loads(value[len('*STRINGIFIED*'):])
            elif value.startswith('*MISSING_VALUE*'):
                return None
            return value

        # Process the JSON-like data into a Python dictionary
        processed_data = {key: process_value(value) for key, value in data.items()}
        return processed_data
