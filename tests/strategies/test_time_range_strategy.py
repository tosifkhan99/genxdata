from datetime import datetime, time

import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_time_range_strategy_returns_correct_number_of_items():
    """
    Tests if the generate method returns a pandas Series with the correct number of items.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={"start_time": "09:00:00", "end_time": "17:00:00"},
    )
    count = 5
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_time_range_strategy_with_seed_produces_deterministic_results():
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"start_time": "09:00:00", "end_time": "17:00:00", "seed": 123},
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"start_time": "09:00:00", "end_time": "17:00:00", "seed": 123},
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_time_range_strategy_missing_start_time_uses_default():
    """
    With factory defaults, missing 'start_time' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=2,
        params={"end_time": "17:00:00"},
    )
    result = strategy.generate_data(2)
    assert len(result) == 2


def test_time_range_strategy_missing_end_time_uses_default():
    """
    With factory defaults, missing 'end_time' falls back to default.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=2,
        params={"start_time": "09:00:00"},
    )
    result = strategy.generate_data(2)
    assert len(result) == 2


def test_time_range_strategy_invalid_time_format_raises_exception():
    """
    Tests if an invalid time format raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={
                "start_time": "09-00-00",
                "end_time": "17-00-00",
                "input_format": "%H:%M:%S",
            },
        )


def test_time_range_strategy_via_factory_output_format():
    """
    Tests the output format of the generated times.
    """
    output_format = "%I:%M:%S %p"
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "output_format": output_format,
        },
    )
    result = strategy.generate_data(5)
    for time_str in result:
        try:
            datetime.strptime(time_str, output_format)
        except ValueError:
            pytest.fail(f"Time {time_str} does not match format {output_format}")


def test_time_range_strategy_via_factory_overnight_range():
    """
    Tests the strategy with an overnight time range.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"start_time": "22:00:00", "end_time": "06:00:00"},
    )
    result = strategy.generate_data(10)
    for time_str in result:
        t = datetime.strptime(time_str, "%H:%M:%S").time()
        assert (t >= time(22, 0, 0)) or (t <= time(6, 0, 0))
