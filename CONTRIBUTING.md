# Contributing to Wine Monitor

Thanks for helping build this! The goal of the repo layout is simple: keep
the **core testable without hardware**, so anything that can be expressed
without `RPi.GPIO`/`gpiozero` or a display belongs in the `wine_monitor`
package and gets a test.

## Ground rules

1. **Branch off `main`.**
   - Features: `feature/<short-description>`
   - Fixes: `bugfix/<short-description>`
2. **Keep the core pure.** `wine_monitor/` must not import `RPi.GPIO`,
   `gpiozero`, `PyQt5`, or `tkinter`. If you need hardware, put it behind an
   interface (e.g. a `SensorReader` protocol) and provide a simulator
   implementation that tests can use.
3. **Tests are required.** Add or update tests in `tests/` for any change.
   Run locally before opening a PR:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   pytest
   ```
4. **CI must pass.** The workflow runs pytest on Linux, Windows, and macOS
   across Python 3.10–3.13. If a dependency is platform‑specific, make it an
   optional extra (`gui`, `hardware`) rather than a hard dependency.
5. **Small, focused PRs.** One concern per PR; link any issue it closes.
6. **Docs stay in sync.** If behavior or layout changes, update the README
   and `docs/roadmap.md` (tick the box) in the same PR.

## Style

- Python 3.10+, PEP 8.
- Type hints on public functions.
- Docstrings for public classes/functions (Google or NumPy style, be
  consistent within a file).
- Keep dependencies minimal; prefer the standard library.

## Hardware work

Real sensor/actuator code goes in a new module (e.g. `wine_monitor/gpio.py`)
and must:

- Only be imported when available (guard the `import RPi.GPIO` with a
  fallback to the simulator, as `src/main.py` already does).
- Expose the same read/write shape as the simulator so the rest of the app
  never cares which backend is active.
- Be covered by tests that exercise the simulator path.

## Release notes

Releases are tagged `vX.Y.Z`. Keep a short "what changed" note in the tag
message.
