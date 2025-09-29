import pandas as pd
import pytest

from exceptions.param_exceptions import InvalidConfigParamException
from tests.strategies.base import create_strategy_via_factory


def test_delete_strategy_returns_series_of_nones():
    """
    Tests if the MockDeleteStrategy returns a pandas Series of None values.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DELETE_STRATEGY",
        df=None,
        col_name="col",
        rows=5,
        params={},
        # mask is now provided at top-level
        mask="col > 10",
    )
    count = 5
    result = strategy.generate_data(count)
    assert isinstance(result, pd.Series)
    assert len(result) == count
    assert all(pd.isna(val) for val in result)


def test_delete_strategy_missing_mask_is_allowed():
    """
    Missing mask at top-level should default to applying to all rows without error.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DELETE_STRATEGY",
        df=None,
        col_name="col",
        rows=1,
        params={},
    )
    s = strategy.generate_data(1)
    assert isinstance(s, pd.Series)


def test_delete_strategy_ignores_non_string_mask():
    """
    Non-string mask at top-level is ignored (treated as None) without raising.
    """
    strategy = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="DELETE_STRATEGY",
        df=None,
        col_name="col",
        rows=1,
        params={},
        mask=123,  # type: ignore
    )
    s = strategy.generate_data(1)
    assert isinstance(s, pd.Series)
