from datetime import datetime

import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_date_generator_strategy_returns_correct_number_of_dates():
    """
    Tests if the generate method returns a pandas Series with the correct number of dates.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DATE_GENERATOR_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "format": "%Y-%m-%d",
        },
    )
    count = 10
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_date_generator_strategy_with_seed_produces_deterministic_results():
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DATE_GENERATOR_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "format": "%Y-%m-%d",
            "seed": 123,
        },
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DATE_GENERATOR_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "format": "%Y-%m-%d",
            "seed": 123,
        },
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_date_generator_strategy_missing_start_date_uses_default():
    """
    With factory defaults, missing 'start_date' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DATE_GENERATOR_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"end_date": "2022-12-31", "format": "%Y-%m-%d"},
    )
    result = strategy.generate_data(5)
    assert len(result) == 5


def test_date_generator_strategy_missing_end_date_uses_default():
    """
    With factory defaults, missing 'end_date' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DATE_GENERATOR_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={
            "start_date": "2022-01-01",
            "format": "%Y-%m-%d",
            "end_date": "2022-12-31",
        },
    )
    result = strategy.generate_data(5)
    assert len(result) == 5


def test_date_generator_strategy_invalid_date_format_raises_exception():
    """
    Tests if an invalid date format raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DATE_GENERATOR_STRATEGY",
            df=None,
            col_name="col",
            rows=5,
            params={
                "start_date": "2022-01-01",
                "end_date": "2022-12-31",
                "format": "kkkf",
                "input_format": "%Y-%m-%d",
            },
        )


def test_date_generator_strategy_output_format():
    """
    Tests the output format of the generated dates.
    """
    output_format = "%d-%m-%Y"
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DATE_GENERATOR_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "format": "%Y-%m-%d",
            "output_format": output_format,
        },
    )
    result = strategy.generate_data(5)
    for date_str in result:
        try:
            datetime.strptime(date_str, output_format)
        except ValueError:
            pytest.fail(f"Date {date_str} does not match format {output_format}")
