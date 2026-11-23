"""Alert notifications.

Turns a list of threshold alerts into user-visible notifications with
**deduplication**: an alert type only fires once while it persists; it can
re-fire after it clears. That keeps the user informed without a wall of
repeated messages every second.

Backends
--------
* :class:`ConsoleNotifier` — prints to stdout (always on; also the default
  for tests).
* :class:`EmailNotifier` — sends via SMTP (stdlib ``smtplib``); constructed
  only when the config supplies SMTP settings, so it stays optional.

:class:`Notifier` combines whichever backends are enabled and exposes the
single :meth:`notify` entry point the app calls with the current alert list.
"""

from __future__ import annotations

import smtplib
import time
from email.message import EmailMessage
from typing import List, Optional, Sequence

from wine_monitor.sensors import SensorReading


class Notifier:
    """Fan-out to multiple backends with per-alert-type deduplication."""

    def __init__(
        self,
        backends: Optional[Sequence["Backend"]] = None,
        dedupe: bool = True,
        quiet_seconds: float = 1800.0,
    ) -> None:
        self.backends: List["Backend"] = list(backends or [])
        self.dedupe = dedupe
        self.quiet_seconds = quiet_seconds
        self._active: set[str] = set()
        self._last_fired: dict[str, float] = {}
        self.sent_count = 0

    def notify(self, reading: SensorReading, alerts: List[str]) -> List[str]:
        """Evaluate *alerts* against state and send what should go out.

        Returns the list of alert strings actually dispatched this call.
        """
        dispatched: List[str] = []
        now = time.time()
        for alert in alerts:
            key = _alert_key(alert)
            if self.dedupe:
                if key in self._active:
                    continue  # already notified while this alert persists
                last = self._last_fired.get(key)
                if last is not None and (now - last) < self.quiet_seconds:
                    # Within the quiet period after a previous firing: mark as
                    # active (so it keeps re-arming only after the window ends)
                    # but do not dispatch.
                    continue
            self._last_fired[key] = now
            dispatched.append(alert)
            for b in self.backends:
                b.send(reading, alert)
        # Active set becomes exactly the alerts present right now; anything
        # cleared drops out automatically.
        self._active = {_alert_key(a) for a in alerts}
        self.sent_count += len(dispatched)
        return dispatched

    def reset(self) -> None:
        self._active.clear()
        self._last_fired.clear()
        self.sent_count = 0


def _alert_key(alert: str) -> str:
    """Stable key for an alert string: the text up to the first value.

    'temperature low: 14.2°C (min 15.0°C)' → 'temperature low'
    """
    return alert.split(":", 1)[0].strip()


class Backend:
    """Base class for notification destinations."""

    name = "backend"

    def send(self, reading: SensorReading, alert: str) -> None:  # pragma: no cover
        raise NotImplementedError


class ConsoleNotifier(Backend):
    """Prints alerts to stdout with a timestamp."""

    name = "console"

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def send(self, reading: SensorReading, alert: str) -> None:
        if self.enabled:
            print(f"[ALERT {time.strftime('%Y-%m-%d %H:%M:%S')}] {alert}")


class EmailNotifier(Backend):
    """Sends an email per alert via SMTP.

    All settings must come from config; if any are missing the notifier is
    disabled (it will never raise on a misconfigured install).
    """

    name = "email"

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        sender: str,
        recipient: str,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sender = sender or user
        self.recipient = recipient
        self.enabled = bool(host and user and password and recipient)

    def send(self, reading: SensorReading, alert: str) -> None:
        if not self.enabled:
            return
        msg = EmailMessage()
        msg["Subject"] = f"Wine Monitor alert: {alert}"
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg.set_content(
            f"Threshold breach at {time.strftime('%Y-%m-%d %H:%M:%S')}:\n\n"
            f"  {alert}\n\n"
            f"Current reading: {reading.temperature_c:.1f}°C, "
            f"{reading.humidity_pct:.1f}% RH, {reading.co2_ppm:.0f} ppm CO₂."
        )
        try:
            with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
        except (OSError, smtplib.SMTPException) as exc:
            # A notification failure must never crash the monitor.
            print(f"[notify] email failed: {exc}")
