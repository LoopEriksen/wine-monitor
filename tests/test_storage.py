"""Tests for :mod:`wine_monitor.storage` — SQLite persistence and CSV export."""

from __future__ import annotations

import csv

from wine_monitor.sensors import SensorReading
from wine_monitor.storage import Storage


def _reading(i: int) -> SensorReading:
    return SensorReading(
        timestamp=1_700_000_000.0 + i,
        temperature_c=20.0 + i * 0.1,
        humidity_pct=50.0 + i,
        co2_ppm=600.0 + i,
    )


def test_add_and_count(tmp_path):
    s = Storage(tmp_path / "test.db")
    for i in range(5):
        s.add(_reading(i))
    assert s.count() == 5
    s.close()


def test_latest_returns_most_recent_oldest_first(tmp_path):
    s = Storage(tmp_path / "test.db")
    for i in range(10):
        s.add(_reading(i))
    latest = s.latest(3)
    assert [r.timestamp for r in latest] == [1_700_000_007.0, 1_700_000_008.0, 1_700_000_009.0]
    s.close()


def test_all_preserves_order(tmp_path):
    s = Storage(tmp_path / "test.db")
    s.add_many([_reading(i) for i in range(7)])
    all_rows = s.all()
    assert len(all_rows) == 7
    assert all_rows[0].timestamp < all_rows[-1].timestamp
    s.close()


def test_roundtrip_values(tmp_path):
    s = Storage(tmp_path / "test.db")
    r = _reading(3)
    s.add(r)
    back = s.latest(1)[0]
    assert back == r
    s.close()


def test_add_many_returns_count(tmp_path):
    s = Storage(tmp_path / "test.db")
    assert s.add_many([_reading(i) for i in range(4)]) == 4
    assert s.count() == 4
    s.close()


def test_persistence_across_instances(tmp_path):
    path = tmp_path / "sub" / "test.db"
    s1 = Storage(path)
    s1.add_many([_reading(i) for i in range(6)])
    s1.close()
    s2 = Storage(path)  # reopen
    assert s2.count() == 6
    assert len(s2.all()) == 6
    s2.close()


def test_to_csv(tmp_path):
    s = Storage(tmp_path / "test.db")
    rows = [_reading(i) for i in range(4)]
    s.add_many(rows)
    out = s.to_csv(tmp_path / "out" / "log.csv")
    with out.open() as fh:
        parsed = list(csv.reader(fh))
    assert parsed[0] == ["timestamp", "temperature_c", "humidity_pct", "co2_ppm"]
    assert len(parsed) == 5  # header + 4 rows
    assert float(parsed[1][1]) == rows[0].temperature_c
    s.close()


def test_context_manager(tmp_path):
    with Storage(tmp_path / "ctx.db") as s:
        s.add(_reading(0))
        assert s.count() == 1
    # closed — no exception, no leak
    s = None
