# Wine Monitor

A Python GUI application for monitoring and controlling a 5‑gallon automated
wine fermentation setup on a Raspberry Pi: live temperature/humidity/CO₂
readings from GPIO‑attached sensors, real‑time graphs, threshold alerts,
actuator control (heater, cooling fan, CO₂ scrubbing pump), and SQLite/CSV
data logging.

The project is split so the **whole system can run on simulated hardware**:
the GUI, storage, and alert logic only talk to a `HardwareBackend`
interface, and `SimulatedHardware` implements it with a small physics model
(heater/fan thermal drift, fermentation‑driven CO₂, pump scrubbing). That
means the app — actuators included — runs, and is unit‑tested, on any
machine (CI, Windows, a laptop), while the real Pi backend drops in behind
the same interface.

## Repository layout

```
wine_monitor/          # Core package (no RPi.GPIO / GUI hard deps)
  sensors.py           # SensorReading, Thresholds, SensorSimulator
  hardware.py          # HardwareBackend + SimulatedHardware (heater/fan/pump physics)
  storage.py           # SQLite time-series store + CSV export
  gui.py               # PyQt5 GUI: live plots, readings, alerts, actuator controls
  __main__.py          # Console entry: GUI, or --headless terminal demo
tests/                 # Pytest suite: sensors, hardware, storage, offscreen GUI
docs/
  roadmap.md           # Sprint plan & milestone status
  phase2-companion-windows.md  # Phase 2: Windows companion + AI expert
.github/workflows/     # CI (pytest on Linux/macOS/Windows, Py 3.10–3.13)
```

## Quick start

```bash
# 1. Clone
git clone https://github.com/LoopEriksen/wine-monitor.git
cd wine-monitor

# 2. Virtual environment (Python 3.10+)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install (GUI + dev extras; "hardware" is Pi-only)
pip install -e ".[gui,dev]"

# 4. Run the GUI (simulated hardware on any machine)
wine-monitor                    # or: python -m wine_monitor
wine-monitor --simulate         # force the simulator explicitly

# 5. Terminal-only demo (no display needed)
python -m wine_monitor --headless

# 6. Run the test suite (GUI tests run offscreen)
pytest
```

## GUI tour

The window shows, top to bottom:

- **Current readings** — wine temperature, humidity, CO₂, fermentation rate.
- **Live plots** — three synchronized time series (temp / humidity / CO₂),
  updated once per second from the store.
- **Actuators** — checkboxes for heater, fan, and pump, plus a heater
  setpoint spinner. On simulated hardware you can watch the temperature
  rise toward the setpoint with the heater on, fall with the fan on, and
  CO₂ climb with fermentation (then fall when the pump scrubs it).
- **Alerts** — threshold breaches (e.g. "temperature low: 10.0 °C") appear
  under the readings.
- **Export CSV** — dumps the full SQLite log to a CSV file.

Readings persist to `data/wine_monitor.db` (SQLite); pass `--db <path>` to
use a different location.

## Raspberry Pi

The GUI and hardware support live in optional extras:

```bash
pip install -e ".[gui,hardware]"
```

`wine_monitor.gui.create_backend()` currently returns the simulator
everywhere; the real GPIO backend (DS18B20, BME280, relays) will plug in
there — selected on a Pi with `WINE_MONITOR_USE_HW=1`. See
[docs/roadmap.md](docs/roadmap.md) for milestones and
[docs/phase2-companion-windows.md](docs/phase2-companion-windows.md) for the
Phase 2 companion app + AI wine expert.

## Features

- ✅ Simulated hardware stack with thermal/fermentation physics (heater, fan, pump, CO₂)
- ✅ Threshold evaluation with human‑readable alerts
- ✅ PyQt5 GUI: live plots, status, actuator controls, CSV export
- ✅ SQLite persistence + CSV export
- ✅ 44‑test pytest suite + cross‑platform CI (Py 3.10–3.13, 3 OSes)
- ⬜ Real sensor acquisition (DS18B20, BME280, …) behind `HardwareBackend`
- ⬜ Relays/actuators wiring on the Pi
- ⬜ Notifications (email, Telegram/Discord) on threshold breach
- ⬜ Installer + systemd autostart

## Development

- **Branch naming:** `feature/…`, `bugfix/…` (OpenClaw agents use `openclaw/…`).
- **Tests:** required for all changes; the core stays hardware/GUI‑free
  specifically so it can be tested everywhere. GUI tests run offscreen via
  `QT_QPA_PLATFORM=offscreen`.
- **Workflow:** PR against `main`; CI must pass (Linux, Windows, macOS ×
  Python 3.10–3.13).
- **Conventions:** see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
