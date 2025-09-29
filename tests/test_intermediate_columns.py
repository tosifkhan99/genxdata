import pandas as pd

from utils.intermediate_column import (
    mark_as_intermediate,
    get_intermediate_columns,
    filter_intermediate_columns,
    compute_dependency_columns,
)


def test_mark_and_filter_intermediate_columns():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df = mark_as_intermediate(df, "b")
    assert "b" in get_intermediate_columns(df)

    filtered = filter_intermediate_columns(df)
    assert "b" not in filtered.columns
    assert "a" in filtered.columns


def test_compute_dependency_columns_from_mask_and_params():
    config = {
        "column_name": ["x", "y", "z"],
        "configs": [
            {"mask": "x > 0", "column_names": ["y"], "strategy": {"name": "SERIES_STRATEGY", "params": {"start": 1, "step": 1}}},
            {"column_names": ["z"], "strategy": {"name": "CONCAT_STRATEGY", "params": {"lhs_col": "x", "rhs_col": "y"}}},
        ],
    }
    deps = compute_dependency_columns(config)
    # x is referenced in mask and in concat params
    assert "x" in deps

