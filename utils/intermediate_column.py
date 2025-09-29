"""
Utility for managing intermediate columns in data generation.

Intermediate columns are used for internal calculations and transformations
but are not included in the final output.
"""

from __future__ import annotations

import os
from typing import Iterable, Set

import pandas as pd

import configs.GENERATOR_SETTINGS as SETTINGS

def mark_as_intermediate(df, column_name):
    """
    Mark a column as intermediate (to be excluded from final output)

    Args:
        df (pandas.DataFrame): The dataframe containing the column
        column_name (str): The name of the column to mark as intermediate

    Returns:
        pandas.DataFrame: The same dataframe with metadata updated
    """
    meta = df.attrs.setdefault("intermediate_columns", set())
    # Ensure a set-like
    if not isinstance(meta, set):
        meta = set(meta)
    meta.add(column_name)
    df.attrs["intermediate_columns"] = meta
    return df


def get_intermediate_columns(df):
    """
    Get the list of intermediate columns in a dataframe

    Args:
        df (pandas.DataFrame): The dataframe to check

    Returns:
        set: Set of column names marked as intermediate
    """
    meta = df.attrs.get("intermediate_columns", set())
    return set(meta) if not isinstance(meta, set) else meta


def filter_intermediate_columns(df):
    """
    Remove intermediate columns from the dataframe

    Args:
        df (pandas.DataFrame): The dataframe to filter

    Returns:
        pandas.DataFrame: A new dataframe with intermediate columns removed
    """
    intermediate_cols = get_intermediate_columns(df)
    if not intermediate_cols:
        return df

    # Filter out intermediate columns
    return df.drop(columns=list(intermediate_cols))


def compute_dependency_columns(config: dict) -> Set[str]:
    """
    Determine columns that are referenced by other strategies via params or masks.

    Heuristics:
    - Mask presence on a config means any columns referenced in the mask are dependencies.
    - For known strategies that reference other columns (e.g., CONCAT_STRATEGY, MAPPING_STRATEGY),
      include their source columns (e.g., lhs_col, rhs_col, map_from).
    """
    dependent: dict[str, str] = {}

    def _extract_from_mask(mask_expr: str) -> Iterable[str]:
        # Basic heuristic: split on non-word chars and intersect with declared column_name list
        if not mask_expr:
            return []
        import re

        tokens = re.split(r"[^A-Za-z0-9_]+", mask_expr)
        columns = set(config.get("column_name", []))
        return [t for t in tokens if t and t in columns]

    for cfg in config.get("configs", []):
        mask = cfg.get("mask")
        if mask:
            for col in _extract_from_mask(mask):
                names = cfg.get("column_names") or []
                dependent[col] = names

        strat = (cfg.get("strategy", {}) or {}).get("name", "")
        params = (cfg.get("strategy", {}) or {}).get("params", {}) or {}

        # Known cross-column references
        if strat == "CONCAT_STRATEGY":
            for key in ("lhs_col", "rhs_col"):
                val = params.get(key)
                if isinstance(val, str):
                    names = cfg.get("column_names") or []
                    dependent[val] = names
        elif strat == "MAPPING_STRATEGY":
            val = params.get("map_from")
            if isinstance(val, str):
                names = cfg.get("column_names") or []
                dependent[val] = names

    return set(dependent.keys())


def should_offload_normal_mode(num_rows: int) -> bool:
    return num_rows >= getattr(SETTINGS, "NORMAL_MODE_OFFLOAD_THRESHOLD_ROWS", 1_000_000)


def ensure_intermediate_dir() -> str:
    out_dir = getattr(SETTINGS, "INTERMEDIATE_STORAGE_DIR", "./output/_intermediate")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def offload_column_to_parquet(series: pd.Series, column_name: str, partition: int | None = None) -> str:
    directory = ensure_intermediate_dir()
    fname = f"{column_name}.parquet" if partition is None else f"{column_name}_{partition}.parquet"
    path = os.path.join(directory, fname)

    df = pd.DataFrame({column_name: series})
    df.to_parquet(path, index=False)
    return path


def load_offloaded_column(column_name: str) -> pd.Series:
    directory = ensure_intermediate_dir()
    path = os.path.join(directory, f"{column_name}.parquet")
    if not os.path.exists(path):
        # Try to glob partitioned files and concatenate in index order
        import glob

        parts = sorted(glob.glob(os.path.join(directory, f"{column_name}_*.parquet")))
        if not parts:
            raise FileNotFoundError(f"Offloaded column not found for '{column_name}'")
        frames = [pd.read_parquet(p) for p in parts]
        merged = pd.concat(frames, ignore_index=True)
        return merged[column_name]

    df = pd.read_parquet(path)
    return df[column_name]
