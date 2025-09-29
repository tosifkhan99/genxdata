"""
SQLite file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

import sqlite3
from typing import Any

import pandas as pd

from .generic_file_writer import GenericFileWriter


def _sqlite_custom_write_func(
    df: pd.DataFrame, 
    output_path: str, 
    pandas_params: dict[str, Any], 
    custom_params: dict[str, Any], 
    metadata: dict[str, Any] = None
) -> dict[str, Any]:
    """Custom write function for SQLite format."""
    conn = None
    try:
        # Extract SQLite-specific parameters
        table_name = custom_params.get("table", "data")
        if_exists = custom_params.get("if_exists", "replace")
        index = custom_params.get("index", False)

        # Create SQLite connection
        conn = sqlite3.connect(output_path)

        # Write DataFrame to SQLite
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists=if_exists,
            index=index,
            **pandas_params,  # Any remaining parameters
        )

        return {
            "table_name": table_name,
        }

    finally:
        # Always close the connection if it was opened
        if conn:
            conn.close()


def _sqlite_params_extractor(writer_params: dict[str, Any]) -> dict[str, Any]:
    """Extract custom SQLite parameters from writer parameters."""
    custom_params = {}
    
    # SQLite-specific parameters
    sqlite_keys = ["table", "if_exists", "index"]
    for key in sqlite_keys:
        if key in writer_params:
            custom_params[key] = writer_params.pop(key)
    
    return custom_params


class SqliteFileWriter(GenericFileWriter):
    """
    Writer for SQLite database format.

    Handles writing DataFrames to SQLite database files with proper defaults
    and parameter validation.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for SQLite format
        sqlite_config = {
            **config,
            "writer_kind": "sqlite",
            "extensions": [".db", ".sqlite", ".sqlite3"],
            "default_params": {
                "table": "data",  # Default table name
                "if_exists": "replace",  # Replace table if it exists
                "index": False,  # Don't include DataFrame index by default
            },
            "custom_write_func": _sqlite_custom_write_func,
            "custom_params_extractor": _sqlite_params_extractor,
        }
        super().__init__(sqlite_config)
