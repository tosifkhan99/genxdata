"""
Delete strategy for removing values from a column.

This strategy has been refactored to use the new mixin pattern, reducing
boilerplate code by ~25 lines while maintaining the same functionality.
"""

import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import StatefulMixin, ValidationMixin


class DeleteStrategy(BaseStrategy, StatefulMixin, ValidationMixin):
    """
    Strategy for deleting/nullifying values in a column.
    Implements stateful interface for consistency.

    Uses mixins for:
    - StatefulMixin: Standardized state management and reporting
    - ValidationMixin: Common parameter validation patterns
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(mode=mode, logger=logger, **kwargs)

        # Initialize state
        self._initialize_state()  # From StatefulMixin

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        super()._initialize_state()  # Call StatefulMixin's _initialize_state first

        # Store mask from top-level field for efficient access
        self._mask = getattr(self, "mask", None)

        self.logger.debug(f"DeleteStrategy initialized with mask='{self._mask}'")

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of None values maintaining internal state.
        For delete strategy, this is stateless but implements the interface.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of None values
        """
        self.logger.debug(f"Generating chunk of {count} None values for deletion")

        # Return None values for the masked rows
        return pd.Series([None] * count, dtype=object)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting DeleteStrategy state")
        self._initialize_state()

    # def get_current_state(self) -> dict:
    #     """Get current state information for debugging"""
    #     return {
    #         "strategy": "DeleteStrategy",
    #         "stateful": True,
    #         "column": self.col_name,
    #         "mask": self._mask,
    #     }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate None values by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of None values
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For non-batch mode, reset state to ensure consistent behavior
        self.reset_state()
        # Generate the chunk
        result = self.generate_chunk(count)

        self.logger.debug(f"Generated {len(result)} None values for deletion")

        return result
