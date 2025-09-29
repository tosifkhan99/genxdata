import os
from datetime import datetime

import pandas as pd
import pytest

from core.writers.batch_writer import BatchWriter
from core.writers.csv_file_writer import CsvFileWriter
from core.writers.file_writer_factory import FileWriterFactory


def test_file_writer_factory_normalize_and_unsupported():
    # Suffix and case normalization
    norm = FileWriterFactory._normalize_type("CSV_WRITER")
    assert norm == "csv"

    # Unsupported type raises ValueError
    with pytest.raises(ValueError):
        FileWriterFactory().create_writer("unknown", {"output_path": "x"})


def test_base_file_writer_metadata_substitution(tmp_path):
    # output path includes placeholders
    path_tpl = os.path.join(str(tmp_path), "file_{batch_index}_{timestamp}.csv")
    writer = CsvFileWriter({"output_path": path_tpl})

    df = pd.DataFrame({"a": [1, 2, 3]})
    ts = datetime(2025, 1, 1, 0, 0, 0).isoformat()
    res = writer.write(df, {"batch_index": 5, "timestamp": ts})
    assert res["status"] == "success"
    assert os.path.exists(res["output_path"])  # path resolved with placeholders


def test_batch_writer_delegates_and_increments_batches(tmp_path):
    inner_path = os.path.join(str(tmp_path), "out_{batch_index}.csv")
    inner = CsvFileWriter({"output_path": inner_path})
    batch_writer = BatchWriter({"batch": {"file_writer": {}}}, inner)

    df = pd.DataFrame({"a": list(range(10))})

    # first batch
    res1 = batch_writer.write(df, {"batch_index": 1})
    assert res1["batch_index"] == 1

    # second batch
    res2 = batch_writer.write(df, {"batch_index": 2})
    assert res2["batch_index"] == 2

    # finalize returns summary
    summary = batch_writer.finalize()
    assert summary["total_batches_written"] == 2
    # inner files created
    assert os.path.exists(os.path.join(str(tmp_path), "out_1.csv"))
    assert os.path.exists(os.path.join(str(tmp_path), "out_2.csv"))
