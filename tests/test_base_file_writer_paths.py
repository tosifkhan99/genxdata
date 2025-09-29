from core.writers.csv_file_writer import CsvFileWriter


def test_writer_normalizes_extension(tmp_path):
    cfg = {"output_path": str(tmp_path / "noext")}
    w = CsvFileWriter(cfg)
    # Should append .csv
    assert w.output_path.endswith(".csv")


def test_get_file_info_not_written(tmp_path):
    path = tmp_path / "future.csv"
    w = CsvFileWriter({"output_path": str(path)})
    info = w.get_file_info()
    assert info["output_path"].endswith("future.csv")
    assert info["exists"] is False
    assert info["writer_type"]

