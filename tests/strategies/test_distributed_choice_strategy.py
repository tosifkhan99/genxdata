import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_distributed_choice_strategy_returns_correct_number_of_items():
    """
    Tests if the generate method returns a pandas Series with the correct number of items.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"choices": {"A": 50, "B": 50}},
    )
    count = 10
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_distributed_choice_strategy_with_seed_produces_deterministic_results():
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"choices": {"A": 50, "B": 50}, "seed": 123},
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"choices": {"A": 50, "B": 50}, "seed": 123},
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_distributed_choice_strategy_missing_choices_raises_exception():
    """
    Tests if missing 'choices' in params raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={},
        )


def test_distributed_choice_strategy_invalid_choices_type_raises_exception():
    """
    Tests if an invalid type for 'choices' raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"choices": ["A", "B"]},
        )


def test_distributed_choice_strategy_empty_choices_raises_exception():
    """
    Tests if empty 'choices' raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"choices": {}},
        )


def test_distributed_choice_strategy_invalid_weight_type_raises_exception():
    """
    Tests if a non-numeric weight raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"choices": {"A": "50", "B": 50}},
        )


def test_distributed_choice_strategy_negative_weight_raises_exception():
    """
    Tests if a negative weight raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"choices": {"A": -50, "B": 150}},
        )


def test_distributed_choice_strategy_total_weight_not_100_raises_exception():
    """
    Tests if the total weight of choices not equal to 100 raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"choices": {"A": 50, "B": 60}},
        )


def test_distributed_choice_strategy_distribution():
    """
    Tests if the distribution of choices is approximately correct.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_CHOICE_STRATEGY",
        df=None,
        col_name="col",
        rows=1000,
        params={"choices": {"A": 25, "B": 75}},
    )
    count = 1000
    result = strategy.generate_data(count)
    counts = result.value_counts()
    assert abs(counts.get("A", 0) - 250) < 50  # Allow for some variance
    assert abs(counts.get("B", 0) - 750) < 50
