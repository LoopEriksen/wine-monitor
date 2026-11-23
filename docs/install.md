# Installing Wine Monitor

A beginner-friendly guide to downloading the project from GitHub and running
it on your machine (Raspberry Pi or any Linux desktop). Windows notes at the
end.

Two things to know before you start:

- **GitHub download vs `git clone`** — if you just want to *run* the app,
  download the ZIP (no `git` needed). If you plan to *develop* it, use
  `git clone`.
- **A "virtual environment" (venv)** — a self-contained folder that holds the
  app's Python libraries, so they don't clash with anything else on your
  machine. The installer creates and manages it for you; you don't need to
  understand it, just let the script do its thing.

---

## Option A — One-command install (recommended)

### 1. Download the code

**Easiest (no git):** on
<https://github.com/LoopEriksen/wine-monitor> click the green **Code**
button → **Download ZIP** → unzip it somewhere, e.g. `~/wine-monitor`.

**Or with git:**
```bash
sudo apt update && sudo apt install -y git        # only the first time
git clone https://github.com/LoopEriksen/wine-monitor.git
cd wine-monitor
```

### 2. Install the prerequisites (first time only)

```bash
sudo apt update
sudo apt install -y python3 python3-venv
```
The installer will also try to add `python3-venv` and the GUI graphics
libraries (`libegl1`, `libgl1`) for you — it only needs you to type your
sudo password once.

### 3. Run the installer

```bash
cd wine-monitor
./install.sh
```
What you'll see: Python check → venv created → packages installed → a
`wine-monitor.json` config file written → a `wine-monitor` command linked
into your PATH. (If it tells you to add `~/.local/bin` to your PATH, do
that and open a new terminal.)

### 4. Run it

```bash
wine-monitor                # opens the GUI
wine-monitor --headless     # terminal version (no display needed)
```
That's it. Stop with `Ctrl+C`.

### 5. (Pi only) Start automatically at boot

```bash
./install.sh --systemd             # GUI at boot (needs a desktop session)
./install.sh --systemd --headless  # terminal loop at boot (headless Pi)
```
Then:
```bash
sudo systemctl start wine-monitor      # start now
systemctl status wine-monitor          # is it running?
journalctl -u wine-monitor -f          # watch its output
sudo systemctl stop wine-monitor       # stop it
```

### 6. Configure it

Edit `wine-monitor.json` (plain text):
- `temp_min_c` / `temp_max_c` / `humidity_min_pct` / `humidity_max_pct` —
  the alert thresholds
- `tick_ms` — how often it samples (1000 = once per second)
- `db_path` — where the SQLite log lives
- `smtp_host`, `smtp_user`, `smtp_password`, `smtp_to`, … — fill these in
  to get email alerts (leaving them empty keeps email off)

Save and restart the app.

### Uninstall

```bash
rm -rf wine-monitor          # or wherever you put it
rm ~/.local/bin/wine-monitor # the command
```

---

## Option B — Manual install (what the script does, by hand)

```bash
cd wine-monitor
python3 -m venv .venv
source .venv/bin/activate          # "(.venv)" appears in your prompt
pip install -e ".[gui]"            # add ,hardware on a Raspberry Pi
deactivate
.venv/bin/wine-monitor             # run
```
Useful if you want to see exactly what's happening or the script trips up.

---

## Updating later

If you got it with git:
```bash
cd wine-monitor
git pull
./.venv/bin/pip install -e ".[gui]"   # pick up any dependency changes
```
If you got the ZIP: download the new ZIP, replace the folder contents, and
re-run `./install.sh` (it keeps your venv and config).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python3: command not found` | `sudo apt install -y python3 python3-venv` |
| `No module named venv` | `sudo apt install -y python3-venv` |
| GUI window doesn't appear / `libGL` or `libEGL` errors | `sudo apt install -y libegl1 libgl1` |
| `wine-monitor: command not found` | open a new terminal, or `export PATH="$HOME/.local/bin:$PATH"` |
| Permission denied on `./install.sh` | `chmod +x install.sh` then run it again |
| Pi headless: GUI fails at boot | run with `--headless` (see step 5) — GUIs need a display |

## Windows

The **core** (sensors, alerts, storage) runs on Windows fine — the GUI
(PyQt5) does too, but `install.sh` is for Linux. Manual steps:

```bat
git clone https://github.com/LoopEriksen/wine-monitor.git
cd wine-monitor
py -3 -m venv .venv
.venv\Scripts\activate
pip install -e ".[gui,dev]"
wine-monitor
```
(`py -3` is the Windows Python launcher; install Python 3.10+ from
python.org first, ticking "Add to PATH".) The GPIO extras are intentionally
not installed on Windows — only the simulator runs there, which is exactly
what the hardware abstraction is for.

## Raspberry Pi hardware (future)

Right now the app always runs on the built-in simulator. When the real
sensors and relays are wired up, a GPIO backend will plug into the same
`create_backend()` hook in `wine_monitor/gui.py` and be selected on the Pi
with `WINE_MONITOR_USE_HW=1` — no other code changes.
