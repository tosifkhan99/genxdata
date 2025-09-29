import argparse
import csv
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path so `core` imports resolve when running from tools/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.orchestrator import DataOrchestrator
from utils.yaml_loader import read_yaml

"""
Tool: run performance benchmark and save performance report to CSV.

- Loads a complex config YAML (perf_all_strategies.yaml) with 1M rows.
- Runs the orchestrator with perf_report=True (NORMAL mode).
- Extracts performance_report and writes it to a CSV file.
- Writes a columns->uses_mask (yes/no) CSV derived from the config.
- Supports multiple runs to let min/max/avg diverge.
"""

# CSV schema for performance report
PERF_FIELDNAMES = [
    "operation",
    "count",
    "total_seconds",
    "avg_seconds",
    "min_seconds",
    "max_seconds",
    "rows_per_second",
    "run_timestamp",
]

MASK_FIELDNAMES = ["column", "uses_mask"]

logger = logging.getLogger("tools.perf_benchmark")


def ensure_output_dir(path: Path) -> None:
    directory = path.parent
    if directory and not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)


def parse_performance_report(report_text: str) -> list[dict[str, Any]]:
    """Parse the text performance report from utils.performance_timer into rows."""
    rows: list[dict[str, Any]] = []
    if not report_text or report_text.strip() == "No performance data collected":
        return rows

    lines = [ln for ln in report_text.splitlines() if ln.strip()]
    header_idx = -1
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("Operation"):
            header_idx = i
            break
    if header_idx == -1:
        return rows

    data_lines = lines[header_idx + 2 :]
    for ln in data_lines:
        try:
            tokens = ln.rstrip().split()
            if len(tokens) < 7:
                continue
            count = tokens[-6]
            total = tokens[-5]
            avg = tokens[-4]
            min_s = tokens[-3]
            max_s = tokens[-2]
            rps = tokens[-1]
            operation = " ".join(tokens[: -6])

            rows.append(
                {
                    "operation": operation.strip(),
                    "count": int(float(count)),
                    "total_seconds": float(total),
                    "avg_seconds": float(avg),
                    "min_seconds": float(min_s),
                    "max_seconds": float(max_s),
                    "rows_per_second": None if rps == "N/A" else float(rps),
                }
            )
        except Exception as e:
            logger.debug(f"Skipping malformed report line: {ln} ({e})")
            continue

    return rows


def write_perf_csv(rows: list[dict[str, Any]], csv_path: Path) -> None:
    ensure_output_dir(csv_path)
    ts = datetime.now(UTC).isoformat()
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PERF_FIELDNAMES)
        writer.writeheader()
        for r in rows:
            r = {**r, "run_timestamp": ts}
            writer.writerow(r)


def write_columns_mask_csv(cfg: dict[str, Any], csv_path: Path) -> None:
    """Write a CSV mapping each configured column to whether it uses a mask (yes/no)."""
    ensure_output_dir(csv_path)
    column_names: list[str] = cfg.get("column_name", []) or []
    configs: list[dict[str, Any]] = cfg.get("configs", []) or []

    masked_columns: set[str] = set()
    for entry in configs:
        try:
            # Correct field in backend config is 'column_names'
            names = entry.get("column_names", []) or []
            has_mask = bool(entry.get("mask"))
            if has_mask:
                for n in names:
                    masked_columns.add(str(n))
        except Exception as e:
            logger.debug(f"Skipping config entry while computing masks: {e}")
            continue

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MASK_FIELDNAMES)
        writer.writeheader()
        for col in column_names:
            writer.writerow({"column": col, "uses_mask": "yes" if col in masked_columns else "no"})


def run_benchmark(cfg: dict[str, Any], runs: int) -> list[dict[str, Any]]:
    """Execute the orchestrator `runs` times and return aggregated perf rows."""
    from utils.performance_timer import get_performance_report  # defer import

    for i in range(max(1, runs)):
        logger.info(f"Starting run {i + 1}/{runs}")
        orchestrator = DataOrchestrator(
            config=cfg, perf_report=True, stream=None, batch=None, log_level="INFO"
        )
        result = orchestrator.run()
        if result.get("status") != "success":
            logger.error(f"Generation failed: {result}")
            raise SystemExit(1)

    perf_text = get_performance_report()
    rows = parse_performance_report(perf_text)
    if not rows:
        logger.error("No performance report generated or could not parse.")
        raise SystemExit(2)
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GenXData performance benchmark and export CSVs.")
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=str(Path(__file__).parent.parent / "examples/by-strategy/perf_all_strategies.yaml"),
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--perf-csv",
        "-o",
        type=str,
        default=str(Path(__file__).parent.parent / "output/perf_report.csv"),
        help="Path to write performance CSV",
    )
    parser.add_argument(
        "--mask-csv",
        "-m",
        type=str,
        default=str(Path(__file__).parent.parent / "output/perf_columns_masks.csv"),
        help="Path to write columns->mask map CSV",
    )
    parser.add_argument(
        "--runs",
        "-r",
        type=int,
        default=1,
        help="Number of times to run the benchmark (>=1)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s - %(message)s",
    )

    cfg_path = Path(args.config).resolve()
    perf_csv_path = Path(args.perf_csv).resolve()
    mask_csv_path = Path(args.mask_csv).resolve()
    runs = max(1, int(args.runs))

    if not cfg_path.exists():
        logger.error(f"Config file not found: {cfg_path}")
        raise SystemExit(1)

    # Load config and write masks CSV first
    cfg = read_yaml(str(cfg_path))
    write_columns_mask_csv(cfg, mask_csv_path)

    # Run benchmark and export perf CSV
    rows = run_benchmark(cfg, runs)
    write_perf_csv(rows, perf_csv_path)

    logger.info(f"Performance report written to {perf_csv_path} with {len(rows)} rows.")
    logger.info(f"Columns->mask map written to {mask_csv_path}.")


if __name__ == "__main__":
    main()
