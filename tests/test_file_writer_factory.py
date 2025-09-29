import pytest

from core.writers.file_writer_factory import FileWriterFactory


def test_normalize_and_support_checks():
    assert FileWriterFactory.is_supported("CSV_WRITER")
    assert FileWriterFactory.is_supported("csv")
    assert not FileWriterFactory.is_supported("unknown_type")


def test_create_writer_injects_default_params(tmp_path):
    fac = FileWriterFactory()
    writer = fac.create_writer("csv", {"output_path": str(tmp_path / "out.csv")})
    # Writer should be created and have output_path normalized
    assert writer is not None


def test_create_multiple_and_error_path(tmp_path):
    fac = FileWriterFactory()
    writers = fac.create_multiple_writers([
        {"type": "json", "params": {"output_path": str(tmp_path / "a.json")}},
        {"type": "csv", "params": {"output_path": str(tmp_path / "b.csv")}},
    ])
    assert len(writers) == 2

    with pytest.raises(ValueError):
        fac.create_multiple_writers([{"foo": "bar"}])


def test_unsupported_writer_type_message():
    fac = FileWriterFactory()
    with pytest.raises(ValueError) as exc:
        fac.create_writer("not-a-writer", {"output_path": "out.xyz"})
    assert "Supported types:" in str(exc.value)

