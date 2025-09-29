"""
Distributed choice strategy for generating values based on weighted choices.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~40 lines while maintaining the same functionality.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.domain_mixins import CategoricalMixin
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin
from core.strategy_config import DistributedChoiceConfig


class DistributedChoiceStrategy(
    BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin, CategoricalMixin
):
    """
    Strategy for generating values based on weighted choices.

    Uses mixins for:
    - SeedMixin: Automatic seed validation and random state initialization
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    - CategoricalMixin: Specialized categorical data validation and utilities
    """

    def _validate_params(self):
        """Delegate validation to DistributedChoiceConfig."""
        self._validate_required_params(["choices"])
        DistributedChoiceConfig(choices=self.params["choices"]).validate()

    def __init__(self, mode: str, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(mode=mode, logger=logger, **kwargs)

        # Use mixins for common functionality
        self._validate_seed()  # From SeedMixin
        self._initialize_random_seed()  # From SeedMixin
        self._initialize_state()  # From StatefulMixin
        self._validate_params()  # From ValidationMixin

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        super()._initialize_state()  # Call StatefulMixin's _initialize_state first

        # Seed initialization is handled by SeedMixin
        self.logger.debug(
            f"DistributedChoiceStrategy initialized with seed={self._seed}"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of data maintaining internal state.
        This method is stateful and maintains consistent random sequence.
        Args:
            count: Number of values to generate
        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(f"Generating chunk of {count} values")
        # Use the original generation logic
        """
        Generate random values based on weighted choices.

        Args:
            count: Number of values to generate

        Returns:
            Series of chosen values
        """
        choices_dict = self.params["choices"]

        # Extract choices and weights
        choices = list(choices_dict.keys())
        weights = list(choices_dict.values())

        # Generate random choices based on weights
        values = []

        # Calculate total weight
        total_weight = sum(weights)

        # Generate values proportionally based on weights
        for choice, weight in choices_dict.items():
            # Calculate how many values this choice should get
            proportion = weight / total_weight
            num_values = int(proportion * count)

            # Add the values for this choice
            for _ in range(num_values):
                values.append(choice)

        # Handle any remaining values due to rounding
        while len(values) < count:
            # Add random choice based on weights
            choice = np.random.choice(choices, p=[w / total_weight for w in weights])
            values.append(choice)

        return pd.Series(values, dtype=object)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting DistributedChoiceStrategy state")
        self._initialize_state()

    # def get_current_state(self) -> dict:
    #     """Get current state information for debugging"""
    #     return {
    #         "strategy": "DistributedChoiceStrategy",
    #         "stateful": True,
    #         "column": self.col_name,
    #         "seed": self.params.get("seed", None),
    #     }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate data by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.
        Args:
            count: Number of values to generate
        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )
        # For non-streaming mode, reset state to ensure consistent behavior
        if not self.is_streaming_and_batch():
            self.reset_state()
        # Generate the chunk
        result = self.generate_chunk(count)
        return result
