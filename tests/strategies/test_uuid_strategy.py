import re

from tests.strategies.base import create_strategy_via_factory


def test_uuid_basic_generation():
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="UUID_STRATEGY",
        df=None,
        col_name="id",
        rows=5,
        params={},
    )
    out = s.generate_data(5)
    assert len(out) == 5
    assert out.dtype == object
    for v in out:
        assert isinstance(v, str)
        assert re.fullmatch(r"[0-9a-fA-F\-]{36}", v) is not None


def test_uuid_no_hyphens_uppercase_prefix_alnum_unique():
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="UUID_STRATEGY",
        df=None,
        col_name="id",
        rows=100,
        params={
            "hyphens": False,
            "uppercase": True,
            "prefix": "ID_",
            "alphanumeric_only": True,
            "seed": 7,
        },
        unique=True,
    )
    out = s.generate_data(100)
    assert len(out) == 100
    # Check format: prefix + 32 uppercase alphanumeric chars (no hyphens)
    for v in out:
        assert v.startswith("ID_")
        body = v[3:]
        assert re.fullmatch(r"[0-9A-Z]{32}", body) is not None
    # Uniqueness
    assert len(set(out.tolist())) == 100


def test_uuid_numbers_only():
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="UUID_STRATEGY",
        df=None,
        col_name="id",
        rows=10,
        params={"numbers_only": True, "uppercase": True, "seed": 1},
        unique=True,
    )
    out = s.generate_data(10)
    for v in out:
        assert v.isdigit()
        assert len(v) > 0


def test_uuid_v4_generation_default_format():
    s = create_strategy_via_factory(
        mode="NORMAL",
        strategy_name="UUID_STRATEGY",
        df=None,
        col_name="id",
        rows=5,
        params={"version": 4},
    )
    out = s.generate_data(5)
    # Default v4 should look like canonical UUID with hyphens
    for v in out:
        assert re.fullmatch(r"[0-9a-fA-F\-]{36}", v) is not None


def test_uuid_v5_deterministic_chunk_progression():
    s = create_strategy_via_factory(
        mode="STREAM&BATCH",
        strategy_name="UUID_STRATEGY",
        df=None,
        col_name="id",
        rows=6,
        params={"version": 5, "seed": 42},
    )
    first = s.generate_data(3)
    second = s.generate_data(3)
    # No overlap between sequential chunks for v5 deterministic
    assert set(first.tolist()).isdisjoint(set(second.tolist()))
