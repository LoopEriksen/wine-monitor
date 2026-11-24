"""Tests for :mod:`wine_monitor.notify`."""

from __future__ import annotations

import time

import pytest

from wine_monitor.notify import (
    Backend,
    ConsoleNotifier,
    EmailNotifier,
    Notifier,
    _alert_key,
)
from wine_monitor.sensors import SensorReading


class RecordingBackend(Backend):
    def __init__(self):
        self.sent = []

    def send(self, reading, alert):
        self.sent.append(alert)


def _reading():
    return SensorReading(timestamp=time.time(), temperature_c=10.0, humidity_pct=55.0)


def test_key_strips_value():
    assert _alert_key("temperature low: 14.2°C (min 15.0°C)") == "temperature low"
    assert _alert_key("humidity high: 99% (max 80%)") == "humidity high"


def test_fires_each_distinct_alert_once():
    rec = RecordingBackend()
    n = Notifier([rec], dedupe=True)
    alerts = ["temperature low: 14.0°C (min 15.0°C)", "humidity low: 20.0% (min 30.0%)"]
    dispatched = n.notify(_reading(), alerts)
    assert len(dispatched) == 2
    assert len(rec.sent) == 2


def test_persistent_alert_does_not_refire():
    rec = RecordingBackend()
    n = Notifier([rec], dedupe=True)
    r = _reading()
    n.notify(r, ["temperature low: 14.0°C (min 15.0°C)"])
    # same alert, slightly different value: key is the same → no re-fire
    n.notify(r, ["temperature low: 13.5°C (min 15.0°C)"])
    assert len(rec.sent) == 1


def test_rearms_after_cleared_and_quiet_window():
    rec = RecordingBackend()
    n = Notifier([rec], dedupe=True, quiet_seconds=0.0)
    r = _reading()
    n.notify(r, ["temperature low: 14.0°C (min 15.0°C)"])
    n.notify(r, [])  # clears
    n.notify(r, ["temperature low: 14.0°C (min 15.0°C)"])  # re-fires
    assert len(rec.sent) == 2


def test_quiet_window_suppresses_refire():
    rec = RecordingBackend()
    n = Notifier([rec], dedupe=True, quiet_seconds=3600)
    r = _reading()
    alert = "temperature low: 14.0°C (min 15.0°C)"
    n.notify(r, [alert])          # fires
    n.notify(r, [])               # clears
    n.notify(r, [alert])          # re-arms within the quiet window → suppressed
    assert len(rec.sent) == 1
    # While it stays present, it must not re-fire even after the window lapses.
    n._last_fired[_alert_key(alert)] = time.time() - 7200
    n.notify(r, [alert])
    assert len(rec.sent) == 1
    # Clear once more, then re-arm after the window: fires again.
    n.notify(r, [])
    n.notify(r, [alert])
    assert len(rec.sent) == 2


def test_dedupe_disabled_refires_every_time():
    rec = RecordingBackend()
    n = Notifier([rec], dedupe=False)
    r = _reading()
    n.notify(r, ["humidity low: 20.0% (min 30.0%)"])
    n.notify(r, ["humidity low: 20.0% (min 30.0%)"])
    assert len(rec.sent) == 2


def test_multiple_backends_receive_all():
    a, b = RecordingBackend(), RecordingBackend()
    n = Notifier([a, b])
    n.notify(_reading(), ["temperature high: 30.0°C (max 25.0°C)"])
    assert a.sent == b.sent == ["temperature high: 30.0°C (max 25.0°C)"]


def test_sent_count_accumulates():
    n = Notifier([RecordingBackend()], dedupe=True)
    r = _reading()
    n.notify(r, ["temperature low: 14.0°C (min 15.0°C)"])
    n.notify(r, [])
    n.notify(r, ["humidity high: 90.0% (max 80.0%)"])
    assert n.sent_count == 2


def test_console_notifier_prints(capfd):
    n = ConsoleNotifier()
    n.send(_reading(), "temperature low: 10.0°C (min 15.0°C)")
    out = capfd.readouterr().out
    assert "[ALERT" in out and "temperature low" in out


def test_console_notifier_disabled_is_quiet(capfd):
    ConsoleNotifier(enabled=False).send(_reading(), "temperature low: 10.0°C")
    assert capfd.readouterr().out == ""


def test_email_notifier_disabled_without_credentials():
    e = EmailNotifier(host="", port=587, user="", password="", sender="", recipient="")
    assert e.enabled is False
    # must not raise even if called
    e.send(_reading(), "temperature low: 10.0°C (min 15.0°C)")


def test_email_notifier_enabled_with_credentials():
    e = EmailNotifier(
        host="smtp.example", port=587, user="u", password="p", sender="from@x", recipient="to@x"
    )
    assert e.enabled is True


def test_email_notifier_sends(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None):
            sent["host"] = host

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self):
            pass

        def login(self, user, password):
            sent["user"] = user

        def send_message(self, msg):
            sent["subject"] = msg["Subject"]
            sent["body"] = msg.get_content()

    monkeypatch.setattr("wine_monitor.notify.smtplib.SMTP", FakeSMTP)
    e = EmailNotifier(
        host="smtp.example", port=587, user="u", password="p", sender="f@x", recipient="t@x"
    )
    e.send(_reading(), "temperature low: 10.0°C (min 15.0°C)")
    assert sent["host"] == "smtp.example"
    assert "temperature low" in sent["subject"]
    assert "10.0°C" in sent["body"]


def test_email_failure_is_swallowed(monkeypatch, capsys):
    import smtplib

    def boom(*a, **k):
        raise smtplib.SMTPException("nope")

    monkeypatch.setattr("wine_monitor.notify.smtplib.SMTP", boom)
    e = EmailNotifier(
        host="smtp.example", port=587, user="u", password="p", sender="f@x", recipient="t@x"
    )
    e.send(_reading(), "temperature low: 10.0°C (min 15.0°C)")  # must not raise
    assert "email failed" in capsys.readouterr().out
