"""Console entry point.

By default launches the PyQt5 GUI. With ``--headless`` it runs the plain
terminal demo loop (simulated hardware + threshold alerts + notification
logging), which is useful on machines without a display and doubles as a
reference for how the real data-acquisition loop works.

Examples
--------
    wine-monitor                    # GUI
    wine-monitor --headless         # terminal loop (reads wine-monitor.json)
    python -m wine_monitor --headless
"""

from __future__ import annotations

import sys


def _headless(argv) -> int:
    """Print live simulated readings and threshold alerts until Ctrl+C."""
    import argparse as _ap
    import time

    from wine_monitor.config import Config, DEFAULT_CONFIG_PATH
    from wine_monitor.hardware import SimulatedHardware
    from wine_monitor.notify import ConsoleNotifier, EmailNotifier, Notifier
    from wine_monitor.storage import Storage

    parser = _ap.ArgumentParser(description="Wine Monitor headless demo")
    parser.add_argument("--config", default=None, help="path to wine-monitor.json")
    parser.add_argument("--db", default=None, help="SQLite database path (overrides config)")
    args = parser.parse_args([a for a in argv if a != "--headless"])

    config = Config.load(args.config or DEFAULT_CONFIG_PATH)
    if args.db:
        config.db_path = args.db

    hw = SimulatedHardware()
    storage = Storage(config.db_path)
    notifiers = [ConsoleNotifier()]
    if config.smtp_host:
        notifiers.append(
            EmailNotifier(
                host=config.smtp_host,
                port=config.smtp_port,
                user=config.smtp_user,
                password=config.smtp_password,
                sender=config.smtp_from,
                recipient=config.smtp_to,
            )
        )
    notifier = Notifier(
        backends=notifiers,
        dedupe=config.notify_dedupe,
        quiet_seconds=config.notify_quiet_minutes * 60.0,
    )

    print(f"Wine Monitor (headless simulator, db={config.db_path}) — Ctrl+C to stop.")
    print(f"{'time':>10}  {'temp(°C)':>9}  {'humidity(%)':>12}  {'co2(ppm)':>9}  alerts")
    print("-" * 82)
    try:
        while True:
            r = hw.read()
            storage.add(r)
            alerts = config.thresholds().evaluate(r)
            notifier.notify(r, alerts)
            if not alerts:
                print(f"{int(r.timestamp):>10}  {r.temperature_c:>9.2f}  {r.humidity_pct:>12.1f}"
                      f"  {r.co2_ppm:>9.0f}  —")
            time.sleep(max(0.2, config.tick_ms / 1000.0))
    except KeyboardInterrupt:
        print("\nStopped.")
        hw.close()
        storage.close()
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--headless" in argv:
        return _headless(argv)
    import wine_monitor.gui as gui_mod

    return gui_mod.main(argv)


if __name__ == "__main__":
    sys.exit(main())
