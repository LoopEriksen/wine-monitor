"""End-to-end integration: config → controller → notifier → storage (no Qt)."""

from __future__ import annotations

from wine_monitor.config import Config
from wine_monitor.gui import Controller
from wine_monitor.hardware import SimulatedHardware
from wine_monitor.notify import Backend, Notifier
from wine_monitor.storage import Storage


class RecordingBackend(Backend):
    def __init__(self):
        self.sent = []

    def send(self, reading, alert):
        self.sent.append(alert)


def test_config_drives_controller_and_notifier(tmp_path):
    cfg = Config(temp_min_c=18.0, temp_max_c=22.0, notify_dedupe=True, notify_quiet_minutes=0.0)
    cfg.db_path = str(tmp_path / "it.db")
    cfg.save(tmp_path / "it.json")

    # Reload to prove the file round-trips (what the app does at startup).
    loaded = Config.load(tmp_path / "it.json")
    assert loaded == cfg

    hw = SimulatedHardware(seed=3, initial_temp_c=10.0)  # far below min → alerts
    rec = RecordingBackend()
    notifier = Notifier(
        backends=[rec],
        dedupe=loaded.notify_dedupe,
        quiet_seconds=loaded.notify_quiet_minutes * 60.0,
    )
    storage = Storage(loaded.db_path)
    ctl = Controller(hw, storage, thresholds=loaded.thresholds(), notifier=notifier)

    for _ in range(5):
        ctl.tick()

    # Temperature 10 °C < min 18 °C → "temperature low" must fire exactly once
    # across five ticks (dedupe), while every reading is persisted.
    low = [a for a in rec.sent if a.startswith("temperature low")]
    assert len(low) == 1
    assert storage.count() == 5


def test_headless_flag_routes_to_headless(monkeypatch, tmp_path):
    """main() with --headless must route to _headless, not the GUI."""
    from wine_monitor import __main__ as m

    called = {}
    monkeypatch.setattr(m, "_headless", lambda argv: called.update(argv=argv) or 0)
    rc = m.main(["--headless", "--config", str(tmp_path / "c.json"), "--db", str(tmp_path / "d.db")])
    assert rc == 0
    assert "--headless" in called["argv"]
    assert str(tmp_path / "c.json") in called["argv"]


def test_headless_without_flag_routes_to_gui(monkeypatch):
    """main() without --headless must route to the GUI entry point."""
    from wine_monitor import __main__ as m
    import wine_monitor.gui as g

    called = {}
    monkeypatch.setattr(g, "main", lambda argv: called.update(argv=argv) or 0)
    rc = m.main(["--simulate"])
    assert rc == 0
    assert called["argv"] == ["--simulate"]


def test_controller_alerts_cleared_when_back_in_range(tmp_path):
    """A persistent low-temp alert stops being dispatched once temp recovers."""
    hw = SimulatedHardware(seed=1, initial_temp_c=10.0)
    rec = RecordingBackend()
    notifier = Notifier(backends=[rec], dedupe=True, quiet_seconds=0.0)
    storage = Storage(tmp_path / "rec.db")
    cfg = Config(temp_min_c=18.0, temp_max_c=22.0)
    ctl = Controller(hw, storage, thresholds=cfg.thresholds(), notifier=notifier)

    ctl.tick()  # 10 °C → alert
    assert [a for a in rec.sent if a.startswith("temperature low")]

    # Force recovery above the floor.
    hw._temp = 20.0
    for _ in range(3):
        ctl.tick()
    # No new "temperature low" dispatches after recovery.
    assert len([a for a in rec.sent if a.startswith("temperature low")]) == 1
    assert ctl.alerts == [] or all(not a.startswith("temperature low") for a in ctl.alerts)
