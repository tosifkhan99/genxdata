"""
Parquet file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

from typing import Any

from .generic_file_writer import GenericFileWriter


class ParquetFileWriter(GenericFileWriter):
    """
    Writer for Parquet file format.

    Handles writing DataFrames to Parquet files with proper defaults
    and parameter validation.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for Parquet format
        parquet_config = {
            **config,
            "writer_kind": "parquet",
            "pandas_method": "to_parquet",
            "extensions": [".parquet"],
            "default_params": {
                "compression": "snappy",  # Default compression
                "index": False,  # Don't include DataFrame index by default
            }
        }
        super().__init__(parquet_config)
