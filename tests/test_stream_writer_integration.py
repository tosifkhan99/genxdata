from types import SimpleNamespace

import pandas as pd

from core.writers.stream_writer import StreamWriter


class DummyProducer:
    def __init__(self):
        self.connected = False
        self.sent_batches = []
        # mimic expected config attributes used in finalize()
        self.config = SimpleNamespace(queue_type="amqp", url="x:5672", queue="q")

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def send_dataframe(self, df: pd.DataFrame, batch_info: dict | None = None):
        self.sent_batches.append((df.copy(), batch_info or {}))


class DummyFactory:
    @staticmethod
    def create_from_config(stream_config: dict):
        return DummyProducer()


def test_stream_writer_sends_batches(monkeypatch):
    # Patch the symbol used inside core.writers.stream_writer
    monkeypatch.setattr(
        "core.writers.stream_writer.QueueFactory", DummyFactory, raising=True
    )

    # Use nested config as expected by StreamWriter (top-level 'amqp' or 'kafka')
    cfg = {"amqp": {"type": "amqp", "host": "x", "port": 5672, "queue": "q"}}
    writer = StreamWriter(cfg)

    df = pd.DataFrame({"x": [1, 2, 3]})
    res = writer.write(df, {"batch_index": 1})
    assert res["status"] == "success"

    summary = writer.finalize()
    assert summary["total_rows_written"] == 3
    assert summary["total_batches_sent"] == 1
