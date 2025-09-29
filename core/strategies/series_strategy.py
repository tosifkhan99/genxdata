"""
Series strategy for generating sequential numeric values.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~30 lines while maintaining the same functionality.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import SeedMixin, StatefulMixin, ValidationMixin
from core.strategy_config import SeriesConfig


class SeriesStrategy(BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin):
    """
    Strategy for generating sequential numeric values.
    Supports both traditional batch generation and stateful chunked generation.

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

        # Determine if we're working with floats or integers
        start_value = self.params["start"]
        step_value = self.params.get("step", 1 if isinstance(start_value, int) else 0.1)

        if isinstance(start_value, float) or isinstance(step_value, float):
            # Use Decimal for floating point precision
            from decimal import Decimal, getcontext

            getcontext().prec = 10  # Increased precision

            self._current_value = Decimal(str(start_value))
            self._step = Decimal(str(step_value))
            self._is_float = True
        else:
            self._current_value = int(start_value)
            self._step = int(step_value)
            self._is_float = False

        # If we're in streaming/batch mode and have prior state, continue from it
        if hasattr(self, "mode") and self.mode == "STREAM&BATCH":
            prev_state = (self.strategy_state or {}).get(self._state_key)
            if prev_state and "last_value" in prev_state:
                last_value = prev_state["last_value"]
                if self._is_float:
                    from decimal import Decimal

                    self._current_value = Decimal(str(last_value)) + self._step
                else:
                    self._current_value = int(last_value) + int(self._step)

        self.logger.debug(
            f"SeriesStrategy initialized with start={self._current_value}, "
            f"step={self._step}, is_float={self._is_float}"
        )

    def _validate_params(self):
        """Delegate validation to SeriesConfig."""
        self._validate_required_params(["start"])  # ensure presence
        SeriesConfig(
            start=self.params["start"], step=self.params.get("step", 1)
        ).validate()

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of sequential values maintaining internal state.
        This method is stateful and continues from where the last chunk ended.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values starting from current state
        """
        self.logger.debug(
            f"Generating chunk of {count} values starting from {self._current_value}"
        )

        if self._is_float:
            # Generate float values using Decimal for precision
            values = []
            current = self._current_value
            for _ in range(count):
                values.append(float(current))
                current += self._step
            self._current_value = current

            return pd.Series(values, dtype=float)
        else:
            # Generate integer values
            start = self._current_value
            end = start + (count * self._step)
            values = np.arange(start, end, self._step, dtype=int)

            # Update current value for next chunk
            self._current_value = end

            return pd.Series(values, dtype=int)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting SeriesStrategy state")
        self._initialize_state()

    # Use BaseStrategy.generate_data
