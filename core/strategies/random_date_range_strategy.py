"""
Random date range strategy for generating random dates within a range.

This strategy uses the mixin pattern to reduce boilerplate while maintaining functionality.
"""

from datetime import datetime

import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin
from utils.date_generator import generate_random_date


class RandomDateRangeStrategy(BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin):
    """
    Strategy for generating random dates within a specified range.

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

        # Seed initialization is handled by SeedMixin._initialize_random_seed()
        self.logger.debug(f"RandomDateRangeStrategy initialized with seed={self._seed}")

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
        # Get date generation parameters
        if isinstance(self.params["start_date"], str):
            start_date = datetime.strptime(
                self.params["start_date"], self.params["format"]
            )
        else:
            start_date = self.params["start_date"]
        if isinstance(self.params["end_date"], str):
            end_date = datetime.strptime(self.params["end_date"], self.params["format"])
        else:
            end_date = self.params["end_date"]

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        if "output_format" in self.params:
            params["output_format"] = self.params["output_format"]
        else:
            params["output_format"] = "%Y-%m-%d"

        # Generate the dates
        dates = [generate_random_date(**params) for _ in range(count)]
        return pd.Series(dates)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting RandomDateRangeStrategy state")
        self._initialize_state()

    # Use BaseStrategy.generate_data
