"""
Distributed time range strategy for generating time values from multiple weighted time ranges.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~40 lines while maintaining the same functionality.
"""

from datetime import datetime, time

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.domain_mixins import DateTimeMixin
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin
from core.strategy_config import TimeRangeItem


class DistributedTimeRangeStrategy(
    BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin, DateTimeMixin
):
    """
    Strategy for generating random time values from multiple weighted time ranges.
    Output values are strings formatted per each range's `format`.

    """

    # Validation handled via DistributedTimeRangeConfig in factory

    def _time_to_seconds(self, time_str: str, format_str: str) -> int:
        """Convert time string to seconds since midnight"""
        time_obj = datetime.strptime(time_str, format_str).time()
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

    def _seconds_to_time_str(self, seconds: int, format_str: str) -> str:
        """Convert seconds since midnight to time string"""
        # Handle overflow (next day)
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        time_obj = time(hours, minutes, secs)
        return time_obj.strftime(format_str)

    def _generate_random_time_in_range(self, range_item: TimeRangeItem) -> str:
        """Generate a single random time within the specified range"""
        start_seconds = self._time_to_seconds(range_item.start, range_item.format)
        end_seconds = self._time_to_seconds(range_item.end, range_item.format)

        # Handle overnight ranges (e.g., 22:00:00 to 06:00:00)
        if end_seconds <= start_seconds:
            # This is an overnight range; randomly choose segment using numpy RNG
            if np.random.rand() < 0.5:
                # Before midnight: start_seconds to 24*3600 - 1
                random_seconds = int(np.random.randint(start_seconds, 24 * 3600))
            else:
                # After midnight: 0 to end_seconds
                random_seconds = int(np.random.randint(0, end_seconds + 1))
        else:
            # Normal range within the same day (inclusive of end)
            random_seconds = int(np.random.randint(start_seconds, end_seconds + 1))

        return self._seconds_to_time_str(random_seconds, range_item.format)

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
            f"DistributedTimeRangeStrategy initialized with seed={self._seed}"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of data maintaining internal state.

        This method is stateful and maintains consistent random sequence.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated time strings (formatted per range `format`)
        """

        self.logger.debug(f"Generating chunk of {count} values")

        # Use the original generation logic
        """
        Generate random time values from multiple weighted time ranges.

        Args:
            count: Number of values to generate

        Returns:
            Series of random time values
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

            # Generate time values for this range
            for _ in range(range_count):
                time_value = self._generate_random_time_in_range(range_item)
                all_values.append(time_value)

        # Return as strings per tests expectations, preserving deterministic order
        return pd.Series(all_values)

    def reset_state(self):
        """Reset the internal state to initial values"""

        self.logger.debug("Resetting DistributedTimeRangeStrategy state")

        self._initialize_state()

    # def get_current_state(self) -> dict:
    #     """Get current state information for debugging"""

    #     return {
    #         "strategy": "DistributedTimeRangeStrategy",
    #         "stateful": True,
    #         "column": self.col_name,
    #         "seed": self.params.get("seed", None),
    #     }

    # Use BaseStrategy.generate_data
