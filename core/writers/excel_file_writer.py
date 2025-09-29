"""
Excel file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

from typing import Any

from .generic_file_writer import GenericFileWriter


class ExcelFileWriter(GenericFileWriter):
    """
    Writer for Excel file format.

    Handles writing DataFrames to Excel files with proper defaults
    and parameter validation.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for Excel format
        excel_config = {
            **config,
            "writer_kind": "excel",
            "pandas_method": "to_excel",
            "extensions": [".xlsx", ".xls"],
            "default_params": {
                "index": False,  # Don't include DataFrame index by default
                "sheet_name": "Sheet1",  # Default sheet name
                "engine": "openpyxl",  # Default engine for xlsx files
            }
        }
        super().__init__(excel_config)
