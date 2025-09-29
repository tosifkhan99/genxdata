"""
Factory for creating file writers in GenXData.

This factory normalizes writer type strings (case-insensitive, optional
"_WRITER" suffix) and instantiates concrete `BaseFileWriter` subclasses.

Notes:
- Supported types: csv, json, excel/xlsx/xls, parquet, sqlite/db, html/htm, feather
- If no parameters are provided, an `output_path` default is injected
  (e.g., "output.csv") so that writers can proceed.
"""

from typing import Any

from utils.logging import Logger

from .base_file_writer import BaseFileWriter
from .csv_file_writer import CsvFileWriter
from .excel_file_writer import ExcelFileWriter
from .feather_file_writer import FeatherFileWriter
from .html_file_writer import HtmlFileWriter
from .json_file_writer import JsonFileWriter
from .parquet_file_writer import ParquetFileWriter
from .sqlite_file_writer import SqliteFileWriter


class FileWriterFactory:
    """
    Factory class for creating file writers.

    Maps writer type strings to their corresponding writer classes and
    provides helpers for type normalization, support checks, and batch
    creation.
    """

    # Mapping of writer type strings to writer classes
    _WRITER_REGISTRY: dict[str, type[BaseFileWriter]] = {
        "csv": CsvFileWriter,
        "json": JsonFileWriter,
        "excel": ExcelFileWriter,
        "xlsx": ExcelFileWriter,  # Alias for Excel
        "xls": ExcelFileWriter,  # Alias for Excel
        "parquet": ParquetFileWriter,
        "sqlite": SqliteFileWriter,
        "db": SqliteFileWriter,  # Alias for SQLite
        "html": HtmlFileWriter,
        "htm": HtmlFileWriter,  # Alias for HTML
        "feather": FeatherFileWriter,
    }

    def __init__(self):
        """Initialize the factory."""
        self.logger = Logger.get_logger("file_writer_factory")

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """
        Get list of supported writer types.

        Returns:
            list[str]: List of supported writer type strings
        """
        return list(cls._WRITER_REGISTRY.keys())

    @classmethod
    def is_supported(cls, writer_type: str) -> bool:
        """
        Check if a writer type is supported.

        Args:
            writer_type: Writer type string to check

        Returns:
            bool: True if the writer type is supported
        """
        return cls._normalize_type(writer_type) in cls._WRITER_REGISTRY

    @staticmethod
    def _normalize_type(writer_type: str) -> str:
        """
        Normalize writer type string.

        Args:
            writer_type: Original writer type string

        Returns:
            str: Normalized writer type
        """
        if not writer_type:
            raise ValueError("Writer type cannot be empty")

        # Convert to lowercase and remove common suffixes
        normalized = writer_type.lower().strip()

        # Remove _WRITER suffix if present (for backward compatibility)
        if normalized.endswith("_writer"):
            normalized = normalized[:-7]

        return normalized

    def create_writer(self, writer_type: str, params: dict[str, Any]) -> BaseFileWriter:
        """
        Create a file writer instance.

        Args:
            writer_type: Type of writer to create (e.g., 'csv', 'json', 'excel')
            params: Parameters for the writer

        Returns:
            BaseFileWriter: Writer instance

        Raises:
            ValueError: If writer type is not supported
            Exception: If writer creation fails
        """
        normalized_type = self._normalize_type(writer_type)

        if normalized_type not in self._WRITER_REGISTRY:
            supported_types = ", ".join(self.get_supported_types())
            raise ValueError(
                f"Unsupported writer type: '{writer_type}'. "
                f"Supported types: {supported_types}"
            )

        writer_class = self._WRITER_REGISTRY[normalized_type]

        try:
            self.logger.debug(f"Creating {writer_class.__name__} with params: {params}")

            if not params:
                params["output_path"] = "output.csv"

            writer = writer_class(params)
            self.logger.info(f"Successfully created {writer_class.__name__}")
            return writer

        except Exception as e:
            self.logger.error(f"Failed to create {writer_class.__name__}: {e}")
            raise Exception(
                f"Failed to create writer for type '{writer_type}': {e}"
            ) from e

    @classmethod
    def register_writer(
        cls, writer_type: str, writer_class: type[BaseFileWriter]
    ) -> None:
        """
        Register a new writer type.

        Args:
            writer_type: Writer type string
            writer_class: Writer class that extends BaseFileWriter

        Raises:
            ValueError: If writer_class doesn't extend BaseFileWriter
        """
        if not issubclass(writer_class, BaseFileWriter):
            raise ValueError(
                f"Writer class must extend BaseFileWriter, got {writer_class}"
            )

        normalized_type = cls._normalize_type(writer_type)
        cls._WRITER_REGISTRY[normalized_type] = writer_class

    def create_multiple_writers(
        self, writer_configs: list[dict[str, Any]]
    ) -> list[BaseFileWriter]:
        """
        Create multiple writer instances from a list of configurations.

        Args:
            writer_configs: List of writer configurations, each containing 'type' and 'params'

        Returns:
            list[BaseFileWriter]: List of writer instances

        Raises:
            ValueError: If any configuration is invalid
        """
        writers = []

        for i, config in enumerate(writer_configs):
            if not isinstance(config, dict):
                raise ValueError(f"Writer config {i} must be a dictionary")

            if "type" not in config:
                raise ValueError(f"Writer config {i} missing 'type' field")

            writer_type = config["type"]
            params = config.get("params", {})

            try:
                writer = self.create_writer(writer_type, params)
                writers.append(writer)
            except Exception as e:
                self.logger.error(
                    f"Failed to create writer {i} (type: {writer_type}): {e}"
                )
                raise

        self.logger.info(f"Successfully created {len(writers)} writers")
        return writers
