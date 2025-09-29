"""
Distributed date range strategy for generating date values from multiple weighted
date ranges.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~40 lines while maintaining the same functionality.
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.domain_mixins import DateTimeMixin
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin
from core.strategy_config import DateRangeItem


class DistributedDateRangeStrategy(
    BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin, DateTimeMixin
):
    """
    Strategy for generating random date values from multiple weighted date ranges.

    Output values are strings formatted per each range's `output_format`.

    Uses mixins for:
    - SeedMixin: Automatic seed validation and random state initialization
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    - DateTimeMixin: Specialized datetime validation and utilities
    """

    def _generate_random_date_in_range(self, range_item: DateRangeItem) -> str:
        """Generate a single random date within the specified range"""
        start_date = datetime.strptime(range_item.start_date, range_item.format)
        end_date = datetime.strptime(range_item.end_date, range_item.format)

        # Calculate the total number of days between start and end
        total_days = (end_date - start_date).days

        # Generate a random number of days to add to start_date
        random_days = random.randint(0, total_days)

        # Calculate the random date
        random_date = start_date + timedelta(days=random_days)

        # Format the date according to output_format
        return random_date.strftime(range_item.output_format)

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

        # Seed initialization is handled by SeedMixin
        self.logger.debug(
            f"DistributedDateRangeStrategy initialized with seed={self._seed}"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of data maintaining internal state.
        This method is stateful and maintains consistent random sequence.
        Args:
            count: Number of values to generate
        Returns:
            pd.Series: Generated date strings (formatted using each range's `output_format`)
        """
        self.logger.debug(f"Generating chunk of {count} values")
        # Use the original generation logic
        """
        Generate random date values from multiple weighted date ranges.
        Args:
            count: Number of values to generate
        Returns:
            Series of random date values
        """
        ranges = self.params["ranges"]

        # Calculate the number of values to generate from each range
        distributions = [r.distribution for r in ranges]
        total_dist = sum(distributions)

        # Normalize distributions
        normalized_dist = [d / total_dist for d in distributions]

        # Calculate counts for each range
        range_counts = np.random.multinomial(count, normalized_dist)

        # Generate values for each range
        all_values = []
        for i, range_item in enumerate(ranges):
            range_count = range_counts[i]
            if range_count == 0:
                continue

            # Generate date values for this range
            for _ in range(range_count):
                date_value = self._generate_random_date_in_range(range_item)
                all_values.append(date_value)

        # Return as strings per tests expectations
        return pd.Series(all_values)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting DistributedDateRangeStrategy state")
        self._initialize_state()

    # def get_current_state(self) -> dict:
    #     """Get current state information for debugging"""
    #     return {
    #         "strategy": "DistributedDateRangeStrategy",
    #         "stateful": True,
    #         "column": self.col_name,
    #         "seed": self.params.get("seed", None),
    #     }

    # Use BaseStrategy.generate_data
