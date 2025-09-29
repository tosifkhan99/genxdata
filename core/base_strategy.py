"""
Base strategy for all data generation strategies.
"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pandas as pd
from pandas.errors import IndexingError

from utils.logging import Logger


class BaseStrategy(ABC):
    """
    Base class for all data generation strategies.
    All strategies must implement the stateful generation pattern.
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        self.df = kwargs.get("df")
        self.col_name = kwargs.get("col_name")
        self.rows = kwargs.get("rows", 100)
        self.is_intermediate = kwargs.get("intermediate", False)
        self.params = kwargs.get("params", {})
        self.debug = kwargs.get("debug", False)
        self.unique = kwargs.get("unique", False)
        self.shuffle = kwargs.get("shuffle", False)
        # mask is a top-level field, not part of params
        self.mask = kwargs.get("mask")
        # Ensure strategy_state is always a dictionary for stateful ops
        self.strategy_state = kwargs.get("strategy_state") or {}
        self.mode = mode
        # Standardized state key
        self._state_key = f"{self.__class__.__name__}:{self.col_name}"
        # Initialize mixin-expected attributes
        self._seed = None

        # Create strategy-specific logger
        if logger is None:
            strategy_name = self.__class__.__name__.lower().replace("strategy", "")
            logger_name = f"strategies.{strategy_name}"
            self.logger = Logger.get_logger(logger_name)
        else:
            self.logger = logger

        # Log strategy initialization
        self.logger.debug(
            f"Initializing {self.__class__.__name__} for column '{self.col_name}'"
        )

        # Warn if uniqueness is requested in streaming/batch mode (currently disabled)
        if self.unique and self.is_streaming_and_batch():
            self.logger.warning(
                f"Unique=True requested for column '{self.col_name}' in {self.__class__.__name__} "
                f"but uniqueness is disabled in STREAM&BATCH mode. It will be ignored."
            )

        # Validation is handled by config classes at factory level

    # def _validate_params(self):
    #     """
    #     Validate the parameters required by this strategy.
    #     Raises InvalidConfigParamException if required parameters are missing or
    #     invalid.
    #     """
    #     return

    def generate_data(self, count: int) -> pd.Series:
        """
        Default data generation flow used by most strategies.
        Resets state in non-streaming mode, then delegates to generate_chunk().

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        if not self.is_streaming_and_batch():
            self.reset_state()

        result = self.generate_chunk(count)
        return result

    @abstractmethod
    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of data maintaining internal state.
        All strategies must implement this method for stateful generation.

        Args:
            count: Number of values to generate
        Returns:
            pd.Series: Generated values
        """
        pass

    @abstractmethod
    def reset_state(self):
        """
        Reset the internal state to initial values.
        All strategies must implement this method.
        """
        pass

    def get_current_state(self) -> dict:
        """
        Get current state information for debugging.

        Returns a safe default if no state was recorded yet.

        Returns:
            dict: Current state information
        """
        if self._state_key in self.strategy_state:
            return self.strategy_state[self._state_key]
        # Safe default state when not yet set
        return {
            "strategy": self.__class__.__name__,
            "stateful": True,
            "column": self.col_name,
            "seed": getattr(self, "_seed", None),
            "dtype": None,
            "step": None,
        }

    def sync_state(self, result: pd.Series) -> dict[str, Any]:
        """
        Sync the state of the strategy.
        This is used to update the state of the strategy with the result of the strategy.
        Strategies may override this method to customize state sync.

        Args:
            result: Result of the strategy

        Returns:
            dict: Updated state information
        """
        if self.is_streaming_and_batch():
            state = self.strategy_state.get(self._state_key, {})
            state.update(
                {
                    "last_value": result.iloc[-1]
                    if len(result) > 0
                    else state.get("last_value"),
                    "last_index": result.index[-1]
                    if len(result) > 0
                    else state.get("last_index"),
                    "dtype": str(result.dtype)
                    if len(result) > 0
                    else state.get("dtype"),
                }
            )

            # Track uniqueness context if requested (NORMAL mode only)
            if self.unique and not self.is_streaming_and_batch():
                prev = state.get("unique_values")
                if prev is None:
                    state["unique_values"] = pd.Series(result).dropna()
                else:
                    # Concatenate and drop duplicates to maintain a running set
                    state["unique_values"] = (
                        pd.concat([pd.Series(prev), pd.Series(result)])
                        .drop_duplicates()
                        .reset_index(drop=True)
                    )

            self.strategy_state[self._state_key] = state

        return self.strategy_state

    def is_streaming_and_batch(self) -> bool:
        """
        Check if this strategy supports streaming and batch generation.
        """
        return self.mode == "STREAM&BATCH"

    def is_stateful(self) -> bool:
        """
        Check if this strategy supports stateful generation.
        All strategies are now stateful by design.

        Returns:
            bool: Always True since all strategies implement stateful methods
        """
        return True

    def apply_to_dataframe(
        self, df: pd.DataFrame, column_name: str, mask: str | None = None
    ) -> pd.DataFrame:
        """
        Apply strategy to dataframe with optional mask filtering.

        Args:
            df: Target dataframe
            column_name: Column to populate
            mask: Optional pandas query string for filtering rows

        Returns:
            Updated dataframe
        """
        self.logger.debug(
            f"Applying {self.__class__.__name__} to column '{column_name}' "
            f"with {len(df)} rows"
        )

        # In-place mutation path to avoid full copies
        df_copy = df  # alias for clarity; we mutate original

        # Initialize column with NaN if it doesn't exist
        if column_name not in df_copy.columns:
            df_copy[column_name] = np.nan

        if mask and mask.strip():
            self.logger.debug(f"Applying mask to column '{column_name}': {mask}")
            try:
                filtered_df = df_copy.query(mask)
                if len(filtered_df) > 0:
                    self.logger.debug(
                        f"Mask filtered {len(filtered_df)} rows out of "
                        f"{len(df_copy)} total rows"
                    )
                    # Generate data only for filtered rows
                    values = self.generate_data(len(filtered_df))

                    # Enforce uniqueness only in NORMAL mode (not STREAM&BATCH)
                    if self.unique and not self.is_streaming_and_batch():
                        values = self._enforce_uniqueness(values)

                    # Sync state with the result
                    self.sync_state(values)

                    # Ensure column has compatible dtype before assignment
                    if (
                        df_copy[column_name].dtype == "float64"
                        and values.dtype == "object"
                    ):
                        df_copy[column_name] = df_copy[column_name].astype("object")

                    df_copy.loc[filtered_df.index, column_name] = values.values
                else:
                    self.logger.warning(
                        f"Mask '{mask}' matched no rows for column '{column_name}'"
                    )

            except IndexingError as e:
                self.logger.warning(
                    f"IndexError applying mask to column '{column_name}': {e}. "
                    f"Applying to all rows as fallback."
                )
                # Fallback: apply to all rows
                values = self.generate_data(len(df_copy))

                # Sync state with the result
                if self.unique and not self.is_streaming_and_batch():
                    values = self._enforce_uniqueness(values)
                self.sync_state(values)

                # Ensure column has compatible dtype before assignment
                if df_copy[column_name].dtype == "float64" and values.dtype == "object":
                    df_copy[column_name] = df_copy[column_name].astype("object")

                df_copy[column_name] = values.values
            except Exception as e:
                self.logger.error(f"Error applying mask to column '{column_name}': {e}")
                raise e
        else:
            # No mask: apply to all rows
            self.logger.debug(f"No mask specified, applying to all {len(df_copy)} rows")
            values = self.generate_data(len(df_copy))

            # Sync state with the result
            if self.unique and not self.is_streaming_and_batch():
                values = self._enforce_uniqueness(values)
            self.sync_state(values)

            # Ensure column has compatible dtype before assignment
            if df_copy[column_name].dtype == "float64" and values.dtype == "object":
                df_copy[column_name] = df_copy[column_name].astype("object")

            df_copy[column_name] = values.values

        self.logger.debug(
            f"Successfully applied {self.__class__.__name__} to column '{column_name}'"
        )
        return df_copy

    def _enforce_uniqueness(
        self, values: pd.Series, max_attempts: int = 10
    ) -> pd.Series:
        """
        Ensure the produced values are unique across chunks when unique=True.

        Uses the recorded unique_values in strategy_state as the running set.

        If duplicates are found against the running set or within the new chunk,
        attempts to sample replacements up to max_attempts times. If still not
        enough unique values can be produced, raises a ValueError.
        """
        # Build current seen set from state and this batch
        state = (
            self.strategy_state.get(self._state_key, {})
            if isinstance(self.strategy_state, dict)
            else {}
        )
        prev_series = state.get("unique_values")
        seen: set[Any] = (
            set(pd.Series(prev_series).dropna().tolist())
            if prev_series is not None
            else set()
        )

        unique_list: list[Any] = []
        local_seen: set[Any] = set()

        # First pass: accept non-duplicates
        for v in values.tolist():
            if v not in seen and v not in local_seen:
                unique_list.append(v)
                local_seen.add(v)

        needed = len(values) - len(unique_list)
        attempts = 0

        # Try to fill remaining with additional samples
        while needed > 0 and attempts < max_attempts:
            attempts += 1
            candidates = self._sample_more(needed * 2)
            for v in candidates.tolist():
                if v not in seen and v not in local_seen:
                    unique_list.append(v)
                    local_seen.add(v)
                    if len(unique_list) == len(values):
                        break
            needed = len(values) - len(unique_list)

        if needed > 0:
            raise ValueError(
                f"Unable to generate {needed} additional unique values for column '{self.col_name}'. "
                f"Consider disabling unique or expanding the domain."
            )

        return pd.Series(unique_list)[: len(values)]

    def _sample_more(self, count: int) -> pd.Series:
        """
        Sample more candidate values using the strategy's stateful generator.
        Default behavior uses generate_chunk which advances state appropriately.
        Strategies can override for more efficient sampling.
        """
        return self.generate_chunk(count)

    def validate_mask(self, df: pd.DataFrame, mask: str) -> tuple[bool, str]:
        """
        Validate if a mask can be executed against the dataframe.

        Args:
            df: Dataframe to test against
            mask: Mask expression to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not mask or not mask.strip():
            return True, ""

        try:
            # Test the query on a small sample
            test_df = df.head(1) if len(df) > 0 else df
            test_df.query(mask)
            self.logger.debug(f"Mask validation successful: {mask}")
            return True, ""
        except Exception as e:
            self.logger.debug(f"Mask validation failed: {mask} - {str(e)}")
            return False, str(e)

    def preview_mask_results(self, df: pd.DataFrame, mask: str) -> dict:
        """
        Preview how many rows would be affected by a mask.

        Args:
            df: Dataframe to test against
            mask: Mask expression

        Returns:
            Dictionary with preview information
        """
        if not mask or not mask.strip():
            return {
                "total_rows": len(df),
                "affected_rows": len(df),
                "percentage": 100.0,
                "mask_valid": True,
            }

        try:
            filtered_df = df.query(mask)
            affected_rows = len(filtered_df)
            total_rows = len(df)
            percentage = (affected_rows / total_rows * 100) if total_rows > 0 else 0

            self.logger.debug(
                f"Mask preview: {affected_rows}/{total_rows} rows "
                f"({percentage:.2f}%) would be affected"
            )

            return {
                "total_rows": total_rows,
                "affected_rows": affected_rows,
                "percentage": round(percentage, 2),
                "mask_valid": True,
                "sample_affected_rows": (
                    filtered_df.head(3).to_dict("records") if affected_rows > 0 else []
                ),
            }
        except Exception as e:
            self.logger.debug(f"Mask preview failed: {str(e)}")
            return {
                "total_rows": len(df),
                "affected_rows": 0,
                "percentage": 0.0,
                "mask_valid": False,
                "error": str(e),
            }
