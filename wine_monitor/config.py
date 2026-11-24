"""Application configuration.

Settings live in a small JSON file (default ``wine-monitor.json``) so the app
can be tuned per install without touching code. Missing values fall back to
sensible defaults; an unreadable or invalid file degrades to defaults rather
than crashing, and the first start writes the default file so the user can
discover the options.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

from wine_monitor.sensors import Thresholds

DEFAULT_CONFIG_PATH = Path("wine-monitor.json")


@dataclass
class Config:
    """All runtime-tunable settings for Wine Monitor."""

    # Where readings are persisted.
    db_path: str = "data/wine_monitor.db"
    # GUI tick interval in milliseconds.
    tick_ms: int = 1000
    # Thresholds for alerts.
    temp_min_c: float = 15.0
    temp_max_c: float = 25.0
    humidity_min_pct: float = 30.0
    humidity_max_pct: float = 80.0
    # Notification behaviour (see wine_monitor.notify).
    notify_dedupe: bool = True
    notify_quiet_minutes: float = 30.0
    # Optional SMTP email alerts (all empty = disabled).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: str = ""

    def thresholds(self) -> Thresholds:
        return Thresholds(
            temp_min_c=self.temp_min_c,
            temp_max_c=self.temp_max_c,
            humidity_min_pct=self.humidity_min_pct,
            humidity_max_pct=self.humidity_max_pct,
        )

    # -- serialization ------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Build a Config from a dict, ignoring unknown keys and keeping
        defaults for missing ones (forward/backward compatible)."""
        valid = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        kwargs = {k: v for k, v in data.items() if k in valid}
        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Config":
        """Load config from *path*.

        * File missing  → returns defaults and writes them to *path*
          (best effort; a failure to write is not an error).
        * File invalid  → returns defaults and a warning is printed.
        """
        p = Path(path)
        if not p.exists():
            cfg = cls()
            cfg.save(p)
            return cfg
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("config root must be a JSON object")
            return cls.from_dict(data)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            print(f"[config] {p} is invalid ({exc}); using defaults.")
            return cls()

    def save(self, path: Union[str, Path]) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        return p
