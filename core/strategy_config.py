"""
Configuration classes for strategy parameters.

Each strategy has its own configuration class that defines and validates
the parameters required for that strategy.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from typing import Any

from exceptions.param_exceptions import InvalidConfigParamException
from utils.logging import Logger


@dataclass(kw_only=True)
class BaseConfig(ABC):
    """Base configuration class for all strategies"""

    mask: str = ""

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "BaseConfig":
        """
        Create a configuration instance from a dictionary.

        Args:
            config_dict: Dictionary containing configuration parameters

        Returns:
            An instance of the configuration class
        """
        # Be resilient to None params
        if config_dict is None:
            config_dict = {}
        field_names = [f.name for f in fields(cls)]
        filtered_dict = {k: v for k, v in config_dict.items() if k in field_names}

        # Log unknown fields at debug level to avoid noisy warnings
        try:
            unknown_keys = [k for k in config_dict.keys() if k not in field_names]
            if unknown_keys:
                logger = Logger.get_logger("config")
                logger.debug(
                    f"Ignored unknown fields for {cls.__name__}: {unknown_keys}"
                )
        except Exception:
            # Do not fail config parsing due to logging issues
            pass

        return cls(**filtered_dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @abstractmethod
    def validate(self) -> None:
        """
        Validate the configuration parameters.
        Raises InvalidConfigParamException if validation fails.
        """
        pass


@dataclass
class RandomNumberRangeConfig(BaseConfig):
    """Configuration for random number range strategy."""

    start: float = 0
    end: float = 99
    step: float = 1
    precision: int = 0
    unique: bool = False

    def validate(self) -> None:
        """Validate number range parameters"""
        if self.start >= self.end:
            raise InvalidConfigParamException(
                f"start ({self.start}) must be less than end ({self.end})"
            )
        if not isinstance(self.start, (int | float)) or not isinstance(
            self.end, (int | float)
        ):
            raise InvalidConfigParamException("Bounds must be numeric values")


@dataclass
class RangeItem:
    """Single range definition with distribution weight"""

    start: int = 10
    end: int = 50
    distribution: int | None = None

    def validate(self) -> None:
        """Validate range item"""
        if self.start >= self.end:
            raise InvalidConfigParamException(
                f"start ({self.start}) must be less than end ({self.end})"
            )
        # Ensure distribution is provided and numeric
        if not isinstance(self.distribution, int | float):
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )
        if self.distribution <= 0 or self.distribution > 100:
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )


@dataclass
class DistributedNumberRangeConfig(BaseConfig):
    """Configuration for distributed number range strategy"""

    ranges: list[RangeItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "DistributedNumberRangeConfig":
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if "ranges" in config_dict:
            for range_dict in config_dict["ranges"]:
                if isinstance(range_dict, RangeItem):
                    config.ranges.append(range_dict)
                elif isinstance(range_dict, dict):
                    config.ranges.append(RangeItem(**range_dict))
                else:
                    raise InvalidConfigParamException(
                        "Each range must be a dict or RangeItem"
                    )
        return config

    def validate(self) -> None:
        """Validate distributed number range parameters"""
        if not self.ranges:
            raise InvalidConfigParamException("At least one range must be specified")

        # Validate each range
        for i, range_item in enumerate(self.ranges):
            try:
                range_item.validate()
            except InvalidConfigParamException as e:
                raise InvalidConfigParamException(
                    f"Invalid range at index {i}: {str(e)}"
                ) from e

        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )


@dataclass
class DateRangeConfig(BaseConfig):
    """Configuration for date generator strategy"""

    start_date: str = "2020-1-31"
    end_date: str = "2020-12-31"
    format: str = "%Y-%m-%d"
    output_format: str = "%Y-%m-%d"

    def validate(self) -> None:
        """Validate date range parameters"""
        from datetime import datetime

        try:
            start = datetime.strptime(self.start_date, self.format)
            end = datetime.strptime(self.end_date, self.format)

            if start >= end:
                raise InvalidConfigParamException(
                    f"Start date ({self.start_date}) must be before end date ({self.end_date})"
                )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid date format. Expected {self.format}"
                ) from e
            # Re-raise the original exception for other ValueError cases
            raise


@dataclass
class DateSeriesConfig(BaseConfig):
    """Configuration for date series strategy"""

    start_date: str = "2024-01-01"
    freq: str = "D"
    format: str = "%Y-%m-%d"
    output_format: str = "%Y-%m-%d"

    def validate(self) -> None:
        from datetime import datetime

        try:
            start = datetime.strptime(self.start_date, self.format)
        except ValueError as e:
            raise InvalidConfigParamException(
                "Invalid date format for start_date"
            ) from e


@dataclass
class PatternConfig(BaseConfig):
    """Configuration for pattern strategy"""

    regex: str = r"^[A-Za-z0-9]+$"

    def validate(self) -> None:
        """Validate pattern parameters"""
        import re

        try:
            re.compile(self.regex)
        except re.error as e:
            raise InvalidConfigParamException(
                f"Invalid regular expression: {self.regex}"
            ) from e


@dataclass
class SeriesConfig(BaseConfig):
    """Configuration for series strategy"""

    start: int = 1
    step: int = 1

    def validate(self) -> None:
        """Validate series parameters"""
        if not isinstance(self.start, (int | float)) or not isinstance(
            self.step, (int | float)
        ):
            raise InvalidConfigParamException("Start and step must be numeric values")


@dataclass
class ChoiceItem:
    """Choice with weight"""

    value: Any
    weight: int


@dataclass
class DistributedChoiceConfig(BaseConfig):
    """Configuration for distributed choice strategy"""

    choices: dict[str, int] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate distributed choice parameters"""
        if not self.choices:
            raise InvalidConfigParamException("At least one choice must be specified")

        if not isinstance(self.choices, dict):
            raise InvalidConfigParamException(
                "Choices must be provided as a dictionary of value -> weight"
            )

        # Validate weights
        total_weight = 0
        for choice, weight in self.choices.items():
            if not isinstance(weight, int | float):
                raise InvalidConfigParamException(
                    f"Weight for choice '{choice}' must be numeric, got {type(weight).__name__}"
                )
            if weight <= 0:
                raise InvalidConfigParamException(
                    f"Weight for choice '{choice}' must be positive, got {weight}"
                )
            total_weight += weight

        if total_weight != 100:
            raise InvalidConfigParamException("Total weight must be 100")


@dataclass
class TimeRangeItem:
    """Single time range definition with distribution weight"""

    start: str = "00:00:00"
    end: str = "23:59:59"
    format: str = "%H:%M:%S"
    distribution: int | None = None

    def validate(self) -> None:
        """Validate time range item"""
        from datetime import datetime

        try:
            start_time = datetime.strptime(self.start, self.format)
            end_time = datetime.strptime(self.end, self.format)

            # Special handling for overnight time ranges (e.g., 22:00:00 to 06:00:00)
            if start_time >= end_time:
                # Check if this could be an overnight range
                if (
                    self.start > self.end
                ):  # String comparison for times like "22:00:00" > "06:00:00"
                    # This is likely an overnight range, which is valid
                    pass
                else:
                    raise InvalidConfigParamException(
                        f"Start time ({self.start}) must be before end time ({self.end})"
                    )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid time format. Expected {self.format}"
                ) from e
            # Re-raise the original exception for other ValueError cases
            raise

        if not isinstance(self.distribution, int | float):
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )
        if self.distribution <= 0 or self.distribution > 100:
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )


@dataclass
class DateRangeItem:
    """Single date range definition with distribution weight"""

    start_date: str = "2020-01-01"
    end_date: str = "2020-12-31"
    format: str = "%Y-%m-%d"
    output_format: str | None = None
    distribution: int | None = None

    def validate(self) -> None:
        """Validate date range item"""
        from datetime import datetime

        try:
            start_date = datetime.strptime(self.start_date, self.format)
            end_date = datetime.strptime(self.end_date, self.format)

            if start_date >= end_date:
                raise InvalidConfigParamException(
                    f"Start date ({self.start_date}) must be before end date ({self.end_date})"
                )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid date format. Expected {self.format}"
                ) from e
            # Re-raise the original exception for other ValueError cases
            raise

        # Require a non-empty output_format
        if not isinstance(self.output_format, str) or not self.output_format.strip():
            raise InvalidConfigParamException(
                "Output format must be provided and non-empty"
            )

        if self.distribution is None:
            raise InvalidConfigParamException(
                "Distribution weight (None) must be between 1 and 100"
            )
        if not isinstance(self.distribution, int | float):
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )
        if self.distribution <= 0 or self.distribution > 100:
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )


@dataclass
class DistributedTimeRangeConfig(BaseConfig):
    """Configuration for distributed time range strategy"""

    ranges: list[TimeRangeItem] = field(default_factory=list)
    seed: int | None = None

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "DistributedTimeRangeConfig":
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if "seed" in config_dict:
            config.seed = config_dict.get("seed")
        if "ranges" in config_dict:
            for range_dict in config_dict["ranges"]:
                if isinstance(range_dict, TimeRangeItem):
                    config.ranges.append(range_dict)
                elif isinstance(range_dict, dict):
                    config.ranges.append(TimeRangeItem(**range_dict))
                else:
                    raise InvalidConfigParamException(
                        "Each time range must be a dict or TimeRangeItem"
                    )
        return config

    def validate(self) -> None:
        """Validate distributed time range parameters"""
        # Ensure ranges is a list and non-empty
        if not isinstance(self.ranges, list) or len(self.ranges) == 0:
            raise InvalidConfigParamException(
                "At least one time range must be specified"
            )

        # Validate each range
        for i, range_item in enumerate(self.ranges):
            if not isinstance(range_item, TimeRangeItem):
                raise InvalidConfigParamException(
                    f"Invalid time range at index {i}: expected TimeRangeItem, got {type(range_item).__name__}"
                )
            try:
                range_item.validate()
            except InvalidConfigParamException as e:
                raise InvalidConfigParamException(
                    f"Invalid time range at index {i}: {str(e)}"
                ) from e

        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )

        # Validate seed if provided
        if self.seed is not None:
            try:
                int(self.seed)
            except (TypeError, ValueError) as e:
                raise InvalidConfigParamException("Seed must be an integer") from e


@dataclass
class DistributedDateRangeConfig(BaseConfig):
    """Configuration for distributed date range strategy"""

    ranges: list[DateRangeItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "DistributedDateRangeConfig":
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if "ranges" in config_dict:
            for range_dict in config_dict["ranges"]:
                if isinstance(range_dict, DateRangeItem):
                    config.ranges.append(range_dict)
                elif isinstance(range_dict, dict):
                    config.ranges.append(DateRangeItem(**range_dict))
                else:
                    raise InvalidConfigParamException(
                        "Each date range must be a dict or DateRangeItem"
                    )
        return config

    def validate(self) -> None:
        """Validate distributed date range parameters"""
        if not self.ranges:
            raise InvalidConfigParamException(
                "At least one date range must be specified"
            )

        # Validate each range
        for i, range_item in enumerate(self.ranges):
            try:
                range_item.validate()
            except InvalidConfigParamException as e:
                raise InvalidConfigParamException(
                    f"Invalid date range at index {i}: {str(e)}"
                ) from e

        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )


@dataclass
class TimeRangeConfig(BaseConfig):
    """Configuration for time range strategy"""

    start_time: str = "00:00:00"
    end_time: str = "23:59:59"
    format: str = "%H:%M:%S"

    def validate(self) -> None:
        """Validate time range parameters"""
        from datetime import datetime

        try:
            start = datetime.strptime(self.start_time, self.format)
            end = datetime.strptime(self.end_time, self.format)

            if start >= end:
                # Allow overnight ranges when the start string is lexicographically after end
                if self.start_time > self.end_time:
                    # Overnight range is valid
                    pass
                else:
                    raise InvalidConfigParamException(
                        f"Start time ({self.start_time}) must be before end time ({self.end_time})"
                    )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid time format. Expected {self.format}"
                ) from e
            # Re-raise the original exception for other ValueError cases
            raise


@dataclass
class ReplacementConfig(BaseConfig):
    """Configuration for replacement strategy"""

    from_value: Any = "a"
    to_value: Any = "b"

    def validate(self) -> None:
        """Validate replacement parameters"""
        # No specific validation needed
        pass


@dataclass
class ConcatConfig(BaseConfig):
    """Configuration for concatenation strategy"""

    lhs_col: str = ""
    rhs_col: str = ""
    separator: str = ""
    suffix: str = ""
    prefix: str = ""

    def validate(self) -> None:
        """Validate concatenation parameters"""
        if not self.lhs_col and not self.rhs_col:
            raise InvalidConfigParamException(
                "At least one column must be specified for concatenation"
            )


@dataclass
class MappingConfig(BaseConfig):
    """Configuration for mapping strategy"""

    source: str = ""
    source_column: str = ""
    source_map_from: str = ""
    map_from: str = ""
    mapping: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        # map_from is required
        if not isinstance(self.map_from, str) or not self.map_from.strip():
            raise InvalidConfigParamException("'map_from' must be provided")

        has_inline = isinstance(self.mapping, dict) and len(self.mapping) > 0
        has_file = bool(self.source) and bool(self.source_column)

        if has_file:
            if not os.path.isfile(self.source):
                raise InvalidConfigParamException(
                    f"Source file '{self.source}' does not exist"
                )

        if has_inline and has_file:
            raise InvalidConfigParamException(
                "Provide either 'mapping' (inline) or ('source' and 'source_column'), not both"
            )

        if has_inline:
            return

        if has_file:
            return

        # Neither inline nor file configuration provided
        raise InvalidConfigParamException(
            "Provide 'mapping' dict or ('source' and 'source_column') for file mapping"
        )


@dataclass
class DeleteConfig(BaseConfig):
    def validate(self) -> None:
        # Delete strategy has no params; mask is now provided at top-level config
        return


@dataclass
class RandomNameConfig(BaseConfig):
    """Configuration for random name generation strategy"""

    name_type: str = "first"  # 'first', 'last', or 'full'
    gender: str = "any"  # 'male', 'female', or 'any'
    case: str = "title"  # 'title', 'upper', or 'lower'

    def validate(self) -> None:
        """Validate random name parameters"""
        valid_name_types = ["first", "last", "full"]
        if self.name_type not in valid_name_types:
            raise InvalidConfigParamException(
                f"Invalid name_type: {self.name_type}. Must be one of {valid_name_types}"
            )

        valid_genders = ["male", "female", "any"]
        if self.gender not in valid_genders:
            raise InvalidConfigParamException(
                f"Invalid gender: {self.gender}. Must be one of {valid_genders}"
            )

        valid_cases = ["title", "upper", "lower"]
        if self.case not in valid_cases:
            raise InvalidConfigParamException(
                f"Invalid case: {self.case}. Must be one of {valid_cases}"
            )


# Example: config_class = get_config_class(strategy_name); config = config_class.from_dict(params)


@dataclass
class UuidConfig(BaseConfig):
    """Configuration for UUID strategy"""

    hyphens: bool = True
    uppercase: bool = False
    prefix: str = ""
    unique: bool = False
    numbers_only: bool = False
    version: int = 5

    def validate(self) -> None:
        # All fields are simple types; nothing complex to validate
        if not isinstance(self.hyphens, bool) or not isinstance(self.uppercase, bool):
            raise InvalidConfigParamException(
                "'hyphens' and 'uppercase' must be booleans"
            )
        if not isinstance(self.numbers_only, bool):
            raise InvalidConfigParamException("'numbers_only' must be a boolean")
        if not isinstance(self.prefix, str):
            raise InvalidConfigParamException("'prefix' must be a string")

        # Version must be 4 or 5
        if self.version not in (4, 5):
            raise InvalidConfigParamException("'version' must be 4 or 5")
