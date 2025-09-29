from datetime import datetime, time

import pandas as pd
import pytest

from core.strategy_config import TimeRangeItem
from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


@pytest.fixture
def valid_ranges():
    return [
        TimeRangeItem(
            start="09:00:00", end="12:00:00", format="%H:%M:%S", distribution=50
        ),
        TimeRangeItem(
            start="13:00:00", end="17:00:00", format="%H:%M:%S", distribution=50
        ),
    ]


def test_distributed_time_range_strategy_returns_correct_number_of_items(valid_ranges):
    """
    Tests if the generate method returns a pandas Series with the correct number of items.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"ranges": valid_ranges},
    )
    count = 10
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count


def test_distributed_time_range_strategy_with_seed_produces_deterministic_results(
    valid_ranges,
):
    """
    Tests if the generate method with a seed produces deterministic results.
    """
    strategy1 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"ranges": valid_ranges, "seed": 123},
    )
    result1 = strategy1.generate_data(10)
    strategy2 = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=10,
        params={"ranges": valid_ranges, "seed": 123},
    )
    result2 = strategy2.generate_data(10)
    pd.testing.assert_series_equal(result1, result2)


def test_distributed_time_range_strategy_missing_ranges_raises_exception():
    """
    Tests if missing 'ranges' in params raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={},
        )


def test_distributed_time_range_strategy_invalid_ranges_type_raises_exception():
    """
    Tests if an invalid type for 'ranges' raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": {}},
        )


def test_distributed_time_range_strategy_empty_ranges_raises_exception():
    """
    Tests if empty 'ranges' raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": []},
        )


def test_distributed_time_range_strategy_invalid_range_item_type_raises_exception():
    """
    Tests if a non-TimeRangeItem in 'ranges' raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": [{}]},
        )


def test_distributed_time_range_strategy_missing_field_in_range_item_raises_exception():
    """
    Tests if a missing field in a TimeRangeItem raises an InvalidConfigParamException.
    """
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={
                "ranges": [
                    TimeRangeItem(start="09:00:00", end="12:00:00", format="%H:%M:%S")
                ]
            },
        )


def test_distributed_time_range_strategy_invalid_time_format_raises_exception(
    valid_ranges,
):
    """
    Tests if an invalid time format in a TimeRangeItem raises an InvalidConfigParamException.
    """
    valid_ranges[0].format = "%H-%M-%S"
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": valid_ranges},
        )


def test_distributed_time_range_strategy_invalid_distribution_type_raises_exception(
    valid_ranges,
):
    """
    Tests if a non-numeric distribution in a TimeRangeItem raises an InvalidConfigParamException.
    """
    valid_ranges[0].distribution = "50"
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": valid_ranges},
        )


def test_distributed_time_range_strategy_negative_distribution_raises_exception(
    valid_ranges,
):
    """
    Tests if a negative distribution in a TimeRangeItem raises an InvalidConfigParamException.
    """
    valid_ranges[0].distribution = -50
    valid_ranges[1].distribution = 150
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": valid_ranges},
        )


def test_distributed_time_range_strategy_distribution_not_100_raises_exception(
    valid_ranges,
):
    """
    Tests if the total distribution not equal to 100 raises an InvalidConfigParamException.
    """
    valid_ranges[0].distribution = 60
    with pytest.raises(InvalidConfigParamException):
        create_strategy_via_factory(
            mode="NORMAL",
            strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
            df=None,
            col_name="col",
            rows=1,
            params={"ranges": valid_ranges},
        )


def test_distributed_time_range_strategy_distribution(valid_ranges):
    """
    Tests if the distribution of times is approximately correct.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DISTRIBUTED_TIME_RANGE_STRATEGY",
        df=None,
        col_name="col",
        rows=1000,
        params={"ranges": valid_ranges},
    )
    count = 1000
    result = strategy.generate_data(count)

    range1_count = 0
    range2_count = 0

    start1 = time(9, 0, 0)
    end1 = time(12, 0, 0)
    start2 = time(13, 0, 0)
    end2 = time(17, 0, 0)

    for time_str in result:
        t = datetime.strptime(time_str, "%H:%M:%S").time()
        if start1 <= t <= end1:
            range1_count += 1
        elif start2 <= t <= end2:
            range2_count += 1

    assert abs(range1_count - 500) < 100
    assert abs(range2_count - 500) < 100
