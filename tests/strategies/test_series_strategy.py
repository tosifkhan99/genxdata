import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_series_strategy_returns_correct_number_of_items():
    """
    Tests if the generate method returns a pandas Series with the correct number of items.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="SERIES_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0, "step": 1},
    )
    count = 5
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_series_strategy_integer_series():
    """
    Tests if the strategy generates a correct integer series.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="SERIES_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0, "step": 2},
    )
    result = strategy.generate_data(5)
    expected = pd.Series([0, 2, 4, 6, 8])
    pd.testing.assert_series_equal(result, expected, check_dtype=False)


def test_series_strategy_float_series():
    """
    Tests if the strategy generates a correct float series.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="SERIES_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0.5, "step": 0.5},
    )
    result = strategy.generate_data(5)
    expected = pd.Series([0.5, 1.0, 1.5, 2.0, 2.5])
    pd.testing.assert_series_equal(result, expected, check_dtype=False)


def test_series_strategy_missing_start_uses_default():
    """
    With factory defaults, missing 'start' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="SERIES_STRATEGY",
        df=None,
        col_name="col",
        rows=2,
        params={"step": 1},
    )
    result = strategy.generate_data(2)
    assert len(result) == 2


def test_series_strategy_invalid_start_type_raises_exception():
    """
    Tests if a non-numeric 'start' value raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="SERIES_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"start": "a", "step": 1},
        )


def test_series_strategy_invalid_step_type_raises_exception():
    """
    Tests if a non-numeric 'step' value raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="SERIES_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"start": 0, "step": "a"},
        )


def test_series_strategy_stateful_generation():
    """
    Tests the stateful generation of the series strategy.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="SERIES_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0, "step": 1},
    )
    result1 = strategy.generate_chunk(5)
    expected1 = pd.Series([0, 1, 2, 3, 4])
    pd.testing.assert_series_equal(result1, expected1, check_dtype=False)

    result2 = strategy.generate_chunk(5)
    expected2 = pd.Series([5, 6, 7, 8, 9])
    pd.testing.assert_series_equal(result2, expected2, check_dtype=False)
