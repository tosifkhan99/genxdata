from typing import Any

from core.base_strategy import BaseStrategy
from core.strategy_factory import StrategyFactory
from utils.logging import Logger


class MockBaseStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        # Provide default mode for unit tests
        if len(args) == 0 and "mode" not in kwargs:
            kwargs["mode"] = "NORMAL"
        super().__init__(*args, **kwargs)

    def sync_state(self, updated_state: Any):
        return self.strategy_state


def create_strategy_via_factory(
    *,
    mode: str,
    strategy_name: str,
    df,
    col_name: str,
    rows: int,
    params: dict,
    intermediate: bool = False,
    unique: bool = False,
    strategy_state: dict | None = None,
    mask: str | None = None,
):
    factory = StrategyFactory(logger=Logger.get_logger("tests.strategies"))
    return factory.create_strategy(
        mode,
        strategy_name,
        df=df,
        col_name=col_name,
        rows=rows,
        intermediate=intermediate,
        params=params,
        unique=unique,
        strategy_state=strategy_state or {},
        mask=mask,
    )
