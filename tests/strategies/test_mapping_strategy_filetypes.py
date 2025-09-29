import pandas as pd

from tests.strategies.base import create_strategy_via_factory


def _assert_mapping(tmp_path, df, mapping_df, ext, read_kwargs=None):
    path = tmp_path / f"mapping{ext}"
    if ext == ".csv":
        mapping_df.to_csv(path, index=False)
    elif ext == ".json":
        mapping_df.to_json(path, orient="records")
    elif ext == ".parquet":
        mapping_df.to_parquet(path, index=False)
    elif ext in (".xlsx", ".xls"):
        mapping_df.to_excel(path, index=False)
    else:
        raise AssertionError("Unsupported ext in test")

    params = {
        "map_from": "id",
        "source_map_from": "key",
        "source": str(path),
        "source_column": "val",
    }
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        df=df.copy(),
        col_name="name",
        rows=len(df),
        params=params,
    )
    out = s.generate_data(len(df)).reset_index(drop=True)
    expected = pd.Series(["A", "B", "DEFAULT", "B"], dtype=object)
    pd.testing.assert_series_equal(out, expected)


def test_mapping_from_csv(tmp_path):
    df = pd.DataFrame({"id": [1, 2, 99, 2], "name": ["DEFAULT"] * 4})
    mapping_df = pd.DataFrame({"key": [1, 2], "val": ["A", "B"]})
    _assert_mapping(tmp_path, df, mapping_df, ".csv")


def test_mapping_from_json(tmp_path):
    df = pd.DataFrame({"id": [1, 2, 99, 2], "name": ["DEFAULT"] * 4})
    mapping_df = pd.DataFrame({"key": [1, 2], "val": ["A", "B"]})
    _assert_mapping(tmp_path, df, mapping_df, ".json")


def test_mapping_from_parquet(tmp_path):
    df = pd.DataFrame({"id": [1, 2, 99, 2], "name": ["DEFAULT"] * 4})
    mapping_df = pd.DataFrame({"key": [1, 2], "val": ["A", "B"]})
    _assert_mapping(tmp_path, df, mapping_df, ".parquet")


def test_mapping_from_excel(tmp_path):
    df = pd.DataFrame({"id": [1, 2, 99, 2], "name": ["DEFAULT"] * 4})
    mapping_df = pd.DataFrame({"key": [1, 2], "val": ["A", "B"]})
    _assert_mapping(tmp_path, df, mapping_df, ".xlsx")
