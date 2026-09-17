# Wine Fermentation System Roadmap

## Mission
Create a continuously‑running, Raspberry Pi‑hosted Python application that
1. **Monitors** key fermentation parameters (temperature, humidity, pH, CO₂, gravity, etc.) and logs them.
2. **Controls** actuators (heaters, pumps, vents, temperature‑control fans, etc.) via GPIO.
3. **Visualizes** data in real‑time graphs and status panels.
4. **Notifies** users through email/SMS/Telegram/Discord when thresholds are crossed or anomalies occur.
5. **Deploys** cleanly as an install package that auto‑starts on boot.

## Core Components
- **Hardware interface** – Raspberry Pi GPIO, sensors (DS18B20, BME280, etc.) and relays.
- **Data storage** – SQLite/CSV for time‑series logs.
- **Backend** – Flask/FastAPI or a lightweight event loop.
- **Frontend** – PyQt5/PySide6 or a lightweight web UI served by the backend.
- **Notification system** – smtplib + Twilio/Telegram Bot.
- **Installer** – `setup.py` / `pip install .` + systemd service.

## High‑Level Roadmap
| Sprint | Milestone | Key Tasks | Owner |
|--------|-----------|-----------|-------|
| 1 | Project scaffolding | Create repo, CI, basic package layout | dev |
| 2 | Hardware abstraction | GPIO wrappers, sensor reading | dev |
| 3 | Data logger | Log to SQLite, CSV | dev |
| 4 | Basic UI | Display current values | dev |
| 5 | Control logic | PID/thresholds, actuator API | dev |
| 6 | Notifications | Email/Twilio/Telegram | dev |
| 7 | Installer & service | systemd unit, `pip install -e .` | dev |
| 8 | QA & documentation | Tests, README, usage docs | dev |

## Current Status
- [ ] Repository initialized (GitHub)
- [ ] Basic package structure created
- [ ] `README.md` placeholder added

## Next Steps
1. **Create GitHub repo** – `git init`, push to GitHub, set up branch protection.
2. **Add CI workflow** – GitHub Actions for linting, tests.
3. **Begin hardware abstraction layer** – stub functions for GPIO to allow testing on non‑Pi.

## Notes
- The name of the main script will be `wine_monitor.py`.
- Use virtualenv or Poetry for dependency isolation.
- Target Python ≥3.10.
- Logging should rotate daily.
- UI should support dark/light themes.

---
**This file is updated automatically by the development process.**