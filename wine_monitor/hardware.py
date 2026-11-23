"""Hardware backends: the contract the app talks to, and a full simulator.

The rest of Wine Monitor (GUI, logging, alerts) only ever talks to
:class:`HardwareBackend`, never to ``RPi.GPIO`` or ``gpiozero`` directly.
That is what lets the *entire system* — actuators included — run on a laptop,
in CI, or on Windows via :class:`SimulatedHardware`, and makes it trivial to
drop in a real Pi backend later.

Simulated hardware
------------------
:class:`SimulatedHardware` is not a bag of random numbers; it models the
physics of the fermentation bay well enough to be useful for development:

* **Heater** drives the wine temperature toward a setpoint (default 28 °C).
* **Fan** drives it down toward a cool target (default 15 °C).
* **Fermentation** produces CO₂ at a rate that peaks near 22 °C and tapers
  off at the edges of the operating range.
* **Pump** (scrubber) removes CO₂ proportional to the fermentation rate.
* **Humidity** drifts toward a target that is higher while the heater runs.

All steps are dt-independent one-tick updates (the GUI ticks at 1 Hz); noise
is injected through an injectable ``random.Random`` so tests can be
deterministic.
"""

from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from wine_monitor.sensors import SensorReading


@dataclass(frozen=True)
class HardwareState:
    """Snapshot of actuator states (mirrors what a real backend would report)."""

    heater: bool
    fan: bool
    pump: bool


class HardwareBackend(ABC):
    """Interface between the application and physical hardware."""

    @abstractmethod
    def read(self) -> SensorReading:
        """Poll the sensors and return the latest :class:`SensorReading`."""

    @abstractmethod
    def set_heater(self, on: bool) -> None:
        """Switch the heating element on/off."""

    @abstractmethod
    def set_fan(self, on: bool) -> None:
        """Switch the cooling fan on/off."""

    @abstractmethod
    def set_pump(self, on: bool) -> None:
        """Switch the CO₂ scrubbing pump on/off."""

    @abstractmethod
    def state(self) -> HardwareState:
        """Return the current actuator states as reported by the hardware."""

    def close(self) -> None:
        """Release hardware resources (no-op by default)."""


class SimulatedHardware(HardwareBackend):
    """A physics-flavoured simulation of the full hardware stack.

    Parameters
    ----------
    seed:
        Seed for reproducible runs.
    rng:
        Explicit ``random.Random`` (overrides *seed*).
    ambient_c / heater_setpoint_c / fan_target_c:
        Temperature targets used by the thermal model.
    initial_temp_c / initial_humidity_pct / initial_co2_ppm:
        Starting conditions.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        rng: Optional[random.Random] = None,
        ambient_c: float = 20.0,
        heater_setpoint_c: float = 28.0,
        fan_target_c: float = 15.0,
        initial_temp_c: float = 20.0,
        initial_humidity_pct: float = 55.0,
        initial_co2_ppm: float = 500.0,
        max_history: int = 2000,
    ) -> None:
        self._rng = rng if rng is not None else random.Random(seed)
        self._ambient_c = ambient_c
        self._heater_setpoint_c = heater_setpoint_c
        self._fan_target_c = fan_target_c
        self._max_history = max_history

        self._temp = initial_temp_c
        self._humidity = initial_humidity_pct
        self._co2 = initial_co2_ppm

        self._heater = False
        self._fan = False
        self._pump = False

        self.history: List[SensorReading] = []

    # -- actuators ---------------------------------------------------------

    def set_heater(self, on: bool) -> None:
        self._heater = bool(on)

    def set_fan(self, on: bool) -> None:
        self._fan = bool(on)

    def set_pump(self, on: bool) -> None:
        self._pump = bool(on)

    def set_heater_setpoint(self, celsius: float) -> None:
        """Adjust the temperature the heater drives toward (e.g. from a GUI spinner)."""
        self._heater_setpoint_c = float(celsius)

    def state(self) -> HardwareState:
        return HardwareState(heater=self._heater, fan=self._fan, pump=self._pump)

    # -- thermal / process model ------------------------------------------

    @property
    def fermentation_rate(self) -> float:
        """Normalized (0..1) fermentation rate for the current temperature.

        Peaks at ~22 °C and tapers to zero 10 °C away, mirroring how yeast
        activity falls off outside the comfortable range.
        """
        return max(0.0, 1.0 - abs(self._temp - 22.0) / 10.0)

    def read(self) -> SensorReading:
        """Advance the simulation one tick and return a new reading."""
        # --- temperature ---------------------------------------------------
        if self._heater:
            self._temp += (self._heater_setpoint_c - self._temp) * 0.03
        if self._fan:
            self._temp += (self._fan_target_c - self._temp) * 0.03
        self._temp += self._rng.uniform(-0.05, 0.05)

        # --- CO₂ (fermentation production, pump scrubbing) ------------------
        f = self.fermentation_rate
        co2_target = 500.0 + 900.0 * f
        self._co2 += (co2_target - self._co2) * 0.1 + self._rng.uniform(-10.0, 10.0)
        if self._pump:
            self._co2 -= 250.0 * f
        self._co2 = max(300.0, self._co2)

        # --- humidity -------------------------------------------------------
        hum_target = 55.0 + 15.0 * (1 if self._heater else 0)
        self._humidity += (hum_target - self._humidity) * 0.02 + self._rng.uniform(-0.2, 0.2)

        reading = SensorReading(
            timestamp=time.time(),
            temperature_c=round(self._temp, 2),
            humidity_pct=round(self._humidity, 1),
            co2_ppm=round(self._co2, 1),
        )
        self.history.append(reading)
        if len(self.history) > self._max_history:
            self.history.pop(0)
        return reading

    def close(self) -> None:
        self.history.clear()
