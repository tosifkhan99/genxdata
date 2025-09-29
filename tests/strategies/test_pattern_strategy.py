import re

import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


class MockPatternStrategy:
    pass


def test_pattern_strategy_returns_correct_number_of_items():
    """
    Tests if the generate method returns a pandas Series with the correct number of items.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="PATTERN_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"regex": "[A-Z]{5}"},
    )
    count = 5
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_pattern_strategy_with_seed_produces_deterministic_results():
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="PATTERN_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"regex": "[A-Z]{5}", "seed": 123},
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="PATTERN_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"regex": "[A-Z]{5}", "seed": 123},
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_pattern_strategy_missing_regex_uses_default():
    """
    With factory defaults, missing 'regex' falls back to a default pattern.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="PATTERN_STRATEGY",
        df=None,
        col_name="col",
        rows=3,
        params={},
    )
    result = strategy.generate_data(3)
    assert len(result) == 3


def test_pattern_strategy_invalid_regex_raises_exception():
    """
    Tests if an invalid regex pattern raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="PATTERN_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"regex": "["},
        )


def test_pattern_strategy_matches_pattern():
    """
    Tests if the generated strings match the specified pattern.
    """
    pattern = r"\d{3}-\d{2}-\d{4}"
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="PATTERN_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"regex": pattern},
    )
    result = strategy.generate_data(5)
    for item in result:
        assert re.match(pattern, item)


def test_pattern_strategy_unique_values():
    """
    Tests if the strategy generates unique values when unique=True.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="PATTERN_STRATEGY",
        df=None,
        col_name="col",
        rows=3,
        params={"regex": "[A-D]{1}"},
        unique=True,
    )
    result = strategy.generate_data(3)
    print(result)
    assert len(result.unique()) == 3
