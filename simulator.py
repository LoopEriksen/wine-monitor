"""Simple GPIO simulator for Windows.

This module mimics the essential parts of the :mod:`RPi.GPIO` API that are
required by the application. It is deliberately minimal – only the attributes
and methods used in :mod:`src.main` are implemented.

Usage
-----
```python
import simulator as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, True)
```

The simulator prints a message to stdout when ``output`` is called, allowing
debugging on non‑Raspberry‑Pi machines.
"""

class _GPIOStub:
    OUT = 0
    IN = 1
    BOARD = 0
    BCM = 1

    @staticmethod
    def setmode(mode):
        print(f"[SIM] setmode({mode})")

    @staticmethod
    def setup(pin, mode):
        print(f"[SIM] setup(pin={pin}, mode={mode})")

    @staticmethod
    def output(pin, value):
        print(f"[SIM] output(pin={pin}, value={value})")

    @staticmethod
    def input(pin):
        print(f"[SIM] input(pin={pin})")
        return 0

# expose the stub as GPIO
GPIO = _GPIOStub()

