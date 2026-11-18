"""PyQt5 GUI: live readings, real-time plots, actuator control, alerts.

The Qt-independent logic lives in :class:`Controller` so the tick loop
(read → evaluate thresholds → store → expose state) can be unit-tested
without a display. :class:`MainWindow` is a thin presentation layer on top
of it.

Run
---
    wine-monitor            # console script, or
    python -m wine_monitor.gui

On a Raspberry Pi the real hardware backend will plug in via
``create_backend()``; everywhere else (and with ``--simulate``) the
:class:`~wine_monitor.hardware.SimulatedHardware` is used, so the whole app —
actuators and all — runs on any machine.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from wine_monitor.hardware import HardwareBackend, SimulatedHardware
from wine_monitor.sensors import Thresholds
from wine_monitor.storage import Storage

PLOT_WINDOW = 120  # points kept per series (≈2 min at the 1 Hz tick)


class Controller:
    """Qt-independent heart of the app: one tick per timer interval."""

    def __init__(
        self,
        backend: HardwareBackend,
        storage: Storage,
        thresholds: Optional[Thresholds] = None,
    ) -> None:
        self.backend = backend
        self.storage = storage
        self.thresholds = thresholds or Thresholds()
        self.last_reading = None
        self.alerts: List[str] = []
        self.tick_count = 0

    def tick(self) -> None:
        """Read sensors, evaluate thresholds, persist the reading."""
        reading = self.backend.read()
        self.alerts = self.thresholds.evaluate(reading)
        self.storage.add(reading)
        self.last_reading = reading
        self.tick_count += 1


def create_backend(simulate: bool = False) -> HardwareBackend:
    """Pick the best available backend.

    A real Pi backend (GPIO wiring, sensors) will be implemented here and
    selected on a Raspberry Pi with ``WINE_MONITOR_USE_HW=1`` and ``RPi.GPIO``
    available. Until then — and on every non-Pi machine, or with *simulate* /
    ``WINE_MONITOR_FORCE_SIM=1`` — the simulator is returned so the entire
    app, actuators included, runs anywhere.
    """
    if simulate or os.getenv("WINE_MONITOR_FORCE_SIM", "0") == "1":
        return SimulatedHardware()
    if os.getenv("WINE_MONITOR_USE_HW", "0") == "1" and sys.platform.startswith("linux"):
        try:
            import RPi.GPIO  # noqa: F401
        except ImportError:
            pass
        else:
            # TODO: return the real GPIO backend once hardware wiring lands.
            pass
    return SimulatedHardware()


class MainWindow(QMainWindow):
    """The Wine Monitor application window."""

    def __init__(
        self,
        backend: Optional[HardwareBackend] = None,
        storage: Optional[Storage] = None,
        thresholds: Optional[Thresholds] = None,
        tick_ms: int = 1000,
    ) -> None:
        super().__init__()
        self.backend = backend or create_backend()
        self.storage = storage or Storage("data/wine_monitor.db")
        self.controller = Controller(self.backend, self.storage, thresholds)

        self.setWindowTitle("Wine Monitor")
        self.resize(900, 760)

        # --- current readings ------------------------------------------------
        readings = QWidget()
        layout = QVBoxLayout(readings)
        row1 = []
        self.temp_label = self._make_reading_label("Wine temp: —")
        self.humidity_label = self._make_reading_label("Humidity: —")
        self.co2_label = self._make_reading_label("CO₂: —")
        self.ferment_label = self._make_reading_label("Fermentation: —")
        for w in (self.temp_label, self.humidity_label, self.co2_label, self.ferment_label):
            w.setMinimumHeight(40)
            row1.append(w)
        hrow = _HRow(*row1)
        layout.addWidget(hrow)
        self.alerts_label = QLabel("No alerts.")
        self.alerts_label.setObjectName("alerts")
        layout.addWidget(self.alerts_label)

        # --- plots -------------------------------------------------------------
        self.fig = Figure(figsize=(8, 6), dpi=96)
        self.ax_temp, self.ax_hum, self.ax_co2 = self.fig.subplots(3, 1, sharex=True)
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self._style_axes()

        # --- actuator controls ---------------------------------------------------
        controls = QWidget()
        c_layout = QVBoxLayout(controls)
        self.heater_cb = QCheckBox("Heater")
        self.fan_cb = QCheckBox("Fan")
        self.pump_cb = QCheckBox("Pump (CO₂ scrub)")
        self.heater_cb.toggled.connect(self.backend.set_heater)
        self.fan_cb.toggled.connect(self.backend.set_fan)
        self.pump_cb.toggled.connect(self.backend.set_pump)
        c_layout.addWidget(_HRow(self.heater_cb, self.fan_cb, self.pump_cb))
        sp_layout = QHBoxLayout()
        sp_layout.addWidget(QLabel("Heater setpoint:"))
        self.setpoint_spin = QDoubleSpinBox()
        self.setpoint_spin.setRange(10.0, 40.0)
        self.setpoint_spin.setValue(28.0)
        self.setpoint_spin.setSingleStep(0.5)
        self.setpoint_spin.setSuffix(" °C")
        self.setpoint_spin.valueChanged.connect(self._on_setpoint_changed)
        sp_layout.addWidget(self.setpoint_spin)
        self.export_btn = QPushButton("Export CSV…")
        self.export_btn.clicked.connect(self._on_export)
        sp_layout.addWidget(self.export_btn)
        sp_layout.addStretch(1)
        c_layout.addLayout(sp_layout)

        # --- assemble ---------------------------------------------------------
        central = QWidget()
        root = QVBoxLayout(central)
        root.addWidget(readings)
        root.addWidget(self.canvas, stretch=1)
        root.addWidget(controls)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Simulated hardware" if isinstance(self.backend, SimulatedHardware)
                                     else "Hardware")

        # --- timer -------------------------------------------------------------
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.tick)
        self._timer.start(tick_ms)
        self.tick()  # first reading immediately

    # ------------------------------------------------------------------

    def _make_reading_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(12)
        label.setFont(font)
        label.setAutoFillBackground(True)
        return label

    def _style_axes(self) -> None:
        self.ax_temp.set_ylabel("Temp °C")
        self.ax_temp.grid(True, alpha=0.3)
        self.ax_hum.set_ylabel("Humidity %")
        self.ax_hum.grid(True, alpha=0.3)
        self.ax_co2.set_ylabel("CO₂ ppm")
        self.ax_co2.set_xlabel("Time (min, from start)")
        self.ax_co2.grid(True, alpha=0.3)

    def tick(self) -> None:
        """Run one controller tick and refresh the UI.

        Public so tests can drive the loop deterministically without waiting
        on the Qt event loop.
        """
        self.controller.tick()
        self._update_readings()
        self._update_plots()
        self._update_alerts()

    def _update_readings(self) -> None:
        r = self.controller.last_reading
        if r is None:
            return
        self.temp_label.setText(f"Wine temp: {r.temperature_c:.1f} °C")
        self.humidity_label.setText(f"Humidity: {r.humidity_pct:.1f} %")
        self.co2_label.setText(f"CO₂: {r.co2_ppm:.0f} ppm")
        if isinstance(self.backend, SimulatedHardware):
            self.ferment_label.setText(f"Fermentation: {self.backend.fermentation_rate:.0f} %")
        else:
            self.ferment_label.setText("Fermentation: n/a")

    def _update_plots(self) -> None:
        readings = self.storage.latest(PLOT_WINDOW)
        if len(readings) < 2:
            return
        t0 = readings[0].timestamp
        x = [(r.timestamp - t0) / 60.0 for r in readings]
        self.ax_temp.clear()
        self.ax_temp.plot(x, [r.temperature_c for r in readings], color="#d1495b")
        self.ax_temp.set_ylabel("Temp °C")
        self.ax_temp.grid(True, alpha=0.3)

        self.ax_hum.clear()
        self.ax_hum.plot(x, [r.humidity_pct for r in readings], color="#4393c3")
        self.ax_hum.set_ylabel("Humidity %")
        self.ax_hum.grid(True, alpha=0.3)

        self.ax_co2.clear()
        self.ax_co2.plot(x, [r.co2_ppm for r in readings], color="#6b8e23")
        self.ax_co2.set_ylabel("CO₂ ppm")
        self.ax_co2.set_xlabel("Time (min, from start)")
        self.ax_co2.grid(True, alpha=0.3)
        self.fig.tight_layout(pad=3.0)
        self.fig.canvas.draw()

    def _update_alerts(self) -> None:
        if self.controller.alerts:
            self.alerts_label.setText("⚠ " + "  ·  ".join(self.controller.alerts))
        else:
            self.alerts_label.setText("No alerts.")

    def _on_setpoint_changed(self, value: float) -> None:
        if isinstance(self.backend, SimulatedHardware):
            self.backend._heater_setpoint_c = float(value)

    def _on_export(self) -> None:
        default = "wine-monitor-log.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", default, "CSV files (*.csv)")
        if path:
            self.storage.to_csv(path)
            self.statusBar().showMessage(f"Exported {len(self.storage.all())} readings to {path}", 8000)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        self._timer.stop()
        self.backend.close()
        self.storage.close()
        super().closeEvent(event)


class _HRow(QWidget):
    """A simple horizontal stretchy row helper."""

    def __init__(self, *widgets: QWidget) -> None:
        super().__init__()
        layout = QHBoxLayout()
        for w in widgets:
            layout.addWidget(w)
        layout.addStretch(1)
        self.setLayout(layout)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Wine Monitor GUI")
    parser.add_argument("--simulate", action="store_true", help="force the hardware simulator")
    parser.add_argument("--db", default="data/wine_monitor.db", help="SQLite database path")
    parser.add_argument("--tick-ms", type=int, default=1000, help="tick interval in milliseconds")
    args = parser.parse_args(argv)

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    storage = Storage(args.db)
    window = MainWindow(
        backend=SimulatedHardware() if args.simulate else create_backend(simulate=args.simulate),
        storage=storage,
        tick_ms=args.tick_ms,
    )
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
