"""
Base abstract class for file writers in GenXData.

Provides a unified interface for all file format writers.
"""

import os
from abc import abstractmethod
from typing import Any

import pandas as pd

from utils.logging import Logger

from .base_writer import BaseWriter


class BaseFileWriter(BaseWriter):
    """
    Abstract base class for all file format writers.

    Provides common functionality for path handling, validation,
    and a unified interface for writing DataFrames to files.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the file writer with configuration.

        Args:
            config: Dictionary containing writer-specific parameters
                   Must include output path via 'output_path' key
        """
        # Call parent constructor
        super().__init__(config)

        # For backward compatibility, support both 'config' and direct params
        self.params = (
            config if "output_path" in config else config.get("params", config)
        )
        self.logger = Logger.get_logger(self.__class__.__name__.lower())

        # Validate required parameters
        self.validate_params()

        # Extract and store the base output path (may contain placeholders)
        self.base_output_path = self._extract_output_path()
        self.output_path = self._normalize_path(self.base_output_path)
        self.last_written_path: str | None = None

        # Ensure output directory exists
        from utils.file_utils.file_operations import ensure_output_dir

        ensure_output_dir(self.output_path, self.logger)

    def validate_params(self) -> None:
        """
        Validate that required parameters are present.

        Raises:
            ValueError: If required parameters are missing
        """
        if not isinstance(self.params, dict):
            raise ValueError("Parameters must be a dictionary")

        # Check for output path using various possible keys
        path_keys = ["output_path", "path_or_buf", "path", "database", "excel_writer"]
        if not any(key in self.params for key in path_keys):
            raise ValueError(
                f"Missing output path parameter. Please use 'output_path' "
                f"(preferred) or one of: {path_keys[1:]}"
            )

    def _extract_output_path(self) -> str:
        """
        Extract output path from parameters using various possible keys.

        Note: 'output_path' is the preferred/standard parameter name.
        Other parameter names are supported for backward compatibility.

        Returns:
            str: The output path
        """
        # Parameter name preference order (most preferred first)
        param_preference = [
            "output_path",  # Preferred standard parameter
            "path_or_buf",  # Pandas standard for some writers
            "path",  # Alternative path parameter
            "database",  # SQLite specific
            "excel_writer",  # Excel specific
        ]

        for key in param_preference:
            if key in self.params:
                # Log deprecation notice for non-preferred parameter names
                if key != "output_path":
                    self.logger.debug(
                        f"Parameter '{key}' is deprecated. Use 'output_path' instead."
                    )
                return self.params[key]

        raise ValueError(
            "No valid output path found in parameters. "
            "Please use 'output_path' parameter."
        )

    def _normalize_path(self, path: str) -> str:
        """
        Normalize the output path by ensuring proper file extension.

        Args:
            path: Original file path

        Returns:
            str: Normalized path with proper extension
        """
        expected_extensions = self.get_expected_extensions()

        # Check if path already has a valid extension
        current_ext = os.path.splitext(path)[1].lower()
        if current_ext in expected_extensions:
            return path

        # Add the default extension
        default_ext = expected_extensions[0]
        return os.path.splitext(path)[0] + default_ext

    def _resolve_output_path(self, metadata: dict[str, Any] = None) -> str:
        """
        Resolve the output path with metadata substitution.

        Args:
            metadata: Optional metadata for path substitution

        Returns:
            str: Resolved output path
        """
        path = self.base_output_path

        if metadata:
            # Handle batch_index substitution
            if "batch_index" in metadata:
                path = path.replace("{batch_index}", str(metadata["batch_index"]))

            # Handle other common placeholders
            if "timestamp" in metadata:
                path = path.replace("{timestamp}", str(metadata["timestamp"]))

        return self._normalize_path(path)

    def _get_writer_params(self) -> dict[str, Any]:
        """
        Get parameters for the pandas writer method, excluding path-related keys.

        Returns:
            dict: Filtered parameters for the writer method
        """
        excluded_keys = {
            "output_path",
            "path_or_buf",
            "path",
            "database",
            "excel_writer",
        }
        return {k: v for k, v in self.params.items() if k not in excluded_keys}

    @abstractmethod
    def get_expected_extensions(self) -> list[str]:
        """
        Get list of valid file extensions for this writer.

        Returns:
            list[str]: List of valid extensions (including the dot)
        """
        pass

    @abstractmethod
    def get_default_params(self) -> dict[str, Any]:
        """
        Get default parameters for this writer type.

        Returns:
            dict: Default parameters
        """
        pass

    @abstractmethod
    def write(
        self, df: pd.DataFrame, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Write DataFrame to file.

        Args:
            df: DataFrame to write
            metadata: Optional metadata (batch info, etc.)

        Returns:
            dict: Result information including status and file path
        """
        pass

    def finalize(self) -> dict[str, Any]:
        """
        Finalize the file writing process.

        For file writers, this typically just returns file information.
        Subclasses can override for specific cleanup needs.

        Returns:
            dict: Finalization results and file information
        """
        return {
            "status": "finalized",
            "writer_type": "file",
            "file_info": self.get_file_info(),
        }

    def get_file_info(self) -> dict[str, Any]:
        """
        Get information about the output file.

        Returns:
            dict: File information including path, size, etc.
        """
        path = self.last_written_path or self.output_path
        info = {
            "output_path": path,
            "writer_type": getattr(
                self,
                "writer_kind",
                self.__class__.__name__.replace("Writer", "").lower(),
            ),
            "exists": os.path.exists(path),
        }

        if info["exists"]:
            stat = os.stat(path)
            info.update({"size_bytes": stat.st_size, "modified_time": stat.st_mtime})

        return info
