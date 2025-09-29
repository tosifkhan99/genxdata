import pandas as pd
import yaml

from core.orchestrator import DataOrchestrator


def _make_stream_config(tmp_path):
    cfg = {
        "metadata": {"name": "stream_cfg", "description": "stream test", "version": "1.0.0"},
        "column_name": ["id"],
        "num_of_rows": 5,
        "shuffle": False,
        # normal writer needed by validation; we'll pass batch section for chunked mode
        "file_writer": {"type": "json", "params": {"output_path": str(tmp_path / "ignored.json")}},
        "configs": [
            {"column_names": ["id"], "strategy": {"name": "SERIES_STRATEGY", "params": {"start": 1, "step": 1}}}
        ],
        "batch": {
            "batch_size": 2,
            "chunk_size": 2,
            "file_writer": {"type": "json", "params": {"output_path": str(tmp_path / "stream_out.json")}},
        },
    }
    return cfg


def test_streaming_processor_runs_in_chunks(tmp_path, monkeypatch):
    # Lower the enforced minimum rows so we can test small configs quickly
    monkeypatch.setattr(
        "configs.GENERATOR_SETTINGS.MINIMUM_ROWS_ALLOWED", 1, raising=False
    )
    cfg = _make_stream_config(tmp_path)
    orch = DataOrchestrator(config=cfg, stream=str(tmp_path / "stream_cfg.yaml"), batch=None, log_level="INFO")
    # Save stream cfg to provide a path; orchestrator will load it
    (tmp_path / "stream_cfg.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))

    result = orch.run()
    assert result["status"] == "success"
    # Expect 3 chunks for 5 rows with chunk_size=2 (2+2+1)
    assert result["processor_type"] == "streaming"
    assert result["rows_generated"] == 5
