"""
JSON file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

from typing import Any

from .generic_file_writer import GenericFileWriter


class JsonFileWriter(GenericFileWriter):
    """
    Writer for JSON file format.

    Handles writing DataFrames to JSON files with proper defaults
    and parameter validation.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for JSON format
        json_config = {
            **config,
            "writer_kind": "json",
            "pandas_method": "to_json",
            "extensions": [".json"],
            "default_params": {
                "orient": "records",  # Write as array of objects
                "date_format": "iso",  # ISO format for dates
                "indent": 2,  # Pretty print JSON
            }
        }
        super().__init__(json_config)
