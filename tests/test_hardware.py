"""Tests for :mod:`wine_monitor.hardware` — the simulated hardware stack."""

from __future__ import annotations

import random

from wine_monitor.hardware import HardwareState, SimulatedHardware


def test_initial_state_all_off():
    hw = SimulatedHardware(seed=1)
    st = hw.state()
    assert st == HardwareState(heater=False, fan=False, pump=False)


def test_acts_as_backend_interface():
    from wine_monitor.hardware import HardwareBackend

    hw = SimulatedHardware(seed=1)
    assert isinstance(hw, HardwareBackend)
    r = hw.read()
    assert 10.0 <= r.temperature_c <= 40.0


def test_heater_warms_toward_setpoint():
    hw = SimulatedHardware(seed=1, initial_temp_c=18.0, heater_setpoint_c=28.0)
    hw.set_heater(True)
    temps = [hw.read().temperature_c for _ in range(60)]
    assert temps[-1] > temps[0]
    assert temps[-1] < 28.0  # asymptotic, never overshoots the model target
    assert hw.state().heater is True


def test_fan_cools():
    hw = SimulatedHardware(seed=1, initial_temp_c=30.0, fan_target_c=15.0)
    hw.set_fan(True)
    temps = [hw.read().temperature_c for _ in range(60)]
    assert temps[-1] < temps[0]
    assert temps[-1] > 15.0


def test_fan_beats_heater_when_both_on():
    hw = SimulatedHardware(seed=1, initial_temp_c=25.0, heater_setpoint_c=28.0, fan_target_c=15.0)
    hw.set_heater(True)
    hw.set_fan(True)
    temps = [hw.read().temperature_c for _ in range(80)]
    # With both on the net drift is downward.
    assert temps[-1] < 25.0


def test_co2_rises_with_fermentation_rate():
    # 22 °C is the fermentation peak.
    hw = SimulatedHardware(seed=1, initial_temp_c=22.0, initial_co2_ppm=500.0)
    for _ in range(40):
        hw.read()
    assert hw.read().co2_ppm > 500.0


def test_pump_scrubs_co2():
    hw = SimulatedHardware(seed=1, initial_temp_c=22.0, initial_co2_ppm=900.0)
    hw.set_pump(True)
    co2s = [hw.read().co2_ppm for _ in range(40)]
    assert co2s[-1] < co2s[0]


def test_humidity_rises_with_heater():
    hw = SimulatedHardware(seed=1, initial_humidity_pct=55.0)
    hw.set_heater(True)
    hums = [hw.read().humidity_pct for _ in range(60)]
    assert hums[-1] > hums[0]


def test_deterministic_with_seed():
    a = SimulatedHardware(seed=99)
    b = SimulatedHardware(seed=99)
    a.set_heater(True)
    b.set_heater(True)
    for _ in range(10):
        ra, rb = a.read(), b.read()
        # Same seed ⇒ same values (timestamps come from the wall clock).
        assert (ra.temperature_c, ra.humidity_pct, ra.co2_ppm) == (
            rb.temperature_c,
            rb.humidity_pct,
            rb.co2_ppm,
        )


def test_injectable_rng():
    hw = SimulatedHardware(rng=random.Random(0))
    r = hw.read()
    assert r.temperature_c > 0


def test_history_is_bounded():
    hw = SimulatedHardware(seed=1, max_history=50)
    for _ in range(120):
        hw.read()
    assert len(hw.history) == 50


def test_close_clears_history():
    hw = SimulatedHardware(seed=1)
    hw.read()
    hw.close()
    assert hw.history == []
