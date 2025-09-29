"""
Mapping between strategy names, strategy classes, and configuration classes.

Provides helpers to list all strategies and to resolve a strategy or config
class from its string identifier. Raises `UnsupportedStrategyException` for
unknown names.
"""

from typing import Any

from core.base_strategy import BaseStrategy
from core.strategies.concat_strategy import ConcatStrategy
from core.strategies.date_series_strategy import DateSeriesStrategy
from core.strategies.delete_strategy import DeleteStrategy
from core.strategies.distributed_choice_strategy import DistributedChoiceStrategy
from core.strategies.distributed_date_range_strategy import DistributedDateRangeStrategy
from core.strategies.distributed_number_range_strategy import (
    DistributedNumberRangeStrategy,
)
from core.strategies.distributed_time_range_strategy import DistributedTimeRangeStrategy
from core.strategies.mapping_strategy import MappingStrategy
from core.strategies.pattern_strategy import PatternStrategy
from core.strategies.random_date_range_strategy import RandomDateRangeStrategy
from core.strategies.random_name_strategy import RandomNameStrategy
from core.strategies.random_number_range_strategy import RandomNumberRangeStrategy
from core.strategies.replacement_strategy import ReplacementStrategy
from core.strategies.series_strategy import SeriesStrategy
from core.strategies.time_range_strategy import TimeRangeStrategy
from core.strategies.uuid_strategy import UuidStrategy
from core.strategy_config import (
    BaseConfig,
    ConcatConfig,
    DateRangeConfig,
    DateSeriesConfig,
    DeleteConfig,
    DistributedChoiceConfig,
    DistributedDateRangeConfig,
    DistributedNumberRangeConfig,
    DistributedTimeRangeConfig,
    MappingConfig,
    PatternConfig,
    RandomNameConfig,
    RandomNumberRangeConfig,
    ReplacementConfig,
    SeriesConfig,
    TimeRangeConfig,
    UuidConfig,
)
from exceptions.strategy_exceptions import UnsupportedStrategyException

# Map strategy names to classes and their config classes
STRATEGY_MAP: dict[str, tuple[type[BaseStrategy], type[BaseConfig]]] = {
    "RANDOM_NUMBER_RANGE_STRATEGY": (
        RandomNumberRangeStrategy,
        RandomNumberRangeConfig,
    ),
    "DISTRIBUTED_NUMBER_RANGE_STRATEGY": (
        DistributedNumberRangeStrategy,
        DistributedNumberRangeConfig,
    ),
    # Backward-compatible alias for the renamed strategy
    "DATE_GENERATOR_STRATEGY": (RandomDateRangeStrategy, DateRangeConfig),
    "RANDOM_DATE_RANGE_STRATEGY": (RandomDateRangeStrategy, DateRangeConfig),
    "DATE_SERIES_STRATEGY": (DateSeriesStrategy, DateSeriesConfig),
    "DISTRIBUTED_DATE_RANGE_STRATEGY": (
        DistributedDateRangeStrategy,
        DistributedDateRangeConfig,
    ),
    "PATTERN_STRATEGY": (PatternStrategy, PatternConfig),
    "SERIES_STRATEGY": (SeriesStrategy, SeriesConfig),
    "DISTRIBUTED_CHOICE_STRATEGY": (DistributedChoiceStrategy, DistributedChoiceConfig),
    "TIME_RANGE_STRATEGY": (TimeRangeStrategy, TimeRangeConfig),
    "DISTRIBUTED_TIME_RANGE_STRATEGY": (
        DistributedTimeRangeStrategy,
        DistributedTimeRangeConfig,
    ),
    "REPLACEMENT_STRATEGY": (ReplacementStrategy, ReplacementConfig),
    "CONCAT_STRATEGY": (ConcatStrategy, ConcatConfig),
    "RANDOM_NAME_STRATEGY": (RandomNameStrategy, RandomNameConfig),
    "DELETE_STRATEGY": (
        DeleteStrategy,
        DeleteConfig,
    ),
    "MAPPING_STRATEGY": (MappingStrategy, MappingConfig),
    "UUID_STRATEGY": (UuidStrategy, UuidConfig),
}


def get_all_strategy_names() -> list[str]:
    return list(STRATEGY_MAP.keys())


def get_all_strategy_schemas() -> list[dict[str, Any]]:
    schemas = {}
    for strategy_name in get_all_strategy_names():
        schemas[strategy_name] = STRATEGY_MAP[strategy_name][1].__doc__
    return schemas


def get_strategy_class(strategy_name: str) -> type[BaseStrategy]:
    """
    Get the strategy class for the given strategy name.

    Args:
        strategy_name: Name of the strategy

    Returns:
        Strategy class

    Raises:
        UnsupportedStrategyException: If the strategy is not supported
    """
    if strategy_name not in STRATEGY_MAP:
        raise UnsupportedStrategyException(f"Unsupported strategy: {strategy_name}")

    return STRATEGY_MAP[strategy_name][0]


def get_config_class(strategy_name: str) -> type[BaseConfig]:
    """
    Get the configuration class for the given strategy name.

    Args:
        strategy_name: Name of the strategy

    Returns:
        Configuration class

    Raises:
        UnsupportedStrategyException: If the strategy is not supported
    """
    if strategy_name not in STRATEGY_MAP:
        raise UnsupportedStrategyException(f"Unsupported strategy: {strategy_name}")

    return STRATEGY_MAP[strategy_name][1]
