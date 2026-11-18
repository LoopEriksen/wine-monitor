"""Headless entry point: print live simulated readings and any threshold alerts.

Runs without a display or hardware, using the bundled simulator. Useful for a
quick sanity check and as a reference for how the real data-acquisition loop
will work.

Example
-------
    python -m wine_monitor
    SIMULATE_TEMPS=1 python -m wine_monitor   # (env hooks reserved for future use)
"""

from __future__ import annotations

import time

from wine_monitor.sensors import SensorSimulator, Thresholds


def main() -> None:
    sim = SensorSimulator()
    thresholds = Thresholds()
    print("Wine Monitor (simulator) — press Ctrl+C to stop.")
    print(f"{'time':>10}  {'temp(°C)':>9}  {'humidity(%)':>12}  alerts")
    print("-" * 60)
    try:
        while True:
            r = sim.read()
            alerts = thresholds.evaluate(r)
            alert_str = "; ".join(alerts) if alerts else "—"
            print(f"{int(r.timestamp):>10}  {r.temperature_c:>9.2f}  {r.humidity_pct:>12.1f}  {alert_str}")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
