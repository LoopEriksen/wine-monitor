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
machine. **Windows is the primary target**: it runs the monitoring GUI,
while the Raspberry Pi hosts the physical sensors/relays (today simulated,
from Phase 2 onward connected over the network — see
[docs/phase2-companion-windows.md](docs/phase2-companion-windows.md)). The
real Pi backend will plug into the same interface; nothing else changes.

## Repository layout

```
wine_monitor/          # Core package (no RPi.GPIO / GUI hard deps)
  sensors.py           # SensorReading, Thresholds, SensorSimulator
  hardware.py          # HardwareBackend + SimulatedHardware (heater/fan/pump physics)
  storage.py           # SQLite time-series store + CSV export
  notify.py            # Alert notifications: dedupe + console/email backends
  config.py            # JSON config (wine-monitor.json) with safe fallbacks
  gui.py               # PyQt5 GUI: live plots, readings, alerts, actuator controls
  __main__.py          # Console entry: GUI, or --headless terminal demo
install.bat            # Windows installer (double-click: venv, deps, launchers)
install.sh             # Linux/Pi installer (venv, deps, PATH link, systemd)
tests/                 # Pytest suite: sensors, hardware, storage, notify, offscreen GUI
docs/
  install.md           # Beginner-friendly install guide (Windows first)
  roadmap.md           # Sprint plan & milestone status
  phase2-companion-windows.md  # Phase 2: Windows companion + AI expert
.github/workflows/     # CI (pytest on Linux/macOS/Windows, Py 3.10–3.13)
```

## Quick start

### Windows (primary target)

1. Install Python 3.10+ from <https://www.python.org/downloads/> (tick
   **Add python.exe to PATH**).
2. Download the ZIP from the [repo page](https://github.com/LoopEriksen/wine-monitor)
   (green **Code** button → **Download ZIP**) and unzip it, e.g. to
   `C:\WineMonitor`.
3. Double-click **`install.bat`**.
4. Double-click **`Start Wine Monitor.vbs`** (or Start Menu → Wine Monitor).

Full beginner guide with troubleshooting: [docs/install.md](docs/install.md).

### Manual, any OS

```bash
# 1. Clone (or unzip the downloaded ZIP)
git clone https://github.com/LoopEriksen/wine-monitor.git
cd wine-monitor

# 2. Virtual environment (Python 3.10+)
python3 -m venv .venv                      # Windows: py -3 -m venv .venv
source .venv/bin/activate                  # Windows: .venv\Scripts\activate

# 3. Install (Windows: core+gui; add hardware extras only on a Raspberry Pi)
pip install -e ".[gui,dev]"

# 4. Run the GUI (simulated hardware)
wine-monitor

# 5. Terminal-only version (no display needed)
wine-monitor --headless

# 6. Run the test suite (GUI tests run offscreen)
pytest
```

On Linux/Raspberry Pi there is also a one-command `install.sh` (venv, deps,
PATH link, optional systemd autostart): `./install.sh`.

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
  under the readings. Each distinct alert notifies once while it persists
  (dedupe + quiet window); optionally by email — fill in the `smtp_*`
  fields in `wine-monitor.json`.
- **Export CSV** — dumps the full SQLite log to a CSV file.

Readings persist to `data/wine_monitor.db` (SQLite); pass `--db <path>` to
use a different location.

## Raspberry Pi (the hardware host)

The Pi runs the physical layer: sensors and relays on GPIO. Its monitoring
stack is the same `wine_monitor` package:

```bash
./install.sh           # adds the hardware extras (RPi.GPIO, gpiozero)
```

`wine_monitor.gui.create_backend()` currently returns the simulator
everywhere; the real GPIO backend (DS18B20, BME280, relays) will plug in
there — selected on a Pi with `WINE_MONITOR_USE_HW=1`. See
[docs/roadmap.md](docs/roadmap.md) for milestones.

The Phase 2 design (Windows GUI ↔ Pi API over the network) is in
[docs/phase2-companion-windows.md](docs/phase2-companion-windows.md).

## Features

- ✅ Simulated hardware stack with thermal/fermentation physics (heater, fan, pump, CO₂)
- ✅ Threshold evaluation with human‑readable alerts
- ✅ PyQt5 GUI: live plots, status, actuator controls, CSV export
- ✅ SQLite persistence + CSV export
- ✅ JSON config file with safe fallbacks (wine-monitor.json)
- ✅ Notifications with dedupe (console now; email via SMTP config)
- ✅ One-command installer (`install.sh`) + optional systemd autostart
- ✅ 66‑test pytest suite + cross‑platform CI (Py 3.10–3.13, 3 OSes)
- ⬜ Real sensor acquisition (DS18B20, BME280, …) behind `HardwareBackend`
- ⬜ Relays/actuators wiring on the Pi
- ⬜ Installer & autostart: deb/Snap packaging (systemd already covered)

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
