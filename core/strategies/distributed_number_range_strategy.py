"""
Distributed number range strategy for generating numeric values from multiple
weighted ranges.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~40 lines while maintaining the same functionality.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.domain_mixins import NumericMixin
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin


class DistributedNumberRangeStrategy(
    BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin, NumericMixin
):
    """
    Strategy for generating random numbers from multiple weighted ranges.

    Uses mixins for:
    - SeedMixin: Automatic seed validation and random state initialization
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    - NumericMixin: Specialized numeric validation and utilities
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

        # Seed initialization is handled by SeedMixin
        self.logger.debug(
            f"DistributedNumberRangeStrategy initialized with seed={self._seed}"
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
        Generate random numbers from multiple weighted ranges.

        Args:
            count: Number of values to generate

        Returns:
            Series of random numbers
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

            lb = range_item.start
            ub = range_item.end

            # Handle integer vs float generation
            if isinstance(lb, int) and isinstance(ub, int):
                # Generate integers
                values = np.random.randint(lb, ub + 1, size=range_count).tolist()
            else:
                # Generate floats
                values = np.random.uniform(lb, ub, size=range_count).tolist()

            all_values.extend(values)

        # Shuffle the values to mix ranges
        np.random.shuffle(all_values)

        return pd.Series(all_values, dtype=float)

    def reset_state(self):
        """Reset the internal state to initial values"""

        self.logger.debug("Resetting DistributedNumberRangeStrategy state")

        self._initialize_state()

    # def get_current_state(self) -> dict:
    #     """Get current state information for debugging"""

    #     return {
    #         "strategy": "DistributedNumberRangeStrategy",
    #         "stateful": True,
    #         "column": self.col_name,
    #         "seed": self.params.get("seed", None),
    #     }

    # Use BaseStrategy.generate_data
