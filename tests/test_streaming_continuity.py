import os

import pandas as pd

from core.orchestrator import DataOrchestrator


class DummyConfig:
    def __init__(
        self, url: str = "amqp://user:***@localhost:5672", queue: str = "test-queue"
    ):
        self.url = url
        self.queue = queue

    @property
    def queue_type(self) -> str:
        return "amqp"


class DummyProducer:
    def __init__(self):
        self.config = DummyConfig()
        self.connected = False
        self.batches: list[pd.DataFrame] = []

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def send_dataframe(self, df: pd.DataFrame, batch_info: dict | None = None) -> None:
        # Store a copy to avoid mutation
        self.batches.append(df.copy())

    def send_message(self, message_data) -> None:
        pass


def test_streaming_series_continuity(monkeypatch, tmp_path):
    # Monkeypatch QueueFactory to use DummyProducer
    from core.writers import stream_writer as sw

    dummy_producer = DummyProducer()

    class DummyQueueFactory:
        @classmethod
        def create_from_config(cls, cfg):
            return dummy_producer

    monkeypatch.setattr(sw, "QueueFactory", DummyQueueFactory)

    # Main generator config (validates file_writer but it won't be used)
    main_cfg = {
        "metadata": {"name": "streaming_series_test"},
        "column_name": ["id"],
        "num_of_rows": 260,
        "shuffle": False,
        "file_writer": {
            "type": "csv",
            "params": {"output_path": os.path.join(str(tmp_path), "noop.csv")},
        },
        "configs": [
            {
                "column_names": ["id"],
                "strategy": {
                    "name": "SERIES_STRATEGY",
                    "params": {"start": 1, "step": 1},
                },
            }
        ],
    }

    # Streaming config (batch_size=50). Include dummy amqp section to satisfy validation
    stream_cfg_path = os.path.join(str(tmp_path), "stream_cfg.yaml")
    with open(stream_cfg_path, "w") as f:
        f.write(
            """
metadata: {name: stream_test}
streaming: {batch_size: 50}
amqp: {url: amqp://user:pass@localhost:5672, queue: test}
"""
        )

    orch = DataOrchestrator(
        config=main_cfg, stream=stream_cfg_path, batch=None, log_level="INFO"
    )
    result = orch.run()

    assert result["status"] == "success"

    # Verify we received batches and they are continuous across chunks
    assert len(dummy_producer.batches) > 0

    last_value = 0
    total_rows = 0
    for df in dummy_producer.batches:
        assert "id" in df.columns
        # Check that this chunk starts right after previous ended
        first = int(df["id"].iloc[0])
        if total_rows > 0:
            assert first == last_value + 1
        last_value = int(df["id"].iloc[-1])
        total_rows += len(df)

    assert total_rows == result["rows_generated"]
