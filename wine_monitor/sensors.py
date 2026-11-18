"""Sensor readings, simulation, and threshold evaluation.

This module is the testable core of Wine Monitor. It intentionally has **no**
dependency on ``RPi.GPIO``/``gpiozero`` or any GUI toolkit, so it can be
imported, run, and unit‑tested on any platform (CI, Windows, non‑Pi dev
boxes). Real hardware reads are expected to be slotted in behind the same
:func:`read`-style interface once the hardware abstraction layer is built.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SensorReading:
    """A single snapshot of the fermentation environment.

    Attributes
    ----------
    timestamp:
        Unix epoch seconds when the reading was taken.
    temperature_c:
        Wine/batch temperature in degrees Celsius.
    humidity_pct:
        Relative humidity in percent.
    co2_ppm:
        Carbon‑dioxide concentration in ppm (informational; 0.0 if not sensed).
    """

    timestamp: float
    temperature_c: float
    humidity_pct: float
    co2_ppm: float = 0.0


@dataclass(frozen=True)
class Thresholds:
    """Desired operating range for a fermentation batch.

    Values outside the inclusive range produce an alert. Defaults are sensible
    for a typical wine fermentation; override per‑batch as needed.
    """

    temp_min_c: float = 15.0
    temp_max_c: float = 25.0
    humidity_min_pct: float = 30.0
    humidity_max_pct: float = 80.0

    def evaluate(self, reading: SensorReading) -> List[str]:
        """Return a list of human‑readable alert strings for *reading*.

        An empty list means the reading is within every threshold.
        """
        alerts: List[str] = []
        t = reading.temperature_c
        h = reading.humidity_pct
        if t < self.temp_min_c:
            alerts.append(f"temperature low: {t:.1f}°C (min {self.temp_min_c:.1f}°C)")
        elif t > self.temp_max_c:
            alerts.append(f"temperature high: {t:.1f}°C (max {self.temp_max_c:.1f}°C)")
        if h < self.humidity_min_pct:
            alerts.append(f"humidity low: {h:.1f}% (min {self.humidity_min_pct:.1f}%)")
        elif h > self.humidity_max_pct:
            alerts.append(f"humidity high: {h:.1f}% (max {self.humidity_max_pct:.1f}%)")
        return alerts


class SensorSimulator:
    """Generate plausible, drifting fermentation readings.

    Used for development, demos, and headless runs where no real hardware is
    attached. The random walk is clamped to realistic bounds so the simulator
    produces believable data.

    Parameters
    ----------
    seed:
        Optional seed for reproducible sequences.
    rng:
        Optional ``random.Random`` instance to inject (useful in tests).
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        rng: Optional[random.Random] = None,
        max_history: int = 2000,
    ) -> None:
        self._rng = rng if rng is not None else random.Random(seed)
        self._max_history = max_history
        self._temp = 20.0
        self._humidity = 55.0
        self.history: List[SensorReading] = []

    def read(self) -> SensorReading:
        """Advance the simulation one step and return a new :class:`SensorReading`."""
        self._temp += self._rng.uniform(-0.3, 0.3)
        self._humidity += self._rng.uniform(-0.5, 0.5)
        self._temp = max(10.0, min(35.0, self._temp))
        self._humidity = max(20.0, min(95.0, self._humidity))

        reading = SensorReading(
            timestamp=time.time(),
            temperature_c=round(self._temp, 2),
            humidity_pct=round(self._humidity, 1),
            co2_ppm=round(self._rng.uniform(400.0, 1200.0), 1),
        )
        self.history.append(reading)
        if len(self.history) > self._max_history:
            self.history.pop(0)
        return reading

    def reset(self) -> None:
        """Clear accumulated history and reset the random walk to baseline."""
        self._temp = 20.0
        self._humidity = 55.0
        self.history.clear()
