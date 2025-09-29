"""
Domain-specific mixins for different data types.

This module provides specialized mixins for numeric, datetime, and text data
generation strategies, offering common validation patterns and utilities.
"""

import re
from datetime import datetime
from typing import Any

from exceptions.param_exceptions import InvalidConfigParamException


class NumericMixin:
    """
    Mixin for strategies that generate numeric data.

    Provides common validation and utilities for numeric data generation,
    including range validation, type checking, and numeric constraints.

    Features:
    - Range validation (min/max values)
    - Integer vs float type handling
    - Precision and scale validation
    - Distribution parameter validation

    Usage:
        class MyNumericStrategy(BaseStrategy, NumericMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._validate_numeric_params()

            def _validate_params(self):
                # Use NumericMixin for common numeric validation
                self._validate_numeric_params()
                # Add strategy-specific validation
                self._validate_distribution_params()
    """

    def _validate_numeric_params(self) -> None:
        """
        Validate common numeric parameters.

        Validates:
        - min_value and max_value ranges
        - data_type (integer/float)
        - precision and scale constraints
        """
        # Validate required range parameters
        if "min_value" not in self.params or "max_value" not in self.params:
            raise InvalidConfigParamException(
                "Numeric strategies require 'min_value' and 'max_value' parameters"
            )

        min_val = self.params["min_value"]
        max_val = self.params["max_value"]

        # Validate that min is less than max
        if min_val >= max_val:
            raise InvalidConfigParamException(
                f"min_value ({min_val}) must be less than max_value ({max_val})"
            )

        # Validate data type
        if "data_type" in self.params:
            valid_types = ["integer", "int", "float", "decimal"]
            if self.params["data_type"] not in valid_types:
                raise InvalidConfigParamException(
                    f"data_type must be one of {valid_types}, "
                    f"got '{self.params['data_type']}'"
                )

        # Validate precision for decimal types
        if "precision" in self.params:
            precision = self.params["precision"]
            if not isinstance(precision, int) or precision <= 0:
                raise InvalidConfigParamException(
                    "precision must be a positive integer"
                )

        # Validate scale for decimal types
        if "scale" in self.params:
            scale = self.params["scale"]
            if not isinstance(scale, int) or scale < 0:
                raise InvalidConfigParamException(
                    "scale must be a non-negative integer"
                )

            # Ensure scale doesn't exceed precision
            if "precision" in self.params and scale > self.params["precision"]:
                raise InvalidConfigParamException("scale cannot exceed precision")

    def _get_numeric_constraints(self) -> dict[str, Any]:
        """
        Get validated numeric constraints.

        Returns:
            Dictionary with validated min_value, max_value, and type information
        """
        return {
            "min_value": self.params["min_value"],
            "max_value": self.params["max_value"],
            "data_type": self.params.get("data_type", "float"),
            "precision": self.params.get("precision", 10),
            "scale": self.params.get("scale", 2),
        }

    def _validate_distribution_params(self, distribution: str = "uniform") -> None:
        """
        Validate distribution-specific parameters.

        Args:
            distribution: Type of distribution ('uniform', 'normal', 'exponential', etc.)
        """
        if distribution == "normal":
            if "mean" not in self.params:
                self.params["mean"] = (
                    self.params["min_value"] + self.params["max_value"]
                ) / 2
            if "std" not in self.params:
                self.params["std"] = (
                    self.params["max_value"] - self.params["min_value"]
                ) / 6

        elif distribution == "exponential":
            if "rate" not in self.params:
                self.params["rate"] = 1.0

        # Validate numeric distribution parameters
        for param in ["mean", "std", "rate", "lambda"]:
            if param in self.params and not isinstance(
                self.params[param], int | float
            ):
                raise InvalidConfigParamException(f"{param} must be a number")


class DateTimeMixin:
    """
    Mixin for strategies that generate datetime data.

    Provides common validation and utilities for datetime data generation,
    including date range validation, format checking, and timezone handling.

    Features:
    - Date range validation
    - Format string validation
    - Timezone support
    - Business day filtering
    - Holiday exclusion

    Usage:
        class MyDateTimeStrategy(BaseStrategy, DateTimeMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._validate_datetime_params()

            def _validate_params(self):
                # Use DateTimeMixin for common datetime validation
                self._validate_datetime_params()
                # Add strategy-specific validation
                self._validate_business_rules()
    """

    def _validate_datetime_params(self) -> None:
        """
        Validate common datetime parameters.

        Validates:
        - start_date and end_date presence and format
        - date format strings
        - timezone information
        - business day constraints
        """
        # Validate required date parameters
        if "start_date" not in self.params or "end_date" not in self.params:
            raise InvalidConfigParamException(
                "DateTime strategies require 'start_date' and 'end_date' parameters"
            )

        # Validate date formats
        self._validate_date_format(self.params["start_date"], "start_date")
        self._validate_date_format(self.params["end_date"], "end_date")

        # Validate that start is before end
        start = self._parse_date(self.params["start_date"])
        end = self._parse_date(self.params["end_date"])

        if start >= end:
            raise InvalidConfigParamException(
                f"start_date ({self.params['start_date']}) must be before "
                f"end_date ({self.params['end_date']})"
            )

        # Validate input format if provided
        if "input_format" in self.params:
            try:
                datetime.strptime(
                    self.params["start_date"], self.params["input_format"]
                )
                datetime.strptime(self.params["end_date"], self.params["input_format"])
            except ValueError as e:
                raise InvalidConfigParamException(f"Invalid date format: {e}") from e

        # Validate business day parameters
        if "business_days_only" in self.params:
            if not isinstance(self.params["business_days_only"], bool):
                raise InvalidConfigParamException(
                    "business_days_only must be a boolean"
                )

        # Validate weekday constraints
        if "weekdays_only" in self.params:
            if not isinstance(self.params["weekdays_only"], bool):
                raise InvalidConfigParamException("weekdays_only must be a boolean")

    def _validate_date_format(self, date_str: str, param_name: str) -> None:
        """
        Validate that a date string can be parsed.

        Args:
            date_str: Date string to validate
            param_name: Name of the parameter for error messages
        """
        try:
            # Try multiple common formats
            formats = [
                "%Y-%m-%d",  # 2023-12-25
                "%Y-%m-%d %H:%M:%S",  # 2023-12-25 15:30:00
                "%Y/%m/%d",  # 2023/12/25
                "%m/%d/%Y",  # 12/25/2023
                "%d/%m/%Y",  # 25/12/2023
                "%Y%m%d",  # 20231225
            ]

            parsed = False
            for fmt in formats:
                try:
                    datetime.strptime(date_str, fmt)
                    parsed = True
                    break
                except ValueError:
                    continue

            if not parsed:
                raise InvalidConfigParamException(
                    f"Unable to parse {param_name} '{date_str}'. "
                    f"Try formats like: YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY"
                )

        except Exception as e:
            raise InvalidConfigParamException(
                f"Invalid {param_name} '{date_str}': {e}"
            ) from e

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse a date string into a datetime object.

        Args:
            date_str: Date string to parse

        Returns:
            Parsed datetime object
        """
        # Try multiple formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y%m%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise InvalidConfigParamException(f"Unable to parse date: {date_str}")

    def _get_datetime_constraints(self) -> dict[str, Any]:
        """
        Get validated datetime constraints.

        Returns:
            Dictionary with validated start_date, end_date, and constraints
        """
        return {
            "start_date": self.params["start_date"],
            "end_date": self.params["end_date"],
            "input_format": self.params.get("input_format", "%Y-%m-%d"),
            "business_days_only": self.params.get("business_days_only", False),
            "weekdays_only": self.params.get("weekdays_only", False),
            "timezone": self.params.get("timezone", "UTC"),
        }


class TextMixin:
    """
    Mixin for strategies that generate text data.

    Provides common validation and utilities for text data generation,
    including pattern validation, length constraints, character set validation,
    and text transformation utilities.

    Features:
    - Pattern/regex validation
    - Length constraints
    - Character set validation
    - Case transformation
    - Text encoding validation

    Usage:
        class MyTextStrategy(BaseStrategy, TextMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._validate_text_params()

            def _validate_params(self):
                # Use TextMixin for common text validation
                self._validate_text_params()
                # Add strategy-specific validation
                self._validate_custom_patterns()
    """

    def _validate_text_params(self) -> None:
        """
        Validate common text parameters.

        Validates:
        - regex patterns
        - length constraints
        - character sets
        - case transformation options
        """
        # Validate regex pattern if provided
        if "regex" in self.params:
            try:
                re.compile(self.params["regex"])
            except re.error as e:
                raise InvalidConfigParamException(
                    f"Invalid regex pattern '{self.params['regex']}': {e}"
                ) from e

        # Validate length constraints
        if "min_length" in self.params:
            if (
                not isinstance(self.params["min_length"], int)
                or self.params["min_length"] < 0
            ):
                raise InvalidConfigParamException(
                    "min_length must be a non-negative integer"
                )

        if "max_length" in self.params:
            if (
                not isinstance(self.params["max_length"], int)
                or self.params["max_length"] < 1
            ):
                raise InvalidConfigParamException(
                    "max_length must be a positive integer"
                )

        # Validate length relationship
        if "min_length" in self.params and "max_length" in self.params:
            if self.params["min_length"] >= self.params["max_length"]:
                raise InvalidConfigParamException(
                    "min_length must be less than max_length"
                )

        # Validate case options
        if "case" in self.params:
            valid_cases = ["upper", "lower", "title", "mixed", "random"]
            if self.params["case"] not in valid_cases:
                raise InvalidConfigParamException(
                    f"case must be one of {valid_cases}, got '{self.params['case']}'"
                )

        # Validate charset if provided
        if "charset" in self.params:
            if not isinstance(self.params["charset"], str):
                raise InvalidConfigParamException("charset must be a string")

            # Validate charset contains valid characters
            if len(self.params["charset"]) == 0:
                raise InvalidConfigParamException("charset cannot be empty")

        # Validate encoding
        if "encoding" in self.params:
            valid_encodings = ["utf-8", "ascii", "latin1", "cp1252"]
            if self.params["encoding"] not in valid_encodings:
                raise InvalidConfigParamException(
                    f"encoding must be one of {valid_encodings}, "
                    f"got '{self.params['encoding']}'"
                )

    def _get_text_constraints(self) -> dict[str, Any]:
        """
        Get validated text constraints.

        Returns:
            Dictionary with validated text generation constraints
        """
        return {
            "regex": self.params.get("regex"),
            "min_length": self.params.get("min_length", 1),
            "max_length": self.params.get("max_length", 100),
            "case": self.params.get("case", "mixed"),
            "charset": self.params.get("charset", "abcdefghijklmnopqrstuvwxyz"),
            "encoding": self.params.get("encoding", "utf-8"),
        }

    def _validate_pattern_complexity(self, pattern: str) -> dict[str, Any]:
        """
        Analyze pattern complexity and provide recommendations.

        Args:
            pattern: Regex pattern to analyze

        Returns:
            Dictionary with complexity metrics and recommendations
        """
        analysis = {
            "complexity_score": 0,
            "estimated_generation_time": "fast",
            "recommendations": [],
        }

        # Simple complexity analysis
        if len(pattern) > 50:
            analysis["complexity_score"] += 2
            analysis["recommendations"].append("Consider simplifying the pattern")

        if "*" in pattern or "+" in pattern:
            analysis["complexity_score"] += 1
            analysis["recommendations"].append(
                "Pattern contains repetition - may be slow"
            )

        if analysis["complexity_score"] > 2:
            analysis["estimated_generation_time"] = "slow"
            analysis["recommendations"].append(
                "Consider using a simpler pattern for better performance"
            )

        return analysis


class CategoricalMixin:
    """
    Mixin for strategies that generate categorical data.

    Provides common validation and utilities for categorical data generation,
    including category validation, weight distribution, and sampling methods.

    Features:
    - Category validation and normalization
    - Weight distribution validation
    - Sampling method selection
    - Category replacement and mapping

    Usage:
        class MyCategoricalStrategy(BaseStrategy, CategoricalMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._validate_categorical_params()

            def _validate_params(self):
                # Use CategoricalMixin for common categorical validation
                self._validate_categorical_params()
                # Add strategy-specific validation
                self._validate_category_mappings()
    """

    def _validate_categorical_params(self) -> None:
        """
        Validate common categorical parameters.

        Validates:
        - categories list
        - weights distribution
        - sampling method
        - category mappings
        """
        # Validate categories
        if "categories" not in self.params:
            raise InvalidConfigParamException(
                "Categorical strategies require 'categories' parameter"
            )

        categories = self.params["categories"]
        if not isinstance(categories, list) or len(categories) == 0:
            raise InvalidConfigParamException("categories must be a non-empty list")

        # Remove duplicates while preserving order
        unique_categories = []
        seen = set()
        for cat in categories:
            if cat not in seen:
                unique_categories.append(cat)
                seen.add(cat)
        self.params["categories"] = unique_categories

        # Validate weights if provided
        if "weights" in self.params:
            weights = self.params["weights"]
            if not isinstance(weights, list):
                raise InvalidConfigParamException("weights must be a list")

            if len(weights) != len(categories):
                raise InvalidConfigParamException(
                    f"weights length ({len(weights)}) must match categories length ({len(categories)})"
                )

            # Validate weight values
            for weight in weights:
                if not isinstance(weight, int | float) or weight < 0:
                    raise InvalidConfigParamException(
                        "All weights must be non-negative numbers"
                    )

            # Normalize weights
            total_weight = sum(weights)
            if total_weight == 0:
                raise InvalidConfigParamException("Total weight cannot be zero")

            self.params["weights"] = [w / total_weight for w in weights]

        # Validate sampling method
        if "sampling_method" in self.params:
            valid_methods = ["uniform", "weighted", "ordered", "random"]
            if self.params["sampling_method"] not in valid_methods:
                raise InvalidConfigParamException(
                    f"sampling_method must be one of {valid_methods}, "
                    f"got '{self.params['sampling_method']}'"
                )

    def _get_categorical_constraints(self) -> dict[str, Any]:
        """
        Get validated categorical constraints.

        Returns:
            Dictionary with validated categories and sampling parameters
        """
        return {
            "categories": self.params["categories"],
            "weights": self.params.get("weights"),
            "sampling_method": self.params.get("sampling_method", "uniform"),
            "allow_replacement": self.params.get("allow_replacement", True),
            "unique_values": self.params.get("unique_values", False),
        }

    def _normalize_categories(self, categories: list[Any]) -> list[str]:
        """
        Normalize categories to strings for consistent processing.

        Args:
            categories: List of categories to normalize

        Returns:
            List of string representations
        """
        return [str(cat) for cat in categories]

    def _validate_category_mappings(self, mappings: dict[str, Any] = None) -> None:
        """
        Validate category mappings/replacements.

        Args:
            mappings: Dictionary mapping categories to replacement values
        """
        if mappings:
            for original, _replacement in mappings.items():
                if original not in self.params["categories"]:
                    raise InvalidConfigParamException(
                        f"Mapping contains unknown category '{original}'"
                    )
