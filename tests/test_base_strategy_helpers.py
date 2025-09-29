import pandas as pd

from core.base_strategy import BaseStrategy


class _StubStrategy(BaseStrategy):
    def generate_chunk(self, count: int) -> pd.Series:
        return pd.Series(list(range(count)))

    def reset_state(self):
        return


def test_apply_to_dataframe_no_mask_and_with_mask():
    df = pd.DataFrame({"a": [0, 1, 2, 3]})
    s = _StubStrategy(mode="NORMAL", df=df, col_name="out", rows=len(df), params={})

    # No mask: fills entire column
    out = s.apply_to_dataframe(df, "out", None)
    assert "out" in out.columns
    assert out["out"].notna().all()

    # With mask: fill subset on a fresh frame to avoid prior full-column fill
    df2 = pd.DataFrame({"a": [0, 1, 2, 3]})
    out2 = s.apply_to_dataframe(df2, "out", "a > 1")
    assert out2["out"].notna().sum() == 2

