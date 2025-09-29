"""
Generic file writer implementation for GenXData.

This module provides a generic file writer that reduces duplication across
different file format writers by handling common patterns while allowing
format-specific customization.
"""

import os
from typing import Any, Callable

import pandas as pd

from .base_file_writer import BaseFileWriter


class GenericFileWriter(BaseFileWriter):
    """
    Generic file writer that handles common patterns for pandas DataFrame output.
    
    This writer reduces duplication by providing a common implementation
    that can be configured for different file formats through the pandas
    to_* methods.
    
    Usage:
        # For simple formats that map directly to pandas methods
        writer = GenericFileWriter({
            "output_path": "output.csv",
            "writer_kind": "csv",
            "pandas_method": "to_csv",
            "extensions": [".csv"],
            "default_params": {"index": False, "encoding": "utf-8"}
        })
        
        # For formats requiring custom handling
        writer = GenericFileWriter({
            "output_path": "output.html", 
            "writer_kind": "html",
            "custom_write_func": custom_html_writer,
            "extensions": [".html", ".htm"]
        })
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the generic file writer.
        
        Args:
            config: Configuration dictionary containing:
                - output_path: Output file path
                - writer_kind: Type identifier for the writer
                - pandas_method: Name of pandas method to use (e.g., 'to_csv')
                - extensions: List of valid file extensions
                - default_params: Default parameters for the pandas method
                - custom_write_func: Optional custom write function
                - custom_params_extractor: Optional function to extract custom params
        """
        # Extract configuration first
        self.writer_kind = config.get("writer_kind", "generic")
        self.pandas_method = config.get("pandas_method")
        self.extensions = config.get("extensions", [])
        self.default_params = config.get("default_params", {})
        self.custom_write_func = config.get("custom_write_func")
        self.custom_params_extractor = config.get("custom_params_extractor")
        
        # Validate configuration
        if not self.custom_write_func and not self.pandas_method:
            raise ValueError("Either 'pandas_method' or 'custom_write_func' must be specified")
        
        if not self.extensions:
            raise ValueError("'extensions' must be specified")
        
        # Now call parent constructor
        super().__init__(config)

    def get_expected_extensions(self) -> list[str]:
        """Get valid file extensions for this writer."""
        return self.extensions

    def get_default_params(self) -> dict[str, Any]:
        """Get default parameters for this writer."""
        return self.default_params.copy()

    def write(self, df: pd.DataFrame, metadata: dict[str, Any] = None) -> dict[str, Any]:
        """
        Write DataFrame to file using the configured method.
        
        Args:
            df: DataFrame to write
            metadata: Optional metadata (batch info, etc.)
            
        Returns:
            dict: Result information
        """
        try:
            # Get writer parameters, excluding path-related keys
            writer_params = self._get_writer_params()
            
            # Apply defaults for missing parameters
            defaults = self.get_default_params()
            for key, value in defaults.items():
                if key not in writer_params:
                    writer_params[key] = value
            
            # Resolve output path with metadata substitution
            resolved_path = self._resolve_output_path(metadata)
            
            # Ensure the directory exists for the resolved path
            output_dir = os.path.dirname(resolved_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Use custom write function if provided
            if self.custom_write_func:
                result = self._write_with_custom_func(df, resolved_path, writer_params, metadata)
            else:
                result = self._write_with_pandas_method(df, resolved_path, writer_params, metadata)
            
            self.last_written_path = resolved_path
            return result
            
        except Exception as e:
            self.logger.error(f"Error writing DataFrame to {self.writer_kind}: {e}")
            return {"status": "error", "error": str(e), "output_path": self.output_path}

    def _write_with_pandas_method(
        self, df: pd.DataFrame, resolved_path: str, writer_params: dict[str, Any], metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Write using pandas method."""
        # Get the pandas method
        pandas_write_method = getattr(df, self.pandas_method)
        
        # Filter out non-pandas parameters
        meta_keys = {
            "writer_kind",
            "extensions",
            "custom_write_func",
            "custom_params_extractor",
            "pandas_method",
            "default_params",
        }
        pandas_params = {k: v for k, v in writer_params.items() if k not in meta_keys}
        
        # Add path parameter (different methods use different parameter names)
        if self.pandas_method in ["to_csv", "to_json"]:
            pandas_params["path_or_buf"] = resolved_path
        elif self.pandas_method == "to_excel":
            pandas_params["excel_writer"] = resolved_path
        elif self.pandas_method in ["to_parquet", "to_feather"]:
            pandas_params["path"] = resolved_path
        else:
            pandas_params["path"] = resolved_path
        
        # Write the file
        self.logger.debug(f"Writing DataFrame to {self.writer_kind}: {resolved_path}")
        
        pandas_write_method(**pandas_params)
        
        self.logger.info(f"Successfully wrote {len(df)} rows to {self.writer_kind}: {resolved_path}")
        
        return {
            "status": "success",
            "output_path": resolved_path,
            "rows_written": len(df),
            "file_info": self.get_file_info(),
        }

    def _write_with_custom_func(
        self, df: pd.DataFrame, resolved_path: str, writer_params: dict[str, Any], metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Write using custom function."""
        self.logger.debug(f"Writing DataFrame to {self.writer_kind}: {resolved_path}")
        
        # Extract custom parameters if extractor is provided
        if self.custom_params_extractor:
            custom_params = self.custom_params_extractor(writer_params)
        else:
            custom_params = {}

        # Build pandas-compatible params by excluding meta and custom keys
        meta_keys = {
            "writer_kind",
            "extensions",
            "custom_write_func",
            "custom_params_extractor",
            "pandas_method",
            "default_params",
        }
        pandas_params = {k: v for k, v in writer_params.items() if k not in meta_keys and k not in custom_params}
        
        # Call custom write function
        result = self.custom_write_func(df, resolved_path, pandas_params, custom_params, metadata)
        
        self.logger.info(f"Successfully wrote {len(df)} rows to {self.writer_kind}: {resolved_path}")
        
        return {
            "status": "success",
            "output_path": resolved_path,
            "rows_written": len(df),
            "file_info": self.get_file_info(),
            **result  # Include any additional result data from custom function
        }