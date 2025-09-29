"""
Factory for creating strategy instances based on strategy name.

Responsibilities:
- Map strategy names to classes via `strategy_mapping`
- Construct and validate corresponding `BaseConfig` objects
- Execute strategies while handling mask application and intermediate columns
"""

from typing import Any

import pandas as pd

from core.base_strategy import BaseStrategy
from core.strategy_mapping import get_config_class, get_strategy_class
from utils.intermediate_column import mark_as_intermediate


class StrategyFactory:
    """
    Factory class for creating strategy instances.

    This class is responsible for creating strategy instances with validated
    configuration parameters.
    """

    def __init__(self, logger):
        """Initialize the factory"""
        self.logger = logger
        # Pool of reusable strategy instances across chunks
        self._strategy_pool: dict[str, BaseStrategy] = {}

    def create_strategy(self, mode: str, strategy_name: str, **kwargs) -> BaseStrategy:
        """
        Create a strategy instance.

        Args:
            strategy_name: Name of the strategy to create
            **kwargs: Parameters for the strategy

        Returns:
            An instance of the strategy

        Raises:
            UnsupportedStrategyException: If the strategy cannot be created
        """

        try:
            # Get the strategy class from our mapping
            strategy_class = get_strategy_class(strategy_name)

            # Get the config class and create a config instance
            config_class = get_config_class(strategy_name)

            # Extract and validate params
            params = kwargs.get("params", {}) or {}
            config = config_class.from_dict(params)

            config.validate()

            # Update kwargs with validated config, preserving extra keys (e.g., seed)
            validated = config.to_dict()
            # todo: check if this is needed
            # Merge original params so non-config knobs like 'seed' survive
            for k, v in params.items():
                if k not in validated:
                    validated[k] = v
            kwargs["params"] = validated

            self.logger.debug(
                f"Strategy {strategy_name} created with params: {kwargs['params']}"
            )
            # Create and return strategy instance
            return strategy_class(mode=mode, logger=self.logger, **kwargs)

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error creating strategy {strategy_name}: {str(e)}")
            # Re-raise the original exception to preserve expected types in tests
            raise

    def get_or_create_strategy(
        self, mode: str, strategy_name: str, pool_key: str, **kwargs
    ) -> BaseStrategy:
        """
        Get a pooled strategy instance or create one if not exists.

        When reusing an instance, update mutable fields: df, rows, params,
        unique flag, and strategy_state reference.
        """
        if pool_key in self._strategy_pool:
            strategy = self._strategy_pool[pool_key]
            # Refresh per-chunk context
            strategy.df = kwargs.get("df", strategy.df)
            strategy.rows = kwargs.get("rows", strategy.rows)
            params = kwargs.get("params")
            if params is not None:
                strategy.params = params
            strategy.unique = kwargs.get("unique", strategy.unique)
            state = kwargs.get("strategy_state")
            if state is not None and state is not strategy.strategy_state:
                strategy.strategy_state = state
            # Update mask if provided (top-level)
            if "mask" in kwargs:
                strategy.mask = kwargs.get("mask")
            return strategy

        # Create and pool new instance
        strategy = self.create_strategy(mode, strategy_name, **kwargs)
        self._strategy_pool[pool_key] = strategy
        return strategy

    def execute_strategy(
        self, strategy: BaseStrategy, mode: str
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """
        Execute a strategy by generating data and applying it to the dataframe.

        Args:
            strategy: The strategy instance to execute

        Returns:
            The updated dataframe
        """

        # Get mask from strategy (top-level)
        mask = getattr(strategy, "mask", None)

        # Use the new mask evaluation from base strategy
        strategy.df = strategy.apply_to_dataframe(strategy.df, strategy.col_name, mask)

        # Mark as intermediate if needed
        if strategy.is_intermediate:
            strategy.df = mark_as_intermediate(strategy.df, strategy.col_name)

        # Ensure strategy state is propagated in streaming/batch scenarios
        return strategy.df, strategy.strategy_state
