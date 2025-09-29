import json
import subprocess
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the CLI with given arguments and return the completed process."""
    cmd = [sys.executable, "-m", "cli.main_cli", *args]
    return subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_global_log_level_and_list_generators_filter(tmp_path: Path):
    proc = run_cli(["--log-level", "DEBUG", "list-generators", "--filter", "EMAIL"])
    assert proc.returncode == 0, proc.stderr
    assert "Available generators" in proc.stdout or "Available generators" in proc.stderr


def test_list_generators_show_stats():
    proc = run_cli(["list-generators", "--show-stats"]) 
    assert proc.returncode == 0, proc.stderr
    assert ("Strategy distribution" in proc.stdout) or ("Strategy distribution" in proc.stderr)


def test_show_generator():
    # Pick a commonly available generator name from generators/*.json
    proc = run_cli(["show-generator", "EMAIL_PATTERN"]) 
    assert proc.returncode == 0, proc.stderr
    assert ("Generator: EMAIL_PATTERN" in proc.stdout) or ("Generator: EMAIL_PATTERN" in proc.stderr)


def test_by_strategy():
    proc = run_cli(["by-strategy", "RANDOM_NAME_STRATEGY"]) 
    assert proc.returncode == 0, proc.stderr
    assert ("Generators using RANDOM_NAME_STRATEGY" in proc.stdout) or (
        "Generators using RANDOM_NAME_STRATEGY" in proc.stderr
    )


def _write_minimal_config(path: Path, writer_path: Path) -> None:
    """Write a minimal, valid config YAML for quick generation."""
    cfg = {
        "metadata": {"name": "test_config", "description": "cli test", "version": "1.0.0"},
        "column_name": ["id"],
        "num_of_rows": 2,
        "shuffle": False,
        "file_writer": {
            # Use normalized types supported by FileWriterFactory (lowercase)
            "type": "json",
            "params": {"output_path": str(writer_path)},
        },
        "configs": [
            {
                "column_names": ["id"],
                "strategy": {"name": "SERIES_STRATEGY", "params": {"start": 1, "step": 1}},
            }
        ],
    }
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))


def test_create_config_with_mapping_and_output(tmp_path: Path):
    output = tmp_path / "generated_config.json"
    proc = run_cli(
        [
            "create-config",
            "--mapping",
            "name:FULL_NAME",
            "--output",
            str(output),
            "--rows",
            "3",
            "--name",
            "cli_gen",
            "--description",
            "desc",
        ]
    )
    assert proc.returncode == 0, proc.stderr
    assert output.exists()
    data = json.loads(output.read_text())
    assert data["num_of_rows"] == 3
    assert data["column_name"]
    assert data["configs"][0]["column_names"][0]


def test_create_config_with_mapping_file_yaml(tmp_path: Path):
    mapping_file = tmp_path / "mapping.yaml"
    mapping_file.write_text(yaml.safe_dump({"col": "FULL_NAME"}))
    output = tmp_path / "cfg.yaml"

    proc = run_cli([
        "create-config",
        "--mapping-file",
        str(mapping_file),
        "--output",
        str(output),
    ])
    assert proc.returncode == 0, proc.stderr
    assert output.exists()
    cfg = yaml.safe_load(output.read_text())
    assert cfg["column_name"] == ["col"]
    assert cfg["configs"][0]["strategy"]["name"]


def test_generate_with_minimal_config(tmp_path: Path):
    cfg_path = tmp_path / "config.yaml"
    out_path = tmp_path / "out.json"
    _write_minimal_config(cfg_path, out_path)

    proc = run_cli(["generate", str(cfg_path)])
    assert proc.returncode == 0, proc.stderr
    # File should be written (and zipped removal is not used in CLI generate)
    assert out_path.exists()


def test_generate_with_batch_flag(tmp_path: Path):
    # Base config
    cfg_path = tmp_path / "config.yaml"
    out_path = tmp_path / "out.json"
    _write_minimal_config(cfg_path, out_path)

    # Batch config: include a top-level 'batch' section so CLI selects BatchWriter
    batch_cfg_path = tmp_path / "batch.yaml"
    batch_out = tmp_path / "batch_out.json"
    batch_cfg = {
        "metadata": {"name": "batch_cfg", "description": "cli test", "version": "1.0.0", "type": "batch"},
        "column_name": ["id"],
        "num_of_rows": 2,
        "shuffle": False,
        # minimal valid base configs for validation path
        "file_writer": {"type": "json", "params": {"output_path": str(tmp_path / "ignored.json")}},
        "configs": [
            {
                "column_names": ["id"],
                "strategy": {"name": "SERIES_STRATEGY", "params": {"start": 1, "step": 1}},
            }
        ],
        "batch": {
            "batch_size": 1,
            "chunk_size": 1,
            "file_writer": {"type": "json", "params": {"output_path": str(batch_out)}},
        },
    }
    batch_cfg_path.write_text(yaml.safe_dump(batch_cfg, sort_keys=False))

    proc = run_cli(["generate", str(cfg_path), "--batch", str(batch_cfg_path)])
    assert proc.returncode == 0, proc.stderr
    # In batch mode, the writer comes from the batch config; check batch_out
    assert batch_out.exists()


def test_generate_with_stream_flag_uses_batch_writer(tmp_path: Path):
    # Base config
    cfg_path = tmp_path / "config.yaml"
    out_path = tmp_path / "out.json"
    _write_minimal_config(cfg_path, out_path)

    # Stream config: include a 'batch' section to avoid MQ connection in StreamWriter
    # and satisfy validation by duplicating minimal config keys
    stream_cfg_path = tmp_path / "stream.yaml"
    stream_out = tmp_path / "stream_out.json"
    base = yaml.safe_load(cfg_path.read_text())
    base["batch"] = {
        "batch_size": 1,
        "chunk_size": 1,
        "file_writer": {"type": "json", "params": {"output_path": str(stream_out)}},
    }
    stream_cfg_path.write_text(yaml.safe_dump(base, sort_keys=False))

    proc = run_cli(["generate", str(cfg_path), "--stream", str(stream_cfg_path)])
    assert proc.returncode == 0, proc.stderr
    # In stream mode with a 'batch' section, output path comes from that section
    assert stream_out.exists()


def test_stats_command():
    proc = run_cli(["stats"]) 
    assert proc.returncode == 0, proc.stderr
    assert ("Generator Statistics" in proc.stdout) or ("Generator Statistics" in proc.stderr)


