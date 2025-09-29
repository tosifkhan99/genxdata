import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_number_range_strategy_returns_correct_number_of_items():
    """
    Tests if the generate method returns a pandas Series with the correct number of items.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0, "end": 10},
    )
    count = 5
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_number_range_strategy_with_seed_produces_deterministic_results():
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"start": 0, "end": 10, "seed": 123},
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"start": 0, "end": 10, "seed": 123},
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_number_range_strategy_missing_start_raises_exception():
    """
    When using the factory, missing 'start' falls back to config defaults.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"end": 10},
    )
    result = strategy.generate_data(5)
    assert isinstance(result, pd.Series)
    assert len(result) == 5


def test_number_range_strategy_missing_end_raises_exception():
    """
    When using the factory, missing 'end' falls back to config defaults.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0},
    )
    result = strategy.generate_data(5)
    assert isinstance(result, pd.Series)
    assert len(result) == 5


def test_number_range_strategy_invalid_bounds_raises_exception():
    """
    Tests if start >= end in params raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=10,
            params={"start": 10, "end": 0},
        )


def test_number_range_strategy_integer_range():
    """
    Tests if the strategy generates integers when start and end are integers.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0, "end": 10},
    )
    result = strategy.generate_data(5)
    assert all(isinstance(x, int) for x in result)


def test_number_range_strategy_float_range():
    """
    Tests if the strategy generates floats when start or end is a float.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start": 0.0, "end": 10},
    )
    result = strategy.generate_data(5)
    assert all(isinstance(x, float) for x in result)
