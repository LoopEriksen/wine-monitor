# Wine Monitor Roadmap

## Mission
To build a Python‑based GUI application that monitors and controls a 5‑gallon automated wine fermentation system, interfacing with Raspberry Pi GPIO, providing notifications, and graphing key parameters. The system should run continuously, auto‑start at boot, and be deployable via an installer.

## Project Scope
- **Windows is the primary device** — it runs the monitoring GUI (today on
  the built-in simulator; from Phase 2 onward connected to the Pi over the
  network).
- Raspberry Pi 4 (or similar) hosts the physical layer: GPIO sensors and
  relays (DS18B20, BME280, …).
- Python 3.10+ with relevant libraries (PyQt5/6, matplotlib; RPi.GPIO or
  gpiozero on the Pi only).
- GUI with real‑time graphs, status panels, control buttons.
- Notification system (email, push, local).
- Data logging to SQLite/CSV.
- One‑command installers: `install.bat` (Windows), `install.sh` (Linux/Pi);
  systemd autostart on the Pi.

## High‑Level Architecture
1. **Data acquisition layer** – GPIO reading + sensor integration (temperature, pressure, etc.).
2. **Control layer** – actuation commands to GPIO pins.
3. **Application layer** – GUI, scheduling, persistence.
4. **Notification layer** – messaging, alerts.

## Milestones
1. Environment setup & GitHub repo initialization. ✅
2. Sensor data acquisition prototype. ✅ (simulated; real sensors pending)
3. Control command interface prototype. ✅ (simulated actuators; real relays pending)
4. Basic GUI skeleton with status panel. ✅
5. Real‑time plotting. ✅
6. Notification module. ✅ (console + email via SMTP config; Telegram/Discord pending)
7. Persistence & logging. ✅ (SQLite + CSV export)
8. Installer & autostart. ✅ (install.sh + systemd; deb/Snap packaging pending)
9. Testing & documentation. ✅ (core; expanded as features land)

## Tasks (to be updated)
- [x] Create GitHub repository and push initial commit.
- [x] Draft README with usage instructions.
- [x] Write unit tests.
- [x] Design GUI mockup.
- [x] Implement main loop and event handling.
- [x] Add notifications (email/Telegram) on threshold breach. (email ✅; Telegram/Discord ⬜)
- [x] Create installer script (e.g., pyinstaller, deb). (install.sh + systemd ✅; deb ⬜)
- [x] Configure systemd service for autostart. (via install.sh --systemd)
- [ ] Setup Raspberry Pi environment (Python, libraries).
- [ ] Define GPIO pin mapping and test readings.

_Last updated: 2026‑11‑23 — Windows confirmed as the primary device (install.bat +
Windows‑first docs). Config, notifications, and installers are in; real GPIO
backend on the Pi and the Phase 2 Windows↔Pi network link are next._

## Notes
- Use virtualenv for dependency isolation.
- Keep code modular to allow future expansion (e.g., adding new sensors).