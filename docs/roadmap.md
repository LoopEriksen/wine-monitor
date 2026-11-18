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
1. Environment setup & GitHub repo initialization.
2. Sensor data acquisition prototype.
3. Control command interface prototype.
4. Basic GUI skeleton with status panel.
5. Real‑time plotting.
6. Notification module.
7. Persistence & logging.
8. Installer & autostart.
9. Testing & documentation.

## Tasks (to be updated)
- [x] Create GitHub repository and push initial commit.
- [x] Draft README with usage instructions.
- [x] Write unit tests.
- [ ] Setup Raspberry Pi environment (Python, libraries).
- [ ] Define GPIO pin mapping and test readings.
- [ ] Design GUI mockup.
- [ ] Implement main loop and event handling.
- [ ] Create installer script (e.g., pyinstaller, deb).
- [ ] Configure systemd service for autostart.

## Notes
- Use virtualenv for dependency isolation.
- Keep code modular to allow future expansion (e.g., adding new sensors).