import pandas as pd
import pytest

from tests.strategies.base import create_strategy_via_factory


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"first_name": ["John", "Jane", "Peter"], "last_name": ["Doe", "Doe", "Jones"]}
    )


def test_concat_strategy_concatenates_columns(sample_df):
    """
    Tests if the MockConcatStrategy correctly concatenates two columns.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="CONCAT_STRATEGY",
        df=sample_df,
        col_name="out",
        rows=len(sample_df),
        params={"lhs_col": "first_name", "rhs_col": "last_name", "separator": " "},
    )
    result = strategy.generate_data(3)
    expected = pd.Series(["John Doe", "Jane Doe", "Peter Jones"])
    pd.testing.assert_series_equal(result, expected)


def test_concat_strategy_with_prefix_and_suffix(sample_df):
    """
    Tests if the MockConcatStrategy correctly adds a prefix and suffix.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="CONCAT_STRATEGY",
        df=sample_df,
        col_name="out",
        rows=len(sample_df),
        params={
            "lhs_col": "first_name",
            "rhs_col": "last_name",
            "separator": " ",
            "prefix": "Name: ",
            "suffix": ".",
        },
    )
    result = strategy.generate_data(3)
    expected = pd.Series(["Name: John Doe.", "Name: Jane Doe.", "Name: Peter Jones."])
    pd.testing.assert_series_equal(result, expected)


def test_concat_strategy_missing_lhs_col_uses_rhs_only():
    """
    With factory defaults, missing lhs_col is allowed if rhs_col present.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="CONCAT_STRATEGY",
        df=None,
        col_name="out",
        rows=3,
        params={"rhs_col": "last_name"},
    )
    result = strategy.generate_data(3)
    assert len(result) == 3


def test_concat_strategy_missing_rhs_col_uses_lhs_only():
    """
    With factory defaults, missing rhs_col is allowed if lhs_col present.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="CONCAT_STRATEGY",
        df=None,
        col_name="out",
        rows=3,
        params={"lhs_col": "first_name"},
    )
    result = strategy.generate_data(3)
    print("--------------------------------")
    print(result)
    assert len(result) == 3


def test_concat_strategy_with_non_string_columns(sample_df):
    """
    Tests if the MockConcatStrategy correctly handles non-string columns.
    """
    sample_df["number"] = [1, 2, 3]
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="CONCAT_STRATEGY",
        df=sample_df,
        col_name="out",
        rows=len(sample_df),
        params={"lhs_col": "first_name", "rhs_col": "number", "separator": "-"},
    )
    result = strategy.generate_data(3)
    expected = pd.Series(["John-1", "Jane-2", "Peter-3"])
    pd.testing.assert_series_equal(result, expected)


def test_concat_strategy_with_no_dataframe():
    """
    Tests if the MockConcatStrategy handles the case where no dataframe is provided.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="CONCAT_STRATEGY",
        df=None,
        col_name="out",
        rows=3,
        params={
            "lhs_col": "first_name",
            "rhs_col": "last_name",
            "separator": " ",
            "prefix": "Name: ",
            "suffix": ".",
        },
    )
    result = strategy.generate_data(3)
    expected = pd.Series(["Name:  .", "Name:  .", "Name:  ."])
    pd.testing.assert_series_equal(result, expected)
