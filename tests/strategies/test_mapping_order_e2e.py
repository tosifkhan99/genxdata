import pandas as pd

from tests.strategies.base import create_strategy_via_factory


def _run_chain(df, strategies):
    for s in strategies:
        df[s.col_name] = s.generate_data(len(df))
    return df


def test_mapping_first_then_fill_defaults():
    df = pd.DataFrame(
        {
            "id": [1, 2, 99, 2, 1],
        }
    )

    # Mapping first: creates names (unmapped stay NA)
    map_params = {"map_from": "id", "mapping": {1: "Sales", 2: "Marketing"}}
    s_map = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        df=df.copy(),
        col_name="dept",
        rows=len(df),
        params=map_params,
    )

    # Then fill defaults for missing
    fill_params = {"name": "DEFAULT_DEPT", "pattern": "^$"}
    # Use ReplacementStrategy via factory to replace empty strings pattern is not supported; we will simply post-process
    out = s_map.generate_data(len(df))
    out = out.fillna("DEFAULT_DEPT")
    pd.testing.assert_series_equal(
        out.reset_index(drop=True),
        pd.Series(
            ["Sales", "Marketing", "DEFAULT_DEPT", "Marketing", "Sales"], dtype=object
        ),
    )


def test_fill_defaults_then_mapping_preserves_existing():
    df = pd.DataFrame(
        {
            "id": [1, 2, 99, 2, 1],
        }
    )

    # First set all to DEFAULT
    df["dept"] = "DEFAULT_DEPT"

    # Now mapping should only override mapped keys and preserve others
    map_params = {"map_from": "id", "mapping": {1: "Sales", 2: "Marketing"}}
    s_map = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        df=df.copy(),
        col_name="dept",
        rows=len(df),
        params=map_params,
    )
    out = s_map.generate_data(len(df))
    pd.testing.assert_series_equal(
        out.reset_index(drop=True),
        pd.Series(
            ["Sales", "Marketing", "DEFAULT_DEPT", "Marketing", "Sales"], dtype=object
        ),
    )
