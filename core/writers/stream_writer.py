"""
Stream writer implementation for GenXData.

Handles writing DataFrames to message queues (AMQP, Kafka, etc.).
"""

from typing import Any

import pandas as pd

from messaging.factory import QueueFactory
from utils.logging import Logger

from .base_writer import BaseWriter


class StreamWriter(BaseWriter):
    """
    Writer implementation for streaming/message queue outputs.

    Uses the messaging module to send data to various message queue systems.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the stream writer.

        Args:
            config: Stream writer configuration containing queue settings
        """
        super().__init__(config)
        self.logger = Logger.get_logger("stream_writer")
        self.queue_producer = None
        self.total_rows_written = 0
        self.total_batches_sent = 0
        self.queue_meta: dict[str, Any] = {}
        self.normalized_queue_config: dict[str, Any] | None = None

        # Validate configuration and normalize queue settings
        self.validate_config()
        # Initialize queue producer
        self._initialize_producer()

        self.logger.debug("StreamWriter initialized with config")

    def _extract_queue_section(self) -> tuple[str, dict[str, Any]] | None:
        """Return (queue_type, queue_section) from config supporting nested or flat forms."""
        # Nested form: {"amqp": {...}} or {"kafka": {...}}
        for key in ("amqp", "kafka"):
            if key in self.config and isinstance(self.config[key], dict):
                return key, self.config[key]

        # Flat form: {"type": "amqp", "host": ..., "port": ..., "queue": ...}
        qtype = self.config.get("type")
        if isinstance(qtype, str) and qtype.lower() in {"amqp", "kafka"}:
            return qtype.lower(), self.config
        return None

    def validate_config(self) -> bool:
        """
        Validate stream writer configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        super().validate_config()

        # Accept nested or flat queue config and normalize
        extracted = self._extract_queue_section()
        if not extracted:
            raise ValueError(
                "Stream writer config must include a supported queue section (e.g., nested 'amqp'/'kafka' or flat 'type')."
            )

        queue_type, section = extracted
        # Validate minimal required fields for convenience (messaging also validates)
        # Accept either a single URL or host+port; 'queue' is always required
        if "queue" not in section:
            raise ValueError(
                f"Stream writer config missing required fields for {queue_type}: queue"
            )
        has_url = "url" in section and isinstance(section["url"], str)
        has_host_port = "host" in section and "port" in section
        if not (has_url or has_host_port):
            raise ValueError(
                f"Stream writer config missing required fields for {queue_type}: provide either 'url' or 'host' and 'port'"
            )

        # Store normalized meta and config
        self.queue_meta = {
            "queue_type": queue_type,
            "host": section.get("host") or section.get("url"),
            "port": section.get("port"),
            "queue": section.get("queue"),
        }
        self.normalized_queue_config = {queue_type: section}

        return True

    def _initialize_producer(self):
        """Initialize the message queue producer."""
        try:
            self.logger.debug("Initializing queue producer")
            cfg = (
                self.normalized_queue_config
                if self.normalized_queue_config
                else self.config
            )
            self.queue_producer = QueueFactory.create_from_config(cfg)
            self.queue_producer.connect()
            # Attempt to log masked connection info if available
            try:
                amqp_conf = getattr(self.queue_producer, "config", None)
                masked = (
                    amqp_conf.get_connection_url_masked() if amqp_conf else "(unknown)"
                )
                self.logger.info(f"Successfully connected to message queue: {masked}")
            except Exception:
                self.logger.info("Successfully connected to message queue")
        except Exception as e:
            self.logger.error(f"Failed to initialize queue producer: {e}")
            raise

    def write(
        self, df: pd.DataFrame, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Write DataFrame to message queue.

        Args:
            df: DataFrame to write
            metadata: Optional metadata (batch info, etc.)

        Returns:
            Dictionary with write operation results
        """
        if df.empty:
            self.logger.warning("Received empty DataFrame, skipping write")
            return {"status": "skipped", "reason": "empty_dataframe"}

        if not self.queue_producer:
            self.logger.error("Queue producer not initialized")
            return {"status": "error", "error": "Queue producer not initialized"}

        self.logger.info(f"Sending DataFrame with {len(df)} rows to message queue")

        try:
            # Prepare batch information
            batch_info = {
                "rows": len(df),
                "columns": list(df.columns),
                "timestamp": pd.Timestamp.now().isoformat(),
            }

            # Add metadata if provided
            if metadata:
                batch_info.update(metadata)

            # Send DataFrame to queue
            self.queue_producer.send_dataframe(df, batch_info)

            # Update counters
            self.total_rows_written += len(df)
            self.total_batches_sent += 1

            self.logger.info(f"Successfully sent {len(df)} rows to message queue")

            return {
                "status": "success",
                "rows_written": len(df),
                "batch_info": batch_info,
                "metadata": metadata,
            }

        except Exception as e:
            self.logger.error(f"Error sending DataFrame to message queue: {e}")
            return {"status": "error", "error": str(e), "metadata": metadata}

    def finalize(self) -> dict[str, Any]:
        """
        Finalize stream writing operations and cleanup.

        Returns:
            Dictionary with summary of all write operations
        """
        self.logger.info(
            f"Finalizing stream writer. Total rows sent: {self.total_rows_written}"
        )

        # Disconnect from queue
        if self.queue_producer:
            try:
                self.queue_producer.disconnect()
                self.logger.info("Disconnected from message queue")
            except Exception as e:
                self.logger.warning(f"Error disconnecting from queue: {e}")

        summary = {
            "total_rows_written": self.total_rows_written,
            "total_batches_sent": self.total_batches_sent,
            "queue_type": self.queue_meta.get("queue_type", "unknown"),
            "queue_host": self.queue_meta.get("host", "unknown"),
            "queue_name": self.queue_meta.get("queue", "unknown"),
            "writer_type": "stream",
        }

        self.logger.debug(f"Stream writer summary: {summary}")
        return summary
