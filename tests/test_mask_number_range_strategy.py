import pandas as pd

from tests.strategies.base import create_strategy_via_factory


class MockNumberRangeStrategy:
    pass


def _make_df():
    return pd.DataFrame(
        {
            "A": ["value1", "value 1", "value2", "other", "value1"],
            "B": ["value2", "value2", "zzz", "value2", "nope"],
            "numericA": [0, 1, 2, 3, 4],
            "numericB": [9, 8, 7, 6, 5],
            "flag": [True, False, True, False, True],
        }
    )


def _new_strategy(df: pd.DataFrame):
    return create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=df.copy(),
        col_name="out",
        rows=len(df),
        params={"start": 100, "end": 200},
        intermediate=False,
        unique=False,
        strategy_state={},
    )


def _assert_mask_applied(df: pd.DataFrame, mask_expr: str):
    # Rows matching mask should have non-null in out; others should remain null
    matched_idx = df.query(mask_expr).index
    assert df.loc[matched_idx, "out"].notna().all()
    remaining = df.index.difference(matched_idx)
    if len(remaining) > 0:
        assert df.loc[remaining, "out"].isna().all()


def test_mask_eq_string():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "A == 'value1'")
    _assert_mask_applied(out, "A == 'value1'")


def test_mask_eq_multiple_conditions():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "A == 'value 1' & B == 'value2'")
    _assert_mask_applied(out, "A == 'value 1' & B == 'value2'")


def test_mask_neq_string():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "A != 'value1'")
    _assert_mask_applied(out, "A != 'value1'")


def test_mask_lt_numeric():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "numericA < 1")
    _assert_mask_applied(out, "numericA < 1")


def test_mask_gt_numeric():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "numericA > 1")
    _assert_mask_applied(out, "numericA > 1")


def test_mask_mixed_numeric_conditions():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "numericA > 1 & numericB < 9")
    _assert_mask_applied(out, "numericA > 1 & numericB < 9")


def test_mask_boolean_direct():
    df = _make_df()
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "flag")
    _assert_mask_applied(out, "flag == True")


def test_mask_datetime_range():
    df = _make_df()
    # Add a datetime column
    df = df.copy()
    df["date"] = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ]
    )
    s = _new_strategy(df)
    out = s.apply_to_dataframe(df, "out", "date >= '2024-01-02'  & date < '2024-01-04'")
    matched_idx = df.query("date >= '2024-01-02'  & date < '2024-01-04'").index
    assert out.loc[matched_idx, "out"].notna().all()
    remaining = df.index.difference(matched_idx)
    if len(remaining) > 0:
        assert out.loc[remaining, "out"].isna().all()
