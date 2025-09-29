"""
Date series strategy: generates a contiguous date sequence starting from a date.

Supports:
- start_date: inclusive start (string in format)
- freq: pandas offset alias (e.g., 'D', 'W', 'M')
- format: input format for parsing start
- output_format: strftime format applied to output strings
"""

from datetime import datetime

import pandas as pd

from core.base_strategy import BaseStrategy
from core.mixins import StatefulMixin, ValidationMixin


class DateSeriesStrategy(BaseStrategy, StatefulMixin, ValidationMixin):
    def __init__(self, mode: str, logger=None, **kwargs):
        super().__init__(mode=mode, logger=logger, **kwargs)
        self._initialize_state()

    def _initialize_state(self) -> None:
        super()._initialize_state()
        self._start = self.params.get("start_date")
        # Normalize freq to lowercase to avoid pandas FutureWarning ('S' -> 's')
        self._freq = str(self.params.get("freq", "D")).lower()
        self._in_fmt = self.params.get("format", "%Y-%m-%d")
        self._out_fmt = self.params.get("output_format", "%Y-%m-%d")

        if isinstance(self._start, str):
            self._start = datetime.strptime(self._start, self._in_fmt)

    def generate_chunk(self, count: int) -> pd.Series:
        # Use count to determine number of periods
        rng = pd.date_range(self._start, periods=count, freq=self._freq)
        series = rng.strftime(self._out_fmt)
        return pd.Series(series, dtype=object)

    def reset_state(self) -> None:
        super().reset_state()
        self._initialize_state()
