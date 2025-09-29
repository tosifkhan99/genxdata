"""
CSV file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

from typing import Any

from .generic_file_writer import GenericFileWriter


class CsvFileWriter(GenericFileWriter):
    """
    Writer for CSV file format.

    Handles writing DataFrames to CSV files with proper defaults
    and parameter validation.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for CSV format
        csv_config = {
            **config,
            "writer_kind": "csv",
            "pandas_method": "to_csv",
            "extensions": [".csv"],
            "default_params": {
                "index": False,  # Don't include DataFrame index by default
                "encoding": "utf-8",
            }
        }
        super().__init__(csv_config)
