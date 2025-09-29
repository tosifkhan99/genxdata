"""
AMQP-specific configuration implementation.
"""

from .base import QueueConfig


class AMQPConfig(QueueConfig):
    """Configuration class for AMQP queue connections."""

    def validate_config(self) -> None:
        """Validate AMQP configuration parameters."""
        if "url" not in self.config:
            raise ValueError("AMQP config must contain 'url' parameter")

        if "queue" not in self.config:
            raise ValueError("AMQP config must contain 'queue' parameter")

        # Optional parameters with defaults
        self.url = self.config["url"]
        self.queue = self.config["queue"]
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.virtual_host = self.config.get("virtual_host", "/")
        self.heartbeat = self.config.get("heartbeat", 60)
        self.queue_durable = self.config.get("queue_durable", True)
        self.queue_auto_delete = self.config.get("queue_auto_delete", False)

        # If credentials are embedded in URL and not provided separately, extract them
        try:
            from urllib.parse import urlparse

            parsed = urlparse(self.url)
            if parsed.username and not self.username:
                self.username = parsed.username
            if parsed.password and not self.password:
                self.password = parsed.password
        except Exception as e:
            # Fallback to a generic error type to avoid undefined exceptions
            raise ValueError("Invalid AMQP URL format") from e

    @property
    def queue_type(self) -> str:
        """Return the queue type identifier."""
        return "amqp"

    def get_connection_url(self) -> str:
        """Build the complete connection URL."""
        if self.username and self.password:
            # If credentials are provided, include them in URL
            if "://" in self.url:
                protocol, rest = self.url.split("://", 1)
                return f"{protocol}://{self.username}:{self.password}@{rest}"
            else:
                return f"amqp://{self.username}:{self.password}@{self.url}"
        return self.url

    def get_connection_url_masked(self) -> str:
        """Return a masked URL suitable for logging (password redacted)."""
        url = self.get_connection_url()
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            if parsed.username:
                safe_netloc = parsed.hostname or "localhost"
                if parsed.port:
                    safe_netloc = f"{safe_netloc}:{parsed.port}"
                return f"{parsed.scheme}://{parsed.username}:***@{safe_netloc}"
            return url
        except Exception:
            return url

    def get_producer_config(self) -> dict[str, str | int | bool]:
        """
        Provide a producer-friendly configuration dictionary.

        Note: The current AMQPProducer uses AMQPConfig directly, but this
        satisfies the abstract interface and allows other components to query
        connection parameters in a generic way.
        """
        return {
            "url": self.get_connection_url(),
            "queue": self.queue,
            "username": self.username,
            "virtual_host": self.virtual_host,
            "heartbeat": self.heartbeat,
            "queue_durable": self.queue_durable,
            "queue_auto_delete": self.queue_auto_delete,
        }
