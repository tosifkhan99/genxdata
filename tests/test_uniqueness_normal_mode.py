import os

import pandas as pd
import pytest

from core.orchestrator import DataOrchestrator


def make_config(strategy_name: str, params: dict, tmp_path: str) -> dict:
    return {
        "metadata": {"name": f"uniq_{strategy_name.lower()}"},
        "column_name": ["value"],
        "num_of_rows": 100,
        "shuffle": False,
        "file_writer": {
            "type": "csv",
            "params": {"output_path": os.path.join(tmp_path, f"{strategy_name}.csv")},
        },
        "configs": [
            {
                "column_names": ["value"],
                "strategy": {
                    "name": strategy_name,
                    "unique": True,
                    "params": params,
                },
            }
        ],
    }


@pytest.mark.parametrize(
    "strategy_name,params,skip_reason",
    [
        ("SERIES_STRATEGY", {"start": 1, "step": 1}, None),
        ("RANDOM_NUMBER_RANGE_STRATEGY", {"start": 1, "end": 1000000}, None),
        (
            "DISTRIBUTED_NUMBER_RANGE_STRATEGY",
            {
                "ranges": [
                    {"start": 1, "end": 500000, "distribution": 50},
                    {"start": 500001, "end": 1000000, "distribution": 50},
                ]
            },
            None,
        ),
        (
            "DATE_GENERATOR_STRATEGY",
            {
                "start_date": "2000-01-01",
                "end_date": "2020-12-31",
                "format": "%Y-%m-%d",
            },
            None,
        ),
        (
            "DISTRIBUTED_DATE_RANGE_STRATEGY",
            {
                "ranges": [
                    {
                        "start_date": "2000-01-01",
                        "end_date": "2010-12-31",
                        "distribution": 50,
                        "format": "%Y-%m-%d",
                        "output_format": "%Y-%m-%d",
                    },
                    {
                        "start_date": "2011-01-01",
                        "end_date": "2020-12-31",
                        "distribution": 50,
                        "format": "%Y-%m-%d",
                        "output_format": "%Y-%m-%d",
                    },
                ]
            },
            None,
        ),
        (
            "TIME_RANGE_STRATEGY",
            {
                "start_time": "00:00:00",
                "end_time": "23:59:59",
                "output_format": "%H:%M:%S",
            },
            None,
        ),
        (
            "DISTRIBUTED_TIME_RANGE_STRATEGY",
            {
                "ranges": [
                    {
                        "start": "00:00:00",
                        "end": "11:59:59",
                        "format": "%H:%M:%S",
                        "distribution": 50,
                    },
                    {
                        "start": "12:00:00",
                        "end": "23:59:59",
                        "format": "%H:%M:%S",
                        "distribution": 50,
                    },
                ]
            },
            None,
        ),
        ("PATTERN_STRATEGY", {"pattern": "[A-Z]{3}[0-9]{5}"}, None),
        (
            "RANDOM_NAME_STRATEGY",
            {"name_type": "first", "gender": "any", "case": "title"},
            None,
        ),
        # Limited-domain or transformation strategies: skip uniqueness check
        (
            "DISTRIBUTED_CHOICE_STRATEGY",
            {"choices": {"A": 25, "B": 25, "C": 25, "D": 25}},
            "limited-domain choices cannot guarantee 100 unique",
        ),
        ("DELETE_STRATEGY", {}, "delete strategy does not produce unique values"),
        (
            "REPLACEMENT_STRATEGY",
            {"target": "x", "value": "y"},
            "replacement cannot ensure uniqueness",
        ),
        ("CONCAT_STRATEGY", {"sources": ["a", "b"]}, "concat depends on other columns"),
    ],
)
def test_uniqueness_normal_mode(strategy_name, params, skip_reason, tmp_path):
    if skip_reason:
        pytest.skip(skip_reason)

    cfg = make_config(strategy_name, params, str(tmp_path))
    orch = DataOrchestrator(config=cfg, stream=None, batch=None, log_level="INFO")
    result = orch.run()
    assert result["status"] == "success"

    out = os.path.join(str(tmp_path), f"{strategy_name}.csv")
    assert os.path.exists(out)
    df = pd.read_csv(out)
    assert len(df) == 100
    assert df["value"].nunique(dropna=False) == 100
