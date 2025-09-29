"""
Random name strategy for generating realistic person names using the names package.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~40 lines while maintaining the same functionality.
"""

import random

import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin
from utils.get_names import apply_case_formatting, get_name


class RandomNameStrategy(BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin):
    """
    Strategy for generating random person names with configurable parameters.
    Supports first names, last names, full names, gender filtering, and case formatting.
    Supports stateful generation with consistent random state.

    Uses mixins for:
    - SeedMixin: Automatic seed validation and random state initialization
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    """

    def __init__(self, mode, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(mode, logger, **kwargs)

        # Use mixins for common functionality
        self._validate_seed()  # From SeedMixin
        self._initialize_random_seed()  # From SeedMixin
        self._initialize_state()  # From StatefulMixin
        # Validation is handled by config via factory

    def sync_state(self, result: pd.Series):
        pass

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        super()._initialize_state()  # Call StatefulMixin's _initialize_state first

        # Store parameters for efficient access
        self._name_type = self.params["name_type"]
        self._gender = None if self.params["gender"] == "any" else self.params["gender"]
        self._case_format = self.params["case"]

        self.logger.debug(
            f"RandomNameStrategy initialized with name_type={self._name_type}, "
            f"gender={self._gender}, case={self._case_format}, seed={self._seed}"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of random names maintaining internal random state.
        This method is stateful and maintains consistent random sequence.

        Args:
            count: Number of names to generate

        Returns:
            pd.Series: Generated names
        """
        self.logger.debug(
            f"Generating chunk of {count} names (type={self._name_type}, gender={self._gender})"
        )

        result = []
        for _ in range(count):
            # Generate the name using the names package
            name = get_name(name_type=self._name_type, gender=self._gender)

            # Apply case formatting
            formatted_name = apply_case_formatting(name, self._case_format)

            result.append(formatted_name)

        return pd.Series(result, dtype=str)

    def reset_state(self):
        """Reset the internal random state to initial values"""
        super().reset_state()  # Call StatefulMixin's reset_state
        # Re-initialize random state with original seed
        if self._seed is not None:
            random.seed(self._seed)
        # Re-derive any cached fields from current params for pooled reuse
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        state = super().get_current_state()  # Get base state from StatefulMixin
        state.update(
            {
                "name_type": self._name_type,
                "gender": self._gender,
                "case_format": self._case_format,
            }
        )
        return state

    # Use BaseStrategy.generate_data
