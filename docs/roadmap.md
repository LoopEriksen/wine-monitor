# Wine Monitor Roadmap

## Mission
To build a Python‑based GUI application that monitors and controls a 5‑gallon automated wine fermentation system, interfacing with Raspberry Pi GPIO, providing notifications, and graphing key parameters. The system should run continuously, auto‑start at boot, and be deployable via an installer.

## Project Scope
- Raspberry Pi 4 (or similar) hosting the application.
- Python 3.10+ with relevant libraries (PyQt5/6, matplotlib, RPi.GPIO or gpiozero, watchdog, etc.)
- GUI with real‑time graphs, status panels, control buttons.
- Notification system (email, push, local).
- Data logging to SQLite/CSV.
- Installer package (dpkg/apt or Snap) that installs dependencies, configures autostart.

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
6. Notification module.
7. Persistence & logging. ✅ (SQLite + CSV export)
8. Installer & autostart.
9. Testing & documentation. ✅ (core; expanded as features land)

## Tasks (to be updated)
- [x] Create GitHub repository and push initial commit.
- [x] Draft README with usage instructions.
- [x] Write unit tests.
- [x] Design GUI mockup.
- [x] Implement main loop and event handling.
- [ ] Setup Raspberry Pi environment (Python, libraries).
- [ ] Define GPIO pin mapping and test readings.
- [ ] Add notifications (email/Telegram) on threshold breach.
- [ ] Create installer script (e.g., pyinstaller, deb).
- [ ] Configure systemd service for autostart.

_Last updated: 2026‑11‑18 — simulated hardware, GUI, and storage are in; real GPIO backend, notifications, and packaging are next._

## Notes
- Use virtualenv for dependency isolation.
- Keep code modular to allow future expansion (e.g., adding new sensors).