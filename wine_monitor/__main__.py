"""Console entry point.

By default launches the PyQt5 GUI. With ``--headless`` it runs the plain
terminal demo loop (simulated sensors + threshold alerts), which is useful
for a quick sanity check on machines without a display.

Examples
--------
    python -m wine_monitor            # GUI
    python -m wine_monitor --headless # terminal demo loop
"""

from __future__ import annotations

import sys


def _headless() -> None:
    """Print live simulated readings and threshold alerts until Ctrl+C."""
    import time

    from wine_monitor.hardware import SimulatedHardware
    from wine_monitor.sensors import Thresholds

    hw = SimulatedHardware()
    thresholds = Thresholds()
    print("Wine Monitor (headless simulator) — press Ctrl+C to stop.")
    print(f"{'time':>10}  {'temp(°C)':>9}  {'humidity(%)':>12}  {'co2(ppm)':>9}  alerts")
    print("-" * 78)
    try:
        while True:
            r = hw.read()
            alerts = thresholds.evaluate(r)
            alert_str = "; ".join(alerts) if alerts else "—"
            print(f"{int(r.timestamp):>10}  {r.temperature_c:>9.2f}  {r.humidity_pct:>12.1f}"
                  f"  {r.co2_ppm:>9.0f}  {alert_str}")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopped.")
        hw.close()


def main() -> int:
    if "--headless" in sys.argv[1:]:
        _headless()
        return 0
    from wine_monitor.gui import main as gui_main

    return gui_main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
