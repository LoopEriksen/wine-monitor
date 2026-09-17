# Phase 2 – Companion Windows App

## Goal
Build a lightweight Windows application that connects to the Raspberry Pi host, authenticates, and forwards user queries to the local AI wine expert running on the Pi.

## Key Tasks
1. **API Design** – Define a REST/WS endpoint on the Pi that accepts JSON `{"question": "..."}` and returns `{"answer": "..."}`.
2. **Pi‑side AI Server** – Use the existing LLM model (e.g., Ollama, local GPT) to process queries. Keep inference lightweight; use async handlers.
3. **Windows Front‑end** – A simple Win32/WinForms or Electron/Node GUI that:
   - Connects to the Pi IP/port.
   - Provides a chat box.
   - Displays streaming responses.
   - Handles network errors gracefully.
4. **Packaging** – Use PyInstaller or Inno Setup to create an installer.
5. **Security** – Use a short‑lived token or basic auth; do not expose the Pi to the internet.

## Timeline
- Week 1‑2: Implement Pi API + test locally.
- Week 3‑4: Build Windows UI prototype.
- Week 5: Integration test and packaging.
- Week 6: Documentation & release.

## Deliverables
- `wine_monitor/api/ai.py` – Flask/FastAPI endpoint.
- `wine_monitor/ai_server.py` – async inference loop.
- `wincompanion/` – Windows client code and installer scripts.
- Updated `README.md` with phase‑2 section.
