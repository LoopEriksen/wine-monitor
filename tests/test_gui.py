"""Tests for the PyQt5 GUI and controller, run offscreen (no display needed).

Requires ``PyQt5`` and matplotlib; skipped automatically when unavailable
(e.g. a bare CI runner without the GUI extra).
"""

from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("PyQt5")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication  # noqa: E402

from wine_monitor.gui import Controller, MainWindow  # noqa: E402
from wine_monitor.hardware import SimulatedHardware  # noqa: E402
from wine_monitor.storage import Storage  # noqa: E402

_QAPP = None


@pytest.fixture(scope="module")
def qapp():
    global _QAPP
    if _QAPP is None:
        _QAPP = QApplication.instance() or QApplication([])
    yield _QAPP


@pytest.fixture
def window(qapp, tmp_path):
    hw = SimulatedHardware(seed=123)
    storage = Storage(tmp_path / "gui.db")
    win = MainWindow(backend=hw, storage=storage, tick_ms=60_000)  # timer effectively off
    yield win
    win.close()


def test_window_constructs(window):
    assert window is not None
    assert window.windowTitle() == "Wine Monitor"


def test_tick_updates_readings_and_storage(window):
    # __init__ performs one immediate tick.
    assert window.controller.tick_count == 1
    for _ in range(5):
        window.tick()
    assert window.controller.tick_count == 6
    assert window.storage.count() == 6
    r = window.controller.last_reading
    assert "°C" in window.temp_label.text()
    assert "%" in window.humidity_label.text()
    assert "ppm" in window.co2_label.text()


def test_alerts_shown_when_threshold_breached(qapp, tmp_path):
    # Start cold: 10 °C trips the low-temperature threshold immediately.
    hw = SimulatedHardware(seed=1, initial_temp_c=10.0)
    storage = Storage(tmp_path / "cold.db")
    win = MainWindow(backend=hw, storage=storage, tick_ms=60_000)
    try:
        win.tick()
        assert win.controller.alerts
        assert "⚠" in win.alerts_label.text()
    finally:
        win.close()


def test_no_alerts_in_comfortable_range(qapp, tmp_path):
    hw = SimulatedHardware(seed=1, initial_temp_c=20.0, initial_humidity_pct=55.0)
    storage = Storage(tmp_path / "ok.db")
    win = MainWindow(backend=hw, storage=storage, tick_ms=60_000)
    try:
        win.tick()
        assert win.controller.alerts == []
        assert win.alerts_label.text() == "No alerts."
    finally:
        win.close()


def test_actuator_toggles_propagate_to_backend(window):
    window.heater_cb.setChecked(True)
    window.pump_cb.setChecked(True)
    assert window.backend.state().heater is True
    assert window.backend.state().pump is True
    window.fan_cb.setChecked(True)
    assert window.backend.state().fan is True


def test_plots_update_with_enough_points(window):
    for _ in range(3):
        window.tick()
    # After ≥2 readings the axes should have line data.
    assert len(window.ax_temp.lines) >= 1
    x, y = window.ax_temp.lines[0].get_xdata(), window.ax_temp.lines[0].get_ydata()
    assert len(x) >= 3 and len(y) >= 3


def test_setpoint_spin_reaches_backend(window):
    window.setpoint_spin.setValue(33.0)
    assert window.backend._heater_setpoint_c == 33.0
    # and the public setter agrees
    window.backend.set_heater_setpoint(21.0)
    assert window.backend._heater_setpoint_c == 21.0


def test_controller_standalone(tmp_path):
    """Controller works with no Qt at all — the heart of the app is GUI-free."""
    hw = SimulatedHardware(seed=5)
    storage = Storage(tmp_path / "ctl.db")
    c = Controller(hw, storage)
    for _ in range(10):
        c.tick()
    assert c.tick_count == 10
    assert storage.count() == 10
    assert c.last_reading is not None


def test_create_backend_returns_simulator(qapp):
    from wine_monitor.gui import create_backend

    assert isinstance(create_backend(), SimulatedHardware)
    assert isinstance(create_backend(simulate=True), SimulatedHardware)
