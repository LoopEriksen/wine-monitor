"""Persistence: time-series storage in SQLite with CSV export.

Standard library only (``sqlite3`` + ``csv``), so it is testable on any
platform. The schema is intentionally flat and append-only — a
fermentation run is one table of readings — and CSV export is used for
long-term archiving and plotting in other tools.
"""

from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional, Union

from wine_monitor.sensors import SensorReading

_SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   REAL    NOT NULL,
    temperature_c REAL  NOT NULL,
    humidity_pct  REAL  NOT NULL,
    co2_ppm       REAL  NOT NULL DEFAULT 0.0
);
CREATE INDEX IF NOT EXISTS idx_readings_ts ON readings (timestamp);
"""


def _coerce(path: Union[str, Path]) -> Path:
    return Path(path)


class Storage:
    """Append-only reading store backed by a single SQLite file.

    The database file (and directory) are created on first use.
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = _coerce(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # -- writes --------------------------------------------------------------

    def add(self, reading: SensorReading) -> int:
        """Insert *reading*; returns the rowid."""
        cur = self._conn.execute(
            "INSERT INTO readings (timestamp, temperature_c, humidity_pct, co2_ppm)"
            " VALUES (?, ?, ?, ?)",
            (reading.timestamp, reading.temperature_c, reading.humidity_pct, reading.co2_ppm),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def add_many(self, readings: List[SensorReading]) -> int:
        """Bulk insert; returns the number of rows written."""
        rows = [(r.timestamp, r.temperature_c, r.humidity_pct, r.co2_ppm) for r in readings]
        self._conn.executemany(
            "INSERT INTO readings (timestamp, temperature_c, humidity_pct, co2_ppm)"
            " VALUES (?, ?, ?, ?)",
            rows,
        )
        self._conn.commit()
        return len(rows)

    # -- reads ---------------------------------------------------------------

    def latest(self, limit: int = 1) -> List[SensorReading]:
        """Return the *limit* most recent readings, oldest first."""
        cur = self._conn.execute(
            "SELECT timestamp, temperature_c, humidity_pct, co2_ppm FROM readings"
            " ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return [
            SensorReading(timestamp=t, temperature_c=t1, humidity_pct=h, co2_ppm=c)
            for (t, t1, h, c) in reversed(rows)
        ]

    def all(self) -> List[SensorReading]:
        """Return every stored reading, oldest first."""
        cur = self._conn.execute(
            "SELECT timestamp, temperature_c, humidity_pct, co2_ppm FROM readings ORDER BY timestamp"
        )
        return [
            SensorReading(timestamp=t, temperature_c=t1, humidity_pct=h, co2_ppm=c)
            for (t, t1, h, c) in cur.fetchall()
        ]

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0])

    # -- export ---------------------------------------------------------------

    def to_csv(self, dest: Union[str, Path]) -> Path:
        """Export all readings to *dest* as CSV; returns the written path."""
        dest = _coerce(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["timestamp", "temperature_c", "humidity_pct", "co2_ppm"])
            for r in self.all():
                writer.writerow([r.timestamp, r.temperature_c, r.humidity_pct, r.co2_ppm])
        return dest

    # -- lifecycle -------------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Storage":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
