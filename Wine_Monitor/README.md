# Wine Fermentation System

This repository contains the source code for the Wine Fermentation System monitor and controller.

## Quick Start
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m wine_monitor
```

## Features
- Monitor temperature, humidity, gravity, etc.
- Control heaters, pumps, fans via Raspberry Pi GPIO.
- Real‑time graphs with PyQt5/PySide6.
- Email / Telegram notifications.
- Installable as a systemd service.

---

> **Note**: The hardware abstraction layer is not yet implemented.
