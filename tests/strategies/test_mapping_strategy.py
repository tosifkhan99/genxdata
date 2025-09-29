import pandas as pd

from tests.strategies.base import create_strategy_via_factory


def test_inline_mapping_overrides_only_mapped_and_preserves_existing():
    df = pd.DataFrame(
        {
            "department_id": [1, 2, 99, 2, 1],
            "department_name": ["DEFAULT_DEPARTMENT"] * 5,
        }
    )

    params = {
        "map_from": "department_id",
        "mapping": {1: "Sales", 2: "Marketing"},
    }
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        df=df.copy(),
        col_name="department_name",
        rows=len(df),
        params=params,
    )

    out = s.generate_data(len(df))
    expected = pd.Series(
        ["Sales", "Marketing", "DEFAULT_DEPARTMENT", "Marketing", "Sales"], dtype=object
    )
    pd.testing.assert_series_equal(out.reset_index(drop=True), expected)


def test_inline_mapping_no_existing_target_creates_series():
    df = pd.DataFrame(
        {
            "department_id": [1, 2, 3],
        }
    )
    params = {
        "map_from": "department_id",
        "mapping": {1: "Sales", 3: "Engineering"},
    }
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        df=df.copy(),
        col_name="department_name",
        rows=len(df),
        params=params,
    )

    out = s.generate_data(len(df))
    # 2 is unmapped -> missing; use pandas NA in expected
    expected = pd.Series(["Sales", pd.NA, "Engineering"], dtype=object)
    # Align NA types to avoid FutureWarning (nan vs <NA>)
    out_aligned = out.reset_index(drop=True).astype("string")
    expected_aligned = expected.astype("string")
    pd.testing.assert_series_equal(out_aligned, expected_aligned, check_names=False)


def test_file_mapping_behaves_like_inline(tmp_path):
    # Create a CSV mapping file
    csv_path = tmp_path / "mapping.csv"
    mapping_df = pd.DataFrame(
        {
            "dept_key": [1, 2, 3],
            "employee_name": ["Alice", "Bob", "Carol"],
        }
    )
    mapping_df.to_csv(csv_path, index=False)

    # Source df with existing target values
    df = pd.DataFrame(
        {
            "department_id": [1, 2, 99, 3],
            "employee_name": ["DEFAULT", "DEFAULT", "DEFAULT", "DEFAULT"],
        }
    )

    params = {
        "map_from": "department_id",
        "source_map_from": "dept_key",
        "source": str(csv_path),
        "source_column": "employee_name",
    }
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="MAPPING_STRATEGY",
        df=df.copy(),
        col_name="employee_name",
        rows=len(df),
        params=params,
    )

    out = s.generate_data(len(df))
    expected = pd.Series(["Alice", "Bob", "DEFAULT", "Carol"], dtype=object)
    pd.testing.assert_series_equal(out.reset_index(drop=True), expected)
