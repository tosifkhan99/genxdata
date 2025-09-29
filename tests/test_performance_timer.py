from utils.performance_timer import measure_time, get_performance_report, time_operation
import time


def test_measure_time_records_metrics():
    # Act: measure a tiny operation
    with measure_time("unit_test_op", rows_processed=5):
        time.sleep(0.01)

    # Assert: report contains our operation and reasonable fields
    report = get_performance_report()
    assert "unit_test_op" in report
    assert "Total (s)" in report
    assert "Avg (s)" in report
    assert "Rows/sec" in report


@time_operation
def _timed_func(rows=0):
    time.sleep(0.005)
    return 42


def test_time_operation_decorator_records():
    assert _timed_func() == 42
    report = get_performance_report()
    # Decorated function should appear in report
    assert "_timed_func" in report

