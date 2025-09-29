"""
Feather file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

from typing import Any

from .generic_file_writer import GenericFileWriter


class FeatherFileWriter(GenericFileWriter):
    """
    Writer for Feather file format.

    Feather is a fast, lightweight binary columnar format designed for
    high-performance data interoperability between multiple languages.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for Feather format
        feather_config = {
            **config,
            "writer_kind": "feather",
            "pandas_method": "to_feather",
            "extensions": [".feather"],
            "default_params": {
                "compression": "zstd"  # Default compression algorithm
            }
        }
        super().__init__(feather_config)
