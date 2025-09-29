"""
Mixin classes for strategy base functionality.

This module provides reusable mixin classes to reduce boilerplate code
across different strategy implementations. Mixins provide common functionality
that can be easily added to any strategy by multiple inheritance.

Available Mixins:
- SeedMixin: Handles random seed validation and initialization
- StatefulMixin: Provides state management methods (reset, get_state, etc.)
- ValidationMixin: Offers common parameter validation patterns

Usage Examples:
    # Simple strategy with all mixins
    class MyStrategy(BaseStrategy, SeedMixin, StatefulMixin, ValidationMixin):
        def __init__(self, logger=None, **kwargs):
            super().__init__(logger, **kwargs)
            self._validate_seed()        # From SeedMixin
            self._initialize_random_seed()  # From SeedMixin
            self._initialize_state()     # From StatefulMixin
            self._validate_params()      # From ValidationMixin

        def _validate_params(self):
            self._validate_required_params(['my_param'])
            self._validate_enum_param('my_type', ['type1', 'type2'])

    # Strategy with just seed functionality
    class SeededStrategy(BaseStrategy, SeedMixin):
        def __init__(self, logger=None, **kwargs):
            super().__init__(logger, **kwargs)
            self._validate_seed()
            self._initialize_random_seed()

Migration from Manual Implementation:
    Before mixins, strategies had ~50-80 lines of boilerplate for:
    - Seed handling and validation
    - State initialization and management
    - Parameter validation

    After using mixins, this reduces to ~5-10 lines of mixin initialization,
    saving ~70% of boilerplate code per strategy.
"""

import random
from typing import Any

import numpy as np
import pandas as pd

from exceptions.param_exceptions import InvalidConfigParamException


class SeedMixin:
    """
    Mixin for strategies that use random seed functionality.

    This mixin provides common seed validation and initialization patterns
    that ensure reproducible random number generation across strategy runs.

    Features:
    - Automatic seed validation (must be integer)
    - Random state initialization for both random and numpy
    - Seed storage for state reporting
    - Graceful handling of missing seed parameter

    Usage:
        class MyStrategy(BaseStrategy, SeedMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._validate_seed()        # Validates 'seed' parameter
                self._initialize_random_seed()  # Sets random seed

        # In params: {"seed": 42} -> reproducible results
        # No seed param -> uses system random state
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seed = None

    def _validate_seed(self) -> None:
        """
        Validate seed parameter if provided.

        Raises:
            InvalidConfigParamException: If seed is not a valid integer
        """
        if "seed" in self.params and self.params["seed"] is not None:
            try:
                self._seed = int(self.params["seed"])
            except (ValueError, TypeError) as e:
                raise InvalidConfigParamException("Seed must be an integer") from e

    def _initialize_random_seed(self) -> None:
        """
        Initialize random seed if provided.
        Should be called during strategy initialization.
        """
        if self._seed is not None:
            random.seed(self._seed)
            np.random.seed(self._seed)

    def _get_seed_for_state(self) -> int | None:
        """Get current seed value for state information."""
        return self._seed


class StatefulMixin:
    """
    Mixin for strategies that implement stateful generation pattern.

    This mixin provides a standard interface for stateful data generation,
    ensuring consistent behavior across different strategies that maintain state.

    Features:
    - Standardized state initialization pattern
    - State reset functionality
    - State reporting for debugging
    - State synchronization after generation

    Usage:
        class MyStrategy(BaseStrategy, StatefulMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._initialize_state()  # Initialize your state

            def _initialize_state(self):
                super()._initialize_state()  # Call parent first
                self._counter = 0           # Your state variables
                self._data = []             # More state

            def generate_chunk(self, count):
                # Use state in generation
                values = [self._counter + i for i in range(count)]
                self._counter += count
                return pd.Series(values)

        # Automatic state management methods available:
        # - reset_state(): Resets to initial state
        # - get_current_state(): Returns state dict for debugging
        # - sync_state(result): Updates state after generation
        # - is_stateful(): Returns True
    """

    def _initialize_state(self) -> None:
        """
        Initialize internal state for stateful generation.
        Strategies should override this method to set up their specific state.
        """
        pass

    def reset_state(self) -> None:
        """
        Reset the internal state to initial values.
        Strategies should override this method to reset their specific state.
        """
        self.logger.debug("Resetting strategy state")

    def get_current_state(self) -> dict[str, Any]:
        """
        Get current state information for debugging.
        Strategies should override this method to provide their specific state info.

        Returns:
            Dict containing state information
        """
        return {
            "strategy": self.__class__.__name__,
            "stateful": self.is_stateful(),
            "column": getattr(self, "col_name", None),
            "seed": getattr(self, "_seed", None),
        }

    def sync_state(self, result: pd.Series) -> dict[str, Any]:
        """
        Sync the state of the strategy with generation results.
        Strategies should override this method to update their state based on results.

        Args:
            result: Generated data series

        Returns:
            Dict containing updated state information
        """
        return self.get_current_state()

    def is_stateful(self) -> bool:
        """
        Check if this strategy supports stateful generation.
        All strategies using this mixin are stateful by design.

        Returns:
            True, as all strategies using this mixin are stateful
        """
        return True


class ValidationMixin:
    """
    Mixin for strategies that need common validation patterns.

    This mixin provides reusable validation methods that eliminate boilerplate
    validation code and ensure consistent error handling across strategies.

    Features:
    - Required parameter validation
    - Enum parameter validation with defaults
    - Numeric parameter validation with range checking
    - Automatic type conversion
    - Consistent error messages

    Usage:
        class MyStrategy(BaseStrategy, ValidationMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._validate_params()

            def _validate_params(self):
                # Required parameters
                self._validate_required_params(['input_file', 'output_format'])

                # Enum validation with default
                self._validate_enum_param('output_format',
                                        ['csv', 'json', 'xml'],
                                        'csv')

                # Numeric validation with range
                self._validate_numeric_param('batch_size',
                                           min_value=1,
                                           max_value=10000)

                # Custom validation
                if self.params.get('batch_size', 0) < 10:
                    raise InvalidConfigParamException(
                        "batch_size should be at least 10 for efficiency"
                    )

    Available Methods:
    - _validate_required_params(params_list): Ensure required params exist
    - _validate_enum_param(name, valid_values, default): Validate enum with default
    - _validate_numeric_param(name, min_value, max_value, param_type): Validate numbers
    """

    def _validate_params(self) -> None:
        """
        Validate strategy parameters using ValidationMixin helpers.

        This method provides a default implementation that strategies can
        override or extend. The default implementation does nothing,
        allowing strategies to use ValidationMixin helper methods as needed.

        Strategies should override this method to implement their specific
        validation logic using the helper methods provided by this mixin.
        """
        pass

    def _validate_required_params(self, required_params: list[str]) -> None:
        """
        Ensure all required parameters are present in self.params.

        Args:
            required_params: List of required parameter names

        Raises:
            InvalidConfigParamException if any required parameter is missing
        """
        missing_params = [
            param
            for param in required_params
            if param not in getattr(self, "params", {})
        ]
        if missing_params:
            raise InvalidConfigParamException(
                f"Missing required parameters: {', '.join(missing_params)}"
            )

    def _validate_enum_param(
        self, param_name: str, valid_values: list[str], default_value: str | None = None
    ) -> None:
        """
        Validate that a parameter has one of the allowed values, optionally setting a default.

        Args:
            param_name: Name of the parameter to validate
            valid_values: Allowed values for the parameter
            default_value: Default value to set if parameter is missing
        """
        if param_name not in self.params:
            if default_value is not None:
                self.params[param_name] = default_value
                return
            raise InvalidConfigParamException(
                f"Missing required parameter: {param_name}"
            )

        if self.params[param_name] not in valid_values:
            raise InvalidConfigParamException(
                f"Invalid {param_name}: {self.params[param_name]}. Must be one of {valid_values}"
            )

    def _validate_numeric_param(
        self,
        param_name: str,
        min_value: float | None = None,
        max_value: float | None = None,
        param_type: type = int,
    ) -> None:
        """
        Validate that a parameter is a valid number within optional bounds.

        Args:
            param_name: Name of the numeric parameter
            min_value: Optional minimum value
            max_value: Optional maximum value
            param_type: int or float
        """
        if param_name not in self.params:
            raise InvalidConfigParamException(
                f"Missing required parameter: {param_name}"
            )

        try:
            value = param_type(self.params[param_name])
            self.params[param_name] = value
        except (ValueError, TypeError) as e:
            raise InvalidConfigParamException(
                f"{param_name} must be a valid {param_type.__name__}"
            ) from e

        if min_value is not None and value < min_value:
            raise InvalidConfigParamException(
                f"{param_name} must be >= {min_value}, got {value}"
            )
        if max_value is not None and value > max_value:
            raise InvalidConfigParamException(
                f"{param_name} must be <= {max_value}, got {value}"
            )


class PerformanceMonitoringMixin:
    """
    Mixin for strategies that need performance monitoring and metrics.

    This mixin provides timing, memory usage tracking, and performance metrics
    to help optimize strategy performance and identify bottlenecks.

    Features:
    - Execution time tracking
    - Memory usage monitoring
    - Operation counting
    - Performance reporting
    - Configurable thresholds

    Usage:
        class MyStrategy(BaseStrategy, PerformanceMonitoringMixin):
            def __init__(self, logger=None, **kwargs):
                super().__init__(logger, **kwargs)
                self._setup_performance_monitoring()

            def generate_chunk(self, count: int) -> pd.Series:
                with self._performance_timer("generate_chunk"):
                    # Your generation logic here
                    result = self._do_generation(count)
                    self._record_metric("chunks_generated", 1)
                    self._record_metric("rows_generated", count)
                    return result

            def _do_generation(self, count: int) -> pd.Series:
                # Actual implementation
                return pd.Series([f"data_{i}" for i in range(count)])

    Available Methods:
    - _setup_performance_monitoring(): Initialize monitoring
    - _performance_timer(name): Context manager for timing operations
    - _record_metric(name, value): Record custom metrics
    - _get_performance_report(): Get performance summary
    - _check_performance_thresholds(): Check if performance is within limits
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._performance_metrics = {}
        self._performance_timers = {}
        self._performance_thresholds = {}

    def _setup_performance_monitoring(self) -> None:
        """Initialize performance monitoring with default metrics."""
        self._performance_metrics = {
            "total_operations": 0,
            "total_execution_time": 0.0,
            "peak_memory_usage": 0,
            "errors_count": 0,
            "warnings_count": 0,
        }

        # Default thresholds
        self._performance_thresholds = {
            "max_execution_time": 30.0,  # seconds
            "max_memory_usage": 100 * 1024 * 1024,  # 100MB
            "warning_execution_time": 5.0,  # seconds
        }

    def _performance_timer(self, operation_name: str):
        """
        Context manager for timing operations.

        Args:
            operation_name: Name of the operation being timed

        Usage:
            with self._performance_timer("data_generation"):
                result = self.generate_data()
        """
        import time
        from contextlib import contextmanager

        @contextmanager
        def timer():
            start_time = time.perf_counter()
            start_memory = self._get_memory_usage()

            try:
                yield
            finally:
                end_time = time.perf_counter()
                end_memory = self._get_memory_usage()

                execution_time = end_time - start_time
                memory_used = end_memory - start_memory

                # Record metrics
                self._record_metric(f"{operation_name}_time", execution_time)
                self._record_metric(f"{operation_name}_memory", memory_used)
                self._record_metric(
                    "total_execution_time", execution_time, increment=True
                )
                self._record_metric("total_operations", 1, increment=True)

                # Update peak memory
                current_peak = self._performance_metrics.get("peak_memory_usage", 0)
                if end_memory > current_peak:
                    self._performance_metrics["peak_memory_usage"] = end_memory

                # Check thresholds
                self._check_performance_thresholds(
                    operation_name, execution_time, memory_used
                )

        return timer()

    def _record_metric(self, name: str, value: float, increment: bool = False) -> None:
        """
        Record a performance metric.

        Args:
            name: Metric name
            value: Metric value
            increment: If True, add value to existing metric instead of replacing
        """
        if increment:
            self._performance_metrics[name] = (
                self._performance_metrics.get(name, 0) + value
            )
        else:
            self._performance_metrics[name] = value

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        import os

        import psutil

        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except Exception:
            return 0

    def _check_performance_thresholds(
        self, operation_name: str, execution_time: float, memory_used: int
    ) -> None:
        """
        Check if performance metrics exceed thresholds.

        Args:
            operation_name: Name of the operation
            execution_time: Time taken for operation
            memory_used: Memory used by operation
        """
        # Check execution time
        max_time = self._performance_thresholds.get("max_execution_time", float("inf"))
        warning_time = self._performance_thresholds.get(
            "warning_execution_time", float("inf")
        )

        if execution_time > max_time:
            self.logger.error(
                f"Performance alert: {operation_name} took {execution_time:.2f}s "
                f"(exceeds threshold {max_time}s)"
            )
        elif execution_time > warning_time:
            self.logger.warning(
                f"Performance warning: {operation_name} took {execution_time:.2f}s "
                f"(exceeds warning threshold {warning_time}s)"
            )

        # Check memory usage
        max_memory = self._performance_thresholds.get("max_memory_usage", float("inf"))
        if memory_used > max_memory:
            self.logger.error(
                f"Memory alert: {operation_name} used {memory_used / 1024 / 1024:.1f}MB "
                f"(exceeds threshold {max_memory / 1024 / 1024:.1f}MB)"
            )

    def _get_performance_report(self) -> dict:
        """
        Get a comprehensive performance report.

        Returns:
            Dictionary containing performance metrics and analysis
        """
        report = {
            "metrics": self._performance_metrics.copy(),
            "thresholds": self._performance_thresholds.copy(),
            "summary": {
                "total_operations": self._performance_metrics.get(
                    "total_operations", 0
                ),
                "avg_execution_time": (
                    self._performance_metrics.get("total_execution_time", 0)
                    / max(self._performance_metrics.get("total_operations", 1), 1)
                ),
                "peak_memory_mb": (
                    self._performance_metrics.get("peak_memory_usage", 0) / 1024 / 1024
                ),
                "performance_status": self._get_performance_status(),
            },
        }

        return report

    def _get_performance_status(self) -> str:
        """Get overall performance status."""
        total_time = self._performance_metrics.get("total_execution_time", 0)
        max_time = self._performance_thresholds.get("max_execution_time", float("inf"))

        if total_time > max_time:
            return "CRITICAL"
        elif total_time > self._performance_thresholds.get(
            "warning_execution_time", float("inf")
        ):
            return "WARNING"
        else:
            return "NORMAL"

