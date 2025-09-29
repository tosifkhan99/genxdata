"""
Pattern strategy for generating random strings matching a regex or pattern.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~30 lines while maintaining the same functionality.
"""

import random

import numpy as np
import pandas as pd
import rstr

from core.base_strategy import BaseStrategy
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin


class PatternStrategy(BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin):
    """
    Strategy for generating random strings matching a regex or pattern.
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

        # Store pattern for efficient access
        self._pattern = self.params["regex"]
        self._unique_values = set() if self.unique else None

        self.logger.debug(
            f"PatternStrategy initialized with pattern='{self._pattern}', "
            f"unique={self.unique}, seed={self._seed}"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of random strings matching the pattern maintaining internal state.
        This method is stateful and maintains consistent random sequence and uniqueness.

        Args:
            count: Number of strings to generate

        Returns:
            pd.Series: Generated strings
        """
        self.logger.debug(
            f"Generating chunk of {count} strings matching pattern '{self._pattern}'"
        )

        max_attempts = count * 3  # tries 3 times more than the count
        attempts = 0

        if self.unique and self._unique_values is not None:
            result = []
            while len(result) < count and attempts < max_attempts:
                attempts += 1
                value = rstr.xeger(self._pattern)

                # Check if it's unique
                if value not in self._unique_values:
                    self._unique_values.add(value)
                    result.append(value)

            # If we couldn't generate enough unique values, pad with existing ones
            if len(result) < count:
                remaining = count - len(result)
                existing_values = list(self._unique_values)
                if existing_values:
                    padding = [
                        np.random.choice(existing_values) for _ in range(remaining)
                    ]
                    result.extend(padding)
                else:
                    # Fallback: generate non-unique values
                    padding = [rstr.xeger(self._pattern) for _ in range(remaining)]
                    result.extend(padding)
        else:
            result = [rstr.xeger(self._pattern) for _ in range(count)]

        return pd.Series(result, dtype=str)

    def reset_state(self):
        """Reset the internal state to initial values"""
        super().reset_state()  # Call StatefulMixin's reset_state
        # Re-initialize random state with original seed
        if self._seed is not None:
            random.seed(self._seed)
            np.random.seed(self._seed)
        # Re-derive any cached fields from current params for pooled reuse
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        state = super().get_current_state()  # Get base state from StatefulMixin
        state.update(
            {
                "pattern": self._pattern,
                "unique": self.unique,
                "unique_count": len(self._unique_values) if self._unique_values else 0,
            }
        )
        return state

    # Use BaseStrategy.generate_data
