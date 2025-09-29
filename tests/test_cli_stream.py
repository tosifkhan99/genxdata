import subprocess
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "cli.main_cli", *args]
    return subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_base_and_stream_cfg(tmp_path: Path) -> tuple[Path, Path, Path]:
    base_out = tmp_path / "base_out.json"
    base_cfg = {
        "metadata": {"name": "cli_stream_base", "description": "cli test", "version": "1.0.0"},
        "column_name": ["id"],
        "num_of_rows": 5,
        "shuffle": False,
        "file_writer": {"type": "json", "params": {"output_path": str(base_out)}},
        "configs": [
            {
                "column_names": ["id"],
                "strategy": {"name": "SERIES_STRATEGY", "params": {"start": 1, "step": 1}},
            }
        ],
    }
    base_cfg_path = tmp_path / "base.yaml"
    base_cfg_path.write_text(yaml.safe_dump(base_cfg, sort_keys=False))

    stream_out = tmp_path / "stream_out.json"
    stream_cfg = {
        **base_cfg,
        "metadata": {"name": "cli_stream_stream", "description": "cli test", "version": "1.0.0"},
        "batch": {
            "batch_size": 2,
            "chunk_size": 2,
            "file_writer": {"type": "json", "params": {"output_path": str(stream_out)}},
        },
    }
    stream_cfg_path = tmp_path / "stream.yaml"
    stream_cfg_path.write_text(yaml.safe_dump(stream_cfg, sort_keys=False))

    return base_cfg_path, stream_cfg_path, stream_out


def test_cli_generate_with_stream_flag(tmp_path: Path):
    base_cfg_path, stream_cfg_path, stream_out = _write_base_and_stream_cfg(tmp_path)

    proc = run_cli(["generate", str(base_cfg_path), "--stream", str(stream_cfg_path)])
    assert proc.returncode == 0, proc.stderr
    # In stream mode with a 'batch' section, output path comes from that section
    assert stream_out.exists()


def test_cli_generate_stream_with_perf_report(tmp_path: Path):
    base_cfg_path, stream_cfg_path, stream_out = _write_base_and_stream_cfg(tmp_path)

    proc = run_cli([
        "--log-level", "INFO",
        "generate", str(base_cfg_path), "--stream", str(stream_cfg_path), "--perf-report",
    ])
    assert proc.returncode == 0, proc.stderr
    combined = proc.stdout + "\n" + proc.stderr
    assert "Performance Report:" in combined or "Performance Report:" in proc.stderr

