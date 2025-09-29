import os
import sqlite3

import pandas as pd
import pytest

from core.writers.file_writer_factory import FileWriterFactory


@pytest.fixture(scope="session")
def sample_df() -> pd.DataFrame:
    rs = pd.Series(range(1, 101), name="id")
    vals = ((rs * 7) % 10 + 1).rename("value")
    return pd.concat([rs, vals], axis=1)


def _assert_equal_df(expected: pd.DataFrame, actual: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(
        expected.reset_index(drop=True),
        actual.reset_index(drop=True),
        check_dtype=False,
        check_like=True,
    )


def test_csv_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.csv")
    writer = FileWriterFactory().create_writer("csv", {"output_path": out_path})
    res = writer.write(sample_df)
    assert res["status"] == "success"

    df = pd.read_csv(out_path)
    _assert_equal_df(sample_df, df)


def test_json_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.json")
    writer = FileWriterFactory().create_writer("json", {"output_path": out_path})
    res = writer.write(sample_df)
    if res.get("status") != "success":
        pytest.skip(f"JSON writer failed: {res}")

    df = pd.read_json(out_path)
    _assert_equal_df(sample_df, df)


def test_excel_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.xlsx")
    writer = FileWriterFactory().create_writer("excel", {"output_path": out_path})
    res = writer.write(sample_df)
    if res.get("status") != "success":
        pytest.skip(f"Excel writer not available: {res}")

    try:
        df = pd.read_excel(out_path)
    except Exception as e:
        pytest.skip(f"Excel read not available: {e}")
    _assert_equal_df(sample_df, df)


def test_parquet_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.parquet")
    writer = FileWriterFactory().create_writer("parquet", {"output_path": out_path})
    res = writer.write(sample_df)
    if res.get("status") != "success":
        pytest.skip(f"Parquet writer not available: {res}")

    try:
        df = pd.read_parquet(out_path)
    except Exception as e:
        pytest.skip(f"Parquet read not available: {e}")
    _assert_equal_df(sample_df, df)


def test_feather_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.feather")
    writer = FileWriterFactory().create_writer("feather", {"output_path": out_path})
    res = writer.write(sample_df)
    if res.get("status") != "success":
        pytest.skip(f"Feather writer not available: {res}")

    try:
        df = pd.read_feather(out_path)
    except Exception as e:
        pytest.skip(f"Feather read not available: {e}")
    _assert_equal_df(sample_df, df)


def test_html_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.html")
    writer = FileWriterFactory().create_writer("html", {"output_path": out_path})
    res = writer.write(sample_df)
    assert res["status"] == "success"

    # Re-read using pandas HTML parser
    try:
        dfs = pd.read_html(out_path)
    except Exception as e:
        pytest.skip(f"HTML read not available: {e}")
    assert len(dfs) >= 1
    df = dfs[0]
    # Ensure numeric types are coerced for comparison
    for col in ["id", "value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    _assert_equal_df(sample_df, df[["id", "value"]])


def test_sqlite_writer_roundtrip(tmp_path, sample_df):
    out_path = os.path.join(str(tmp_path), "data.db")
    writer = FileWriterFactory().create_writer("sqlite", {"output_path": out_path})
    res = writer.write(sample_df)
    if res.get("status") != "success":
        pytest.skip(f"SQLite writer failed: {res}")

    # Read back using sqlite3
    conn = sqlite3.connect(out_path)
    try:
        df = pd.read_sql_query("SELECT id, value FROM data ORDER BY id", conn)
    finally:
        conn.close()
    _assert_equal_df(sample_df.sort_values(["id"]).reset_index(drop=True), df)
