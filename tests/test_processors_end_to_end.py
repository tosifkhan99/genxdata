import os

import pandas as pd

from core.orchestrator import DataOrchestrator


def _write_yaml(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def _normal_config(tmpdir: str) -> str:
    path = os.path.join(tmpdir, "normal.yaml")
    _write_yaml(
        path,
        """
metadata:
  name: test_normal
column_name: [id, value]
num_of_rows: 100
shuffle: false
file_writer:
  type: CSV_WRITER
  params:
    output_path: {out}
configs:
  - column_names: [id]
    strategy:
      name: SERIES_STRATEGY
      params: {start: 1, step: 1}
  - column_names: [value]
    strategy:
      name: RANDOM_NUMBER_RANGE_STRATEGY
      params: {start: 0, end: 10}
""".replace("{out}", os.path.join(tmpdir, "normal.csv")),
    )
    return path


def _batch_config(tmpdir: str) -> str:
    path = os.path.join(tmpdir, "batch.yaml")
    _write_yaml(
        path,
        """
batch:
  output_dir: "batch_output_csv"
  file_prefix: "data_batch"
  file_format: "csv"
  batch_size: 500
  file_writer:
    type: "csv"
    params:
      output_path: ./batch_output_csv/batch_example_{batch_index}.csv
metadata:
  name: test_batch
column_name: [id, name]
num_of_rows: 200
shuffle: false
file_writer: {type: CSV, params: {output_path: {out}}}
configs:
  - column_names: [id]
    strategy:
      name: SERIES_STRATEGY
      params: {start: 1000, step: 1}
  - column_names: [name]
    strategy:
      name: RANDOM_NAME_STRATEGY
      params: {name_type: first, gender: any, case: title}
""".replace("{out}", os.path.join(tmpdir, "batch.csv")),
    )
    return path


def _stream_config(tmpdir: str) -> tuple[str, str]:
    main = os.path.join(tmpdir, "stream_main.yaml")
    stream = os.path.join(tmpdir, "stream.yaml")
    _write_yaml(
        main,
        """
metadata: {name: test_stream}
column_name: [tick]
num_of_rows: 120
shuffle: false
file_writer: {type: CSV, params: {output_path: {out}}}
configs:
  - column_names: [tick]
    strategy:
      name: SERIES_STRATEGY
      params: {start: 0, step: 1}
""".replace("{out}", os.path.join(tmpdir, "stream.csv")),
    )
    _write_yaml(
        stream,
        """
metadata: {type: stream}
batch_size: 50
chunk_size: 25
batch: {file_writer: {type: CSV, params: {output_path: {out}}}}
""".replace("{out}", os.path.join(tmpdir, "stream_chunk.csv")),
    )
    return main, stream


def test_normal_mode_end_to_end(tmp_path):
    cfg = _normal_config(str(tmp_path))
    orch = DataOrchestrator(
        config=_load_yaml(cfg), stream=None, batch=None, log_level="INFO"
    )
    result = orch.run()
    assert result["status"] == "success"
    out = os.path.join(str(tmp_path), "normal.csv")
    assert os.path.exists(out)
    df = pd.read_csv(out)
    assert len(df) == 100
    assert list(df.columns) == ["id", "value"]


def test_batch_mode_end_to_end(tmp_path):
    cfg = _batch_config(str(tmp_path))
    orch = DataOrchestrator(
        config=_load_yaml(cfg), stream=None, batch=cfg, log_level="INFO"
    )
    result = orch.run()
    print(result)
    assert result["status"] == "success"
    # Batch mode writes chunk files via BatchWriter, not the normal file_writer path
    batch_out = os.path.join("batch_output_csv", "batch_example_0.csv")
    assert os.path.exists(batch_out)
    df = pd.read_csv(batch_out)
    assert len(df) == 200
    assert set(df.columns) == {"id", "name"}


def test_stream_mode_end_to_end(tmp_path):
    main_cfg, stream_cfg = _stream_config(str(tmp_path))
    orch = DataOrchestrator(
        config=_load_yaml(main_cfg), stream=stream_cfg, batch=None, log_level="INFO"
    )
    result = orch.run()
    assert result["status"] == "success"
    # streamed chunks file
    out = os.path.join(str(tmp_path), "stream_chunk.csv")
    assert os.path.exists(out)


def _load_yaml(p: str) -> dict:
    import yaml

    with open(p) as f:
        return yaml.safe_load(f)
