import pytest

from core.writers.stream_writer import StreamWriter


def test_stream_writer_missing_queue_raises():
    cfg = {"amqp": {"host": "x", "port": 5672}}  # missing 'queue'
    with pytest.raises(ValueError):
        StreamWriter(cfg)


def test_stream_writer_missing_url_and_host_port_raises():
    cfg = {"amqp": {"queue": "q"}}  # neither url nor host+port
    with pytest.raises(ValueError):
        StreamWriter(cfg)


class _FailingProducer:
    def __init__(self):
        pass

    def connect(self):
        raise RuntimeError("connect failed")

    def disconnect(self):
        pass

    def send_dataframe(self, *_args, **_kwargs):
        raise RuntimeError("send failed")


class _FailingFactory:
    @staticmethod
    def create_from_config(_cfg):
        return _FailingProducer()


def test_stream_writer_producer_failures(monkeypatch):
    # Patch factory to a failing producer
    monkeypatch.setattr(
        "core.writers.stream_writer.QueueFactory", _FailingFactory, raising=True
    )

    cfg = {"amqp": {"host": "x", "port": 5672, "queue": "q"}}

    with pytest.raises(Exception):
        StreamWriter(cfg)  # connect fails

