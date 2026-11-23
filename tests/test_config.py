"""Tests for :mod:`wine_monitor.config`."""

from __future__ import annotations

import json

import pytest

from wine_monitor.config import Config, DEFAULT_CONFIG_PATH


def test_defaults():
    c = Config()
    assert c.tick_ms == 1000
    assert c.db_path == "data/wine_monitor.db"
    t = c.thresholds()
    assert t.temp_min_c == 15.0 and t.temp_max_c == 25.0


def test_load_missing_file_writes_defaults(tmp_path):
    p = tmp_path / "nope.json"
    c = Config.load(p)
    assert c == Config()
    assert p.exists()
    on_disk = json.loads(p.read_text())
    assert on_disk["tick_ms"] == 1000


def test_load_roundtrip(tmp_path):
    p = tmp_path / "cfg.json"
    c = Config(tick_ms=250, temp_min_c=18.0, smtp_host="mail.example")
    c.save(p)
    back = Config.load(p)
    assert back.tick_ms == 250
    assert back.temp_min_c == 18.0
    assert back.smtp_host == "mail.example"


def test_unknown_keys_ignored(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"tick_ms": 100, "mystery_key": "x", "old_option": 1}))
    c = Config.load(p)
    assert c.tick_ms == 100
    assert c == Config(tick_ms=100)


def test_invalid_file_falls_back_to_defaults(tmp_path, capsys):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    c = Config.load(p)
    assert c == Config()
    assert "invalid" in capsys.readouterr().out


def test_non_object_root_falls_back(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("[1, 2, 3]")
    c = Config.load(p)
    assert c == Config()


def test_thresholds_mapping():
    c = Config(temp_min_c=1.0, temp_max_c=2.0, humidity_min_pct=3.0, humidity_max_pct=4.0)
    t = c.thresholds()
    assert (t.temp_min_c, t.temp_max_c, t.humidity_min_pct, t.humidity_max_pct) == (1.0, 2.0, 3.0, 4.0)


def test_default_config_path_is_repo_relative():
    # Sanity: the default lives next to wherever the app is launched from.
    assert str(DEFAULT_CONFIG_PATH) == "wine-monitor.json"
