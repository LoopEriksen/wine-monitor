"""Wine Monitor — monitor and control a 5‑gallon wine fermentation system.

The ``wine_monitor`` package is organized so that the testable, pure‑Python
core (sensor readings, simulation, threshold logic) has no dependency on
hardware (``RPi.GPIO``/``gpiozero``) or GUI toolkits (PyQt5/tkinter). That
keeps the core importable and unit‑testable on any machine, including CI and
Windows, while the GUI and hardware layers can be layered on top.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
