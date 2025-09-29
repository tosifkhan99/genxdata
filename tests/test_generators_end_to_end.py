import json
import os
import re
from datetime import datetime, timedelta

import pandas as pd

from core.orchestrator import DataOrchestrator
from utils.generator_utils import generator_to_config


def _write_json(path: str, content: dict) -> None:
    with open(path, "w") as f:
        json.dump(content, f, indent=2)


def _load_yaml(path: str) -> dict:
    import yaml

    with open(path) as f:
        return yaml.safe_load(f)


def test_generator_mapping_minimal_end_to_end(tmp_path):
    """
    End-to-end test using the generator mapping utilities (same flow as CLI create-config)
    to generate a small dataset and validate output.
    """
    # Build config from pre-defined generators
    config = generator_to_config(
        {
            "full_name": "FULL_NAME",
            "email": "EMAIL_PATTERN",
            "age": "PERSON_AGE",
        },
        num_rows=100,
        metadata={
            "name": "generator_mapping_e2e",
            "description": "E2E from generator mapping",
            "version": "1.0.0",
        },
    )

    # Override file writer to write to tmp json
    output_path = os.path.join(str(tmp_path), "gen_mapping.json")
    config["file_writer"] = {
        "type": "JSON_WRITER",
        "params": {
            "output_path": output_path,
            "orient": "records",
            "date_format": "iso",
            "indent": 2,
        },
    }

    orch = DataOrchestrator(config=config, stream=None, batch=None, log_level="INFO")
    result = orch.run()

    assert result["status"] == "success"
    assert os.path.exists(output_path)
    with open(output_path) as f:
        rows = json.load(f)
    assert len(rows) == 100
    # Basic column checks
    assert set(rows[0].keys()) == {"full_name", "email", "age"}


def test_uuid_and_date_series_from_all_generators_example(tmp_path):
    """
    End-to-end test that extracts the UUID_STRATEGY and DATE_SERIES_STRATEGY examples
    from examples/generators/all_generators.yaml and validates generation.
    """
    all_examples_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "examples",
        "generators",
        "all_generators.yaml",
    )

    base_cfg = _load_yaml(all_examples_path)

    # Downselect to only our new columns to keep the test fast
    target_columns = ["UUID_V5", "DATE_SERIES_DAY"]
    filtered_configs = []
    for entry in base_cfg.get("configs", []):
        names = entry.get("column_names") or entry.get("names") or []
        if any(name in target_columns for name in names):
            filtered_configs.append(entry)

    assert filtered_configs, "Expected UUID_V5 and DATE_SERIES_DAY configs to exist"

    test_cfg = {
        "metadata": {"name": "uuid_date_series_subset"},
        "column_name": target_columns,
        "num_of_rows": 100,
        "shuffle": False,
        "configs": filtered_configs,
    }

    # Write to a temp JSON to simplify reading
    output_path = os.path.join(str(tmp_path), "subset.json")
    test_cfg["file_writer"] = {
        "type": "JSON_WRITER",
        "params": {
            "output_path": output_path,
            "orient": "records",
            "date_format": "iso",
            "indent": 2,
        },
    }

    orch = DataOrchestrator(config=test_cfg, stream=None, batch=None, log_level="INFO")
    result = orch.run()
    assert result["status"] == "success"
    assert os.path.exists(output_path)

    with open(output_path) as f:
        rows = json.load(f)

    assert len(rows) == 100 
    # Validate presence of columns
    assert set(rows[0].keys()) == {"UUID_V5", "DATE_SERIES_DAY"}

    # Validate UUID format (canonical hyphenated lowercase)
    uuid_regex = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    for r in rows:
        assert uuid_regex.match(r["UUID_V5"]) is not None

    # Validate date series contiguous from 2024-01-01
    start = datetime.strptime("2024-01-01", "%Y-%m-%d")
    for i, r in enumerate(rows):
        d = datetime.strptime(r["DATE_SERIES_DAY"], "%Y-%m-%d")
        assert d == start + timedelta(days=i)


