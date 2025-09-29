"""
Batch writer implementation for GenXData.

This is a compatibility wrapper that implements the BaseWriter interface
for use with batch processing scenarios.
"""

from typing import Any

import pandas as pd

from utils.logging import Logger

from .base_writer import BaseWriter


class BatchWriter(BaseWriter):
    """
    Writer implementation for batch processing scenarios.

    This is a wrapper that adapts a concrete writer implementation
    (e.g., file writer or StreamWriter) to the generic BaseWriter interface
    while adding batch-aware metadata and counters.
    """

    def __init__(
        self, config: dict[str, Any], writer_implementation: BaseWriter = None
    ):
        """
        Initialize the batch writer.

        Args:
            config: Batch writer configuration
            actual_writer: The actual writer to delegate to (FileWriter, StreamWriter, etc.)
        """
        super().__init__(config)
        self.logger = Logger.get_logger("batch_writer")
        self.writer_implementation = writer_implementation
        self.batches_written = 0
        self.total_rows_written = 0
        self.written_paths: list[str] = []

        # If no actual writer provided, default to CSV file writer
        if not self.writer_implementation:
            from .file_writer_factory import FileWriterFactory

            factory = FileWriterFactory()
            file_writer_config = config.get("batch", {}).get("file_writer", {})
            writer_type = file_writer_config.get("type", "csv")
            writer_params = file_writer_config.get("params", {})

            self.writer_implementation = factory.create_writer(
                writer_type, writer_params
            )

        self.logger.debug(
            f"BatchWriter initialized with {type(self.writer_implementation).__name__}"
        )

    def write(
        self, df: pd.DataFrame, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Write DataFrame (BaseWriter interface).

        Args:
            df: DataFrame to write
            metadata: Optional metadata

        Returns:
            Dictionary with write operation results
        """
        # Increment batch counter first (1-based indexing)
        self.batches_written += 1

        # Convert to batch format and delegate
        batch_info = {
            "batch_index": self.batches_written,
            "batch_size": len(df),
            "timestamp": pd.Timestamp.now().isoformat(),
        }

        if metadata:
            batch_info.update(metadata)

        # Delegate to the actual writer
        result = self.writer_implementation.write(df, batch_info)

        # Track last written path from underlying writer if available
        last_path = getattr(self.writer_implementation, "last_written_path", None)
        if last_path:
            self.written_paths.append(last_path)

        # Update row counter
        self.total_rows_written += len(df)

        self.logger.debug(f"Batch write result: {result}")

        return {
            "status": "success",
            "rows_written": len(df),
            "batch_index": self.batches_written,
            "metadata": metadata,
        }

    def finalize(self) -> dict[str, Any]:
        """
        Finalize batch writing operations.

        Returns:
            Dictionary with summary of all write operations
        """
        self.logger.info(
            f"Finalizing batch writer. Total batches: {self.batches_written}, Total rows: {self.total_rows_written}"
        )

        # Finalize the actual writer
        actual_summary = self.writer_implementation.finalize()

        summary = {
            "total_rows_written": self.total_rows_written,
            "total_batches_written": self.batches_written,
            "writer_type": "batch",
            "writer_implementation_type": type(self.writer_implementation).__name__,
            "writer_implementation_summary": actual_summary,
        }

        # If the writer implementation tracked the last path, include it
        last_path = getattr(self.writer_implementation, "last_written_path", None)
        if last_path:
            summary["last_written_path"] = last_path
        if self.written_paths:
            summary["written_paths"] = list(self.written_paths)

        self.logger.debug(f"Batch writer summary: {summary}")
        return summary
