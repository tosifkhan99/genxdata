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


def _write_minimal_config(path: Path, writer_path: Path) -> None:
    cfg = {
        "metadata": {"name": "perf_cfg", "description": "cli perf test", "version": "1.0.0"},
        "column_name": ["id"],
        "num_of_rows": 3,
        "shuffle": False,
        "file_writer": {"type": "json", "params": {"output_path": str(writer_path)}},
        "configs": [
            {
                "column_names": ["id"],
                "strategy": {"name": "SERIES_STRATEGY", "params": {"start": 1, "step": 1}},
            }
        ],
    }
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))


def test_generate_with_perf_report_prints_report(tmp_path: Path):
    cfg_path = tmp_path / "config.yaml"
    out_path = tmp_path / "out.json"
    _write_minimal_config(cfg_path, out_path)

    proc = run_cli(["generate", str(cfg_path), "--perf-report"]) 
    assert proc.returncode == 0, proc.stderr
    combined = proc.stdout + "\n" + proc.stderr
    assert "Performance Report:" in combined or "Performance Report:" in proc.stderr

