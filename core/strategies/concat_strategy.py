"""
Concat strategy for concatenating values from multiple columns.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~30 lines while maintaining the same functionality.
"""

import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import StatefulMixin, ValidationMixin


class ConcatStrategy(BaseStrategy, StatefulMixin, ValidationMixin):
    """
    Strategy for concatenating values from multiple columns.
    Implements stateful interface for consistency.

    Uses mixins for:
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(mode=mode, logger=logger, **kwargs)

        self._initialize_state()  # From StatefulMixin

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        super()._initialize_state()  # Call StatefulMixin's _initialize_state first

        # Store concatenation parameters for efficient access
        self._lhs_col = self.params["lhs_col"]
        self._rhs_col = self.params["rhs_col"]
        self._prefix = self.params.get("prefix", "")
        self._suffix = self.params.get("suffix", "")
        self._separator = self.params.get("separator", "")

        self.logger.debug(
            f"ConcatStrategy initialized: {self._lhs_col} + {self._rhs_col} "
            f"with prefix='{self._prefix}', suffix='{self._suffix}', separator='{self._separator}'"
        )

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of concatenated values maintaining internal state.
        For concat strategy, this works with existing data from multiple columns.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of concatenated values
        """
        self.logger.debug(f"Generating chunk of {count} concatenated values")

        if self.df is None:
            self.logger.warning("No dataframe available for concatenation")
            return pd.Series([f"{self._prefix}{self._separator}{self._suffix}"] * count)

        # Get data from both columns, limited to count
        lhs_data = self.df[self._lhs_col].head(count)
        rhs_data = self.df[self._rhs_col].head(count)

        # Convert to string for concatenation
        if lhs_data.dtype != "str":
            lhs_data_as_string = lhs_data.astype(str)
        else:
            lhs_data_as_string = lhs_data

        if rhs_data.dtype != "str":
            rhs_data_as_string = rhs_data.astype(str)
        else:
            rhs_data_as_string = rhs_data

        # Perform concatenation
        result = (
            self._prefix
            + lhs_data_as_string
            + self._separator
            + rhs_data_as_string
            + self._suffix
        )

        return result

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting ConcatStrategy state")
        self._initialize_state()

    # Use BaseStrategy.generate_data
