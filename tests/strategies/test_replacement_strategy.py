import pandas as pd
import pytest

from tests.strategies.base import create_strategy_via_factory


@pytest.fixture
def sample_df():
    return pd.DataFrame({"col1": ["A", "B", "C", "A"]})


def test_replacement_strategy_replaces_values(sample_df):
    """
    Tests if the MockReplacementStrategy correctly replaces values in a column.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="REPLACEMENT_STRATEGY",
        df=sample_df,
        col_name="col1",
        rows=4,
        params={"from_value": "A", "to_value": "Z"},
    )
    result = strategy.generate_data(4)
    expected = pd.Series(["Z", "B", "C", "Z"])
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_replacement_strategy_missing_from_value_raises_exception():
    """
    With factory defaults, missing 'from_value' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="REPLACEMENT_STRATEGY",
        df=None,
        col_name="col",
        rows=2,
        params={"to_value": "Z"},
    )
    result = strategy.generate_data(2)
    assert len(result) == 2


def test_replacement_strategy_missing_to_value_raises_exception():
    """
    With factory defaults, missing 'to_value' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="REPLACEMENT_STRATEGY",
        df=None,
        col_name="col",
        rows=2,
        params={"from_value": "A"},
    )
    result = strategy.generate_data(2)
    assert len(result) == 2


def test_replacement_strategy_no_dataframe():
    """
    Tests if the strategy returns a series of 'to_value' when no dataframe is provided.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="REPLACEMENT_STRATEGY",
        df=None,
        col_name="col",
        rows=3,
        params={"from_value": "A", "to_value": "Z"},
    )
    result = strategy.generate_data(3)
    expected = pd.Series(["Z", "Z", "Z"])
    pd.testing.assert_series_equal(result, expected)


def test_replacement_strategy_no_column_in_dataframe(sample_df):
    """
    Tests if the strategy returns a series of 'to_value' when the column is not in the dataframe.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="REPLACEMENT_STRATEGY",
        df=sample_df,
        col_name="col2",
        rows=3,
        params={"from_value": "A", "to_value": "Z"},
    )
    result = strategy.generate_data(3)
    expected = pd.Series(["Z", "Z", "Z"])
    pd.testing.assert_series_equal(result, expected)
