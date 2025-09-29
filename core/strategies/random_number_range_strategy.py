"""
Random number range strategy for generating numbers within a range.

This strategy uses the mixin pattern to reduce boilerplate while maintaining functionality.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin


class RandomNumberRangeStrategy(
    BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin
):
    """
    Strategy for generating random numbers within a specified range.
    Supports stateful generation with consistent random state.

    Uses mixins for:
    - SeedMixin: Automatic seed validation and random state initialization
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(mode=mode, logger=logger, **kwargs)

        # Use mixins for common functionality
        self._validate_seed()  # From SeedMixin
        self._initialize_random_seed()  # From SeedMixin
        self._initialize_state()  # From StatefulMixin
        # Validation is handled by config via factory

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        super()._initialize_state()  # Call StatefulMixin's _initialize_state first

        # Initialize random state (seed handled by SeedMixin)
        self._random_state = np.random.RandomState(self._seed)

        # Store bounds for efficient access
        self._lower = float(self.params["start"])
        self._upper = float(self.params["end"])
        self._is_integer = isinstance(self.params["start"], int) and isinstance(
            self.params["end"], int
        )

        self.logger.debug(
            f"RandomNumberRangeStrategy initialized with range=[{self._lower}, {self._upper}], "
            f"integer={self._is_integer}, seed={self._seed}"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of random numbers maintaining internal random state.
        This method is stateful and maintains consistent random sequence.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(
            f"Generating chunk of {count} random numbers in range [{self._lower}, {self._upper}]"
        )

        # Generate random numbers using internal state
        values = self._random_state.uniform(self._lower, self._upper, count)

        # Convert to integers if both bounds are integers
        if self._is_integer:
            values = values.astype(int)

        return pd.Series(values, dtype=int if self._is_integer else float)


    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        state = super().get_current_state()  # Get base state from StatefulMixin
        state.update(
            {
                "lower_bound": self._lower,
                "upper_bound": self._upper,
                "is_integer": self._is_integer,
                "random_state_type": type(self._random_state).__name__,
            }
        )
        return state

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting RandomNumberRangeStrategy state")
        super().reset_state()
        self._initialize_state()

    # Use BaseStrategy.generate_data
