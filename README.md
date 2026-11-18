# Wine Monitor

A Python GUI application for monitoring and controlling a 5‑gallon automated
wine fermentation setup on a Raspberry Pi: live temperature/humidity/CO₂
readings from GPIO‑attached sensors, real‑time graphs, threshold alerts, and
actuator control (heaters, pumps, fans).

The project is split so the **testable core has no hardware or GUI
dependencies**. That means the simulation and alerting logic runs — and is
unit‑tested — on any machine (CI, Windows, a laptop), while the Raspberry Pi
brings in the GPIO and GUI extras.

## Repository layout

```
wine_monitor/          # Core package (no hardware/GUI deps)
  sensors.py           # SensorReading, Thresholds, SensorSimulator
  __main__.py          # Headless demo loop: python -m wine_monitor
src/
  main.py              # PyQt5 GUI entry point (target: Raspberry Pi)
tests/                 # Pytest suite for the core package
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

# 3. Install the core (any machine)
pip install -e .

# 4. Run the headless demo (simulated sensors, no display needed)
python -m wine_monitor

# 5. Run the test suite
pytest
```

## GUI (Raspberry Pi)

The PyQt5 front end and GPIO hardware support live in optional extras:

```bash
# Raspberry Pi / Linux with a display:
pip install -e ".[gui,hardware]"
SIMULATE=1 python src/main.py    # 1 = use GPIO simulator, 0 = real RPi.GPIO
```

On a non‑Pi machine, or with `SIMULATE=1`, `src/main.py` falls back to the
bundled GPIO simulator so the window runs anywhere.

## Features (planned → shipped)

- ✅ Simulated sensor feed with realistic drift (humidity, temp, CO₂)
- ✅ Threshold evaluation with human‑readable alerts
- ✅ Pytest suite + cross‑platform CI
- ⬜ Real sensor acquisition (DS18B20, BME280, …) behind the same interface
- ⬜ Actuator control (heaters, pumps, vents) via GPIO
- ⬜ Live plots in the GUI (matplotlib)
- ⬜ Notifications (email, Telegram/Discord) on threshold breach
- ⬜ SQLite/CSV logging with daily rotation
- ⬜ Installer + systemd autostart

See [docs/roadmap.md](docs/roadmap.md) for the full plan and
[docs/phase2-companion-windows.md](docs/phase2-companion-windows.md) for the
Phase 2 companion app + AI wine expert.

## Development

- **Branch naming:** `feature/…`, `bugfix/…` (OpenClaw agents use `openclaw/…`).
- **Tests:** all changes should be accompanied by tests; the core package is
  hardware/GUI‑free specifically so it can be tested everywhere.
- **Workflow:** open a pull request against `main`; CI must pass (pytest on
  Linux, Windows, and macOS for Python 3.10–3.13).
- **Conventions:** see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
