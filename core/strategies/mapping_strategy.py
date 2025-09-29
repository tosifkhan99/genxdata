import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import StatefulMixin, ValidationMixin


class MappingStrategy(BaseStrategy, StatefulMixin, ValidationMixin):
    """
    Strategy that maps values from an existing source column to the target
    column using a provided mapping dictionary. Intended for use-cases like
    mapping `department_id` -> `department_name`.

    Expected params:
    - map_from: name of source column in df to read keys from
    - mapping: dict of key -> value (inline mode)
    - OR
    - source: path to CSV file containing mapping table (file mode)
    - source_column: target column name in the CSV to map to
    """

    def __init__(self, mode: str, logger=None, **kwargs):
        super().__init__(mode=mode, logger=logger, **kwargs)
        self._initialize_state()

    def _initialize_state(self):
        super()._initialize_state()
        self._map_from: str = self.params.get("map_from", "")

        raw_mapping = self.params.get("mapping", None)
        self._mapping_dict: dict = (
            dict(raw_mapping) if isinstance(raw_mapping, dict) else {}
        )

        self._source_path: str | None = self.params.get("source")
        self._source_column: str | None = self.params.get("source_column")
        self._source_map_from: str | None = self.params.get("source_map_from")

        self._mode: str = "MAPPING"

        if self._source_path and self._source_column:
            try:
                import os

                if not os.path.isfile(self._source_path):
                    self.logger.warning(
                        f"MappingStrategy: source file '{self._source_path}' does not exist"
                    )
                else:
                    src_df = self._read_mapping_source(self._source_path)
                    join_key = self._source_map_from or self._map_from
                    if (
                        join_key not in src_df.columns
                        or self._source_column not in src_df.columns
                    ):
                        self.logger.warning(
                            f"MappingStrategy: required columns not found in source file. "
                            f"Needed: '{join_key}', '{self._source_column}'. Found: {list(src_df.columns)}"
                        )
                    else:
                        # Build mapping from file
                        self._mapping_dict = (
                            src_df[[join_key, self._source_column]]
                            .dropna(subset=[join_key])
                            .set_index(join_key)[self._source_column]
                            .to_dict()
                        )
                        self._mode: str = "FILE"
            except Exception as e:
                self.logger.warning(
                    f"MappingStrategy: failed to load mapping from file: {e}"
                )

        self.logger.debug(
            f"MappingStrategy initialized: map_from='{self._map_from}', "
            f"target='{self.col_name}', mapping_size={len(self._mapping_dict)}, mode={self._mode}"
        )

    def _read_mapping_source(self, path: str) -> pd.DataFrame:
        """Read mapping source file based on extension (csv, json, parquet, xlsx/xls)."""
        lower = path.lower()
        if lower.endswith(".csv"):
            return pd.read_csv(path)
        if lower.endswith(".json"):
            return pd.read_json(path)
        if lower.endswith(".parquet"):
            return pd.read_parquet(path)
        if lower.endswith(".xlsx") or lower.endswith(".xls"):
            return pd.read_excel(path)
        # Fallback: attempt csv for unknown extension
        self.logger.debug(
            f"MappingStrategy: unknown extension for '{path}', attempting CSV reader"
        )
        return pd.read_csv(path)

    def generate_chunk(self, count: int) -> pd.Series:
        self.logger.debug(
            f"Generating mapping for {count} rows from '{self._map_from}' to '{self.col_name}'"
        )

        if (
            self.df is None
            or not self._map_from
            or self._map_from not in self.df.columns
        ):
            self.logger.warning(
                "MappingStrategy: df or source column missing; returning NaNs"
            )
            return pd.Series([None] * count, dtype=object)

        src = self.df[self._map_from].head(count).rename(None)
        mapped = src.map(self._mapping_dict, na_action="ignore")

        # Preserve existing target values; only overwrite where mapping produced a value
        if self.col_name in self.df.columns:
            existing = self.df[self.col_name].head(count)
            result = mapped.combine_first(existing)
        else:
            result = mapped

        return result.astype(object)

    def reset_state(self):
        # Ensure internal state (including mapping dict and map_from) reflects
        # the latest params when this pooled strategy instance is reused.
        super().reset_state()
        self._initialize_state()
