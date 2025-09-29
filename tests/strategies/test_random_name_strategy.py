import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_random_name_strategy_returns_correct_number_of_names():
    """
    Tests if the generate method returns a pandas Series with the correct number of names.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NAME_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"name_type": "full", "gender": "any", "case": "title"},
    )
    count = 10
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_random_name_strategy_with_seed_produces_deterministic_results():
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NAME_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"name_type": "full", "gender": "any", "case": "title", "seed": 123},
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NAME_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"name_type": "full", "gender": "any", "case": "title", "seed": 123},
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_random_name_strategy_invalid_name_type_raises_exception():
    """
    Tests if an invalid name_type raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="RANDOM_NAME_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"name_type": "invalid", "gender": "any", "case": "title"},
        )


def test_random_name_strategy_invalid_gender_raises_exception():
    """
    Tests if an invalid gender raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="RANDOM_NAME_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"name_type": "full", "gender": "invalid", "case": "title"},
        )


def test_random_name_strategy_invalid_case_raises_exception():
    """
    Tests if an invalid case raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="RANDOM_NAME_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"name_type": "full", "gender": "any", "case": "invalid"},
        )


def test_random_name_strategy_case_formatting():
    """
    Tests the case formatting options.
    """
    strategy_upper = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NAME_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"name_type": "full", "gender": "any", "case": "upper", "seed": 42},
    )
    result_upper = strategy_upper.generate_data(5)
    assert all(name.isupper() for name in result_upper)

    strategy_lower = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NAME_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"name_type": "full", "gender": "any", "case": "lower", "seed": 42},
    )
    result_lower = strategy_lower.generate_data(5)
    assert all(name.islower() for name in result_lower)

    strategy_title = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="RANDOM_NAME_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"name_type": "full", "gender": "any", "case": "title", "seed": 42},
    )
    result_title = strategy_title.generate_data(5)
    assert all(name.istitle() for name in result_title)
