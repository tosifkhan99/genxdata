"""
Abstract base classes for queue producers and configuration.

Defines `QueueConfig` (validates and exposes producer config) and `QueueProducer`
interfaces. Concrete implementations (AMQP/Kafka) should subclass these and
provide connection lifecycle and data sending behavior.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


class QueueConfig(ABC):
    """Abstract base class for queue configuration."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize queue configuration.

        Args:
            config: Configuration dictionary containing queue-specific settings
        """
        self.config = config
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> None:
        """Validate the configuration parameters."""
        pass

    @property
    @abstractmethod
    def queue_type(self) -> str:
        """Return the queue type identifier."""
        pass

    @abstractmethod
    def get_producer_config(self) -> dict[str, Any]:
        """Get the producer configuration dictionary."""
        pass


class QueueProducer(ABC):
    """Abstract base class for queue producers."""

    def __init__(self, config: QueueConfig):
        """
        Initialize the queue producer.

        Args:
            config: Queue configuration instance
        """
        self.config = config
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the queue system."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the queue system."""
        pass

    @abstractmethod
    def send_dataframe(
        self, df: "pd.DataFrame", batch_info: dict[str, Any] | None = None
    ) -> None:
        """
        Send a DataFrame to the queue.

        Args:
            df: DataFrame to send
            batch_info: Optional metadata about the batch
        """
        pass

    @abstractmethod
    def send_message(self, message_data: Any) -> None:
        """
        Send a custom message to the queue.

        Args:
            message_data: Message data to send
        """
        pass

    @property
    def is_connected(self) -> bool:
        """Check if the producer is connected."""
        return self._connected

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
