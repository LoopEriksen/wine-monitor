"""Tests for :mod:`wine_monitor.sensors`."""

from __future__ import annotations

import random

import pytest

from wine_monitor.sensors import SensorReading, SensorSimulator, Thresholds


def _reading(temp=20.0, hum=55.0, co2=0.0, ts=1_700_000_000.0) -> SensorReading:
    return SensorReading(timestamp=ts, temperature_c=temp, humidity_pct=hum, co2_ppm=co2)


class TestThresholds:
    def test_in_range_no_alerts(self):
        assert Thresholds().evaluate(_reading(20.0, 55.0)) == []

    def test_temp_low(self):
        alerts = Thresholds().evaluate(_reading(10.0, 55.0))
        assert any("temperature low" in a for a in alerts)

    def test_temp_high(self):
        alerts = Thresholds().evaluate(_reading(30.0, 55.0))
        assert any("temperature high" in a for a in alerts)

    def test_humidity_low(self):
        alerts = Thresholds().evaluate(_reading(20.0, 10.0))
        assert any("humidity low" in a for a in alerts)

    def test_humidity_high(self):
        alerts = Thresholds().evaluate(_reading(20.0, 99.0))
        assert any("humidity high" in a for a in alerts)

    def test_multiple_alerts(self):
        alerts = Thresholds().evaluate(_reading(5.0, 99.0))
        assert len(alerts) == 2

    def test_boundary_values_are_inclusive(self):
        # Exactly at the min/max should not alert (inclusive range).
        assert Thresholds().evaluate(_reading(15.0, 30.0)) == []
        assert Thresholds().evaluate(_reading(25.0, 80.0)) == []

    def test_custom_thresholds(self):
        t = Thresholds(temp_min_c=0.0, temp_max_c=100.0, humidity_min_pct=0.0, humidity_max_pct=100.0)
        assert t.evaluate(_reading(20.0, 50.0)) == []
        # Same reading against the default range is also fine, but a value just
        # above the custom max must alert.
        t2 = Thresholds(temp_min_c=0.0, temp_max_c=10.0)
        assert any("temperature high" in a for a in t2.evaluate(_reading(11.0, 50.0)))


class TestSensorSimulator:
    def test_read_returns_sane_values(self):
        sim = SensorSimulator(seed=42)
        for _ in range(50):
            r = sim.read()
            assert 10.0 <= r.temperature_c <= 35.0
            assert 20.0 <= r.humidity_pct <= 95.0
            assert r.co2_ppm > 0.0

    def test_history_grows_and_bounded(self):
        sim = SensorSimulator(seed=1, max_history=10)
        for _ in range(25):
            sim.read()
        assert len(sim.history) == 10

    def test_reset_clears_history(self):
        sim = SensorSimulator(seed=1)
        sim.read()
        assert len(sim.history) == 1
        sim.reset()
        assert sim.history == []

    def test_deterministic_with_seed(self):
        a = SensorSimulator(seed=7)
        b = SensorSimulator(seed=7)
        seq_a = [a.read() for _ in range(5)]
        seq_b = [b.read() for _ in range(5)]
        assert [x.temperature_c for x in seq_a] == [x.temperature_c for x in seq_b]
        assert [x.humidity_pct for x in seq_a] == [x.humidity_pct for x in seq_b]

    def test_injectable_rng(self):
        sim = SensorSimulator(rng=random.Random(0))
        r = sim.read()
        assert isinstance(r, SensorReading)


class TestSensorReading:
    def test_frozen(self):
        import dataclasses

        r = _reading()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.temperature_c = 99.0  # type: ignore[misc]

    def test_fields(self):
        r = _reading(temp=18.5, hum=60.0, co2=700.0, ts=123.0)
        assert r.temperature_c == 18.5
        assert r.humidity_pct == 60.0
        assert r.co2_ppm == 700.0
        assert r.timestamp == 123.0
