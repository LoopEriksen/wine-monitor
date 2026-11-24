# Phase 2 – Windows ↔ Raspberry Pi Link

## Context

Phase 1 (this repo's current state) is a **self‑contained, fully simulated**
monitor: the Windows GUI, storage, alerts, and installer all run on
simulated hardware. **Windows is the intended device**, so Phase 2's job is
to make the Windows app talk to the *real* Raspberry Pi that holds the
sensors and relays — and to add the AI wine‑expert chat.

The architecture is already set up for this: everything on the Pi side goes
through the `HardwareBackend` interface, and the Windows side needs a
`NetworkHardwareBackend` that speaks the same interface over HTTP/WebSocket.
No other code changes are required.

## Goal
Connect the existing Windows GUI to the Raspberry Pi host so it can:
1. **Read** live sensor data (temperature, humidity, CO₂) over the network.
2. **Control** actuators (heater, fan, pump) from the Windows GUI.
3. **Chat** with a local AI wine expert running on the Pi.

## Components
1. **Pi‑side API** (`wine_monitor/api/`) — a FastAPI service that:
   - `GET  /readings` and `GET /readings/stream` (SSE or WebSocket) for live data.
   - `POST /actuator/{heater|fan|pump}` with `{"on": true|false}` for control.
   - `POST /ask` with `{"question": "..."}` → `{"answer": "..."}` for the AI expert.
   - Authenticates with a short‑lived token or basic auth. **Do not expose
     the Pi to the internet** — LAN only.
2. **Pi AI server** (`wine_monitor/ai_server.py`) — wraps a local LLM
   (Ollama or similar) for the wine‑expert endpoint. Keep inference
   lightweight; use async handlers.
3. **Windows `NetworkHardwareBackend`** — a `HardwareBackend`
   implementation that reads from and writes to the Pi API. The GUI already
   consumes the interface, so this is the only Windows‑side change.
4. **Configuration** — a `pi_host` / `pi_port` / `token` field in
   `wine-monitor.json`. When set, the app uses the network backend; when
   absent, it falls back to the simulator (so the app always runs).
5. **Packaging** — keep the double‑click `install.bat`; optionally add a
   PyInstaller single‑exe build later.

## Security
- LAN only; bind the API to the Pi's LAN IP, not `0.0.0.0` on a public face.
- Short‑lived token or basic auth; store the token in the Windows config file.
- Rate‑limit actuator commands to avoid relay chatter.

## Timeline
- Week 1‑2: Pi API (readings + actuator) + test with a script.
- Week 3: `NetworkHardwareBackend` on Windows; end‑to‑end with a real Pi.
- Week 4: AI expert endpoint + chat UI in the Windows app.
- Week 5: Integration test, auth, and error handling.
- Week 6: Packaging, docs, release.

## Deliverables
- `wine_monitor/api/` — FastAPI service (readings, actuators, ask).
- `wine_monitor/ai_server.py` — async LLM inference loop.
- `wine_monitor/network_backend.py` — Windows `HardwareBackend` over the API.
- `wine-monitor.json` gains `pi_host` / `pi_port` / `token` fields.
- Updated `README.md` / `docs/install.md` with a "Connect your Pi" section.

## Acceptance criteria
- Windows GUI shows **live Pi sensor data** (not the simulator) when
  `pi_host` is configured.
- Toggling the heater/fan/pump in the GUI flips the **real relays** on the Pi.
- The AI chat returns answers from the Pi's local LLM.
- With `pi_host` unset, the app still runs on the simulator (Phase 1 behavior).
