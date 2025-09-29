"""
Replacement strategy for replacing specific values with other values.
"""

import pandas as pd

from core.base_strategy import BaseStrategy
from core.strategy_config import ReplacementConfig
from exceptions.param_exceptions import InvalidConfigParamException


class ReplacementStrategy(BaseStrategy):
    """
    Strategy for replacing specific values with other values.
    Implements stateful interface for consistency.
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(mode=mode, logger=logger, **kwargs)

        # Initialize state (simple for replacement strategy)
        self._initialize_state()

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        # Store replacement values for efficient access
        self._from_value = self.params["from_value"]
        self._to_value = self.params["to_value"]

        self.logger.debug(
            f"ReplacementStrategy initialized: {self._from_value} -> {self._to_value}"
        )

    def _validate_params(self):
        """Delegate validation to ReplacementConfig (no-op) while ensuring presence."""
        if "from_value" not in self.params or "to_value" not in self.params:
            raise InvalidConfigParamException(
                "Missing required parameter: from_value/to_value"
            )
        ReplacementConfig(
            from_value=self.params["from_value"], to_value=self.params["to_value"]
        ).validate()

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of replacement values maintaining internal state.
        For replacement strategy, this works with existing data.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series with replacements applied
        """
        self.logger.debug(f"Generating chunk of {count} replacement values")

        if self.df is not None and self.col_name in self.df.columns:
            # Work with existing data
            values = self.df[self.col_name].head(count)
            result = values.replace(self._from_value, self._to_value)
        else:
            # If no existing data, return the to_value repeated
            self.logger.warning("No existing data found, returning to_value repeated")
            result = pd.Series([self._to_value] * count)

        return result

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting ReplacementStrategy state")
        self._initialize_state()

    # def get_current_state(self) -> dict:
    #     """Get current state information for debugging"""
    #     return {
    #         "strategy": "ReplacementStrategy",
    #         "stateful": True,
    #         "column": self.col_name,
    #         "from_value": self._from_value,
    #         "to_value": self._to_value,
    #     }

    def generate_data(self, count: int) -> pd.Series:
        """
        Replace values by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series with replacements applied
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For non-batch mode, reset state to ensure consistent behavior
        self.reset_state()
        # Generate the chunk
        result = self.generate_chunk(count)

        self.logger.debug(f"Generated {len(result)} replacement values")

        return result
