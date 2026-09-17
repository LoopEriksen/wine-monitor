# Wine Monitor Project

This repository contains the source code for the **Wine Monitor** application, a Python GUI-based system for monitoring and controlling a 5‑gallon automated wine fermentation setup.

## Features
- Real‑time data acquisition from Raspberry Pi GPIO (temperature, pressure, etc.)
- Control of actuators via GPIO pins
- Graphical user interface with live plots and status panels
- Notification system (email, push, local)
- Persistent data logging to SQLite/CSV
- Installer package for easy deployment
- Auto‑start on Raspberry Pi boot via systemd

## Setup
1. **Clone the repo**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/wine-monitor.git
   cd wine-monitor
   ```
2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app**:
   ```bash
   python src/main.py
   ```

## Development
- Branch naming convention: `feature/…`, `bugfix/…`.
- All changes should be accompanied by tests.
- Push to the `main` branch for CI builds.

## Contributions
Feel free to open issues or pull requests. Please follow the coding standards outlined in `CONTRIBUTING.md`.

---

*This README is auto‑generated as part of the project initialization.*