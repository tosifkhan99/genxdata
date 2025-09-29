import pandas as pd

from core.strategy_factory import StrategyFactory
from utils.logging import Logger


def test_mapping_strategy_reuse_with_different_params():
    logger = Logger.get_logger("tests.reuse")
    factory = StrategyFactory(logger=logger)

    df = pd.DataFrame(
        {
            "department_id": [1, 2, 3, 2, 1],
            "department_name": ["DEFAULT"] * 5,
        }
    )

    # First params: map 1 -> A
    params1 = {"map_from": "department_id", "mapping": {1: "A"}}
    s1 = factory.get_or_create_strategy(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        pool_key="dept_name",
        df=df.copy(),
        col_name="department_name",
        rows=len(df),
        params=params1,
    )
    out1 = s1.generate_data(len(df)).reset_index(drop=True)
    pd.testing.assert_series_equal(
        out1, pd.Series(["A", "DEFAULT", "DEFAULT", "DEFAULT", "A"], dtype=object)
    )

    # Second params: map 2 -> B (reuse same pooled instance)
    params2 = {"map_from": "department_id", "mapping": {2: "B"}}
    s2 = factory.get_or_create_strategy(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        pool_key="dept_name",
        df=df.copy(),
        col_name="department_name",
        rows=len(df),
        params=params2,
    )
    out2 = s2.generate_data(len(df)).reset_index(drop=True)
    # Expect only 2's mapped to B, others preserve existing
    pd.testing.assert_series_equal(
        out2, pd.Series(["DEFAULT", "B", "DEFAULT", "B", "DEFAULT"], dtype=object)
    )


def test_number_range_strategy_reuse_with_different_bounds():
    logger = Logger.get_logger("tests.reuse")
    factory = StrategyFactory(logger=logger)

    df = pd.DataFrame({"x": [0] * 10})

    params1 = {"start": 0, "end": 10, "seed": 123}
    s1 = factory.get_or_create_strategy(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        pool_key="num_range_x",
        df=df.copy(),
        col_name="x",
        rows=len(df),
        params=params1,
    )
    out1 = s1.generate_data(len(df))
    assert (out1 >= 0).all() and (out1 < 10).all()

    # Reuse same instance with different bounds
    params2 = {"start": 100, "end": 200, "seed": 123}
    s2 = factory.get_or_create_strategy(
        mode="NORMAL",
        strategy_name="RANDOM_NUMBER_RANGE_STRATEGY",
        pool_key="num_range_x",
        df=df.copy(),
        col_name="x",
        rows=len(df),
        params=params2,
    )
    out2 = s2.generate_data(len(df))
    assert (out2 >= 100).all() and (out2 < 200).all()
