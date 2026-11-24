# Installing Wine Monitor

A beginner-friendly guide. **Windows is the primary target** — it's your
intended device. (Linux/Raspberry Pi notes are at the end.)

Two things to know before you start:

- **Downloading from GitHub** — you just need to download the ZIP. No
  "git" knowledge required (git is only for people who want to change the
  code).
- **A "virtual environment" (venv)** — a self-contained folder that holds
  the app's Python libraries so they don't clash with anything else on your
  computer. The installer creates it for you; you don't need to understand
  it.

---

## Option A — Windows (recommended, ~2 minutes)

### 1. Install Python (one time only)

1. Go to <https://www.python.org/downloads/> and click the big yellow
   **Download Python 3.x** button.
2. Run the installer. **Important:** tick the box at the bottom that says
   **Add python.exe to PATH**, then click **Install Now**.
3. Done. (You only need this once; future installs skip straight to step 2.)

### 2. Download Wine Monitor

1. Go to <https://github.com/LoopEriksen/wine-monitor>
2. Click the green **Code** button (top right of the file list) →
   **Download ZIP**.
3. Unzip it to a folder you'll keep, e.g. `C:\WineMonitor`.
   (Right-click the ZIP → **Extract All…**)

### 3. Run the installer

Double-click **`install.bat`** inside the folder. A console window opens and
runs 4 steps: check Python → create the venv → install the app → create
launchers. It ends with a "Done!" summary. (If Windows SmartScreen asks
"Windows protected your PC", click **More info** → **Run anyway** — it's a
script you downloaded from the project page.)

### 4. Start the app

- Double-click **`Start Wine Monitor.vbs`** in the folder — the GUI opens
  with no console window.
- Or: **Start Menu → Wine Monitor** (the installer creates the shortcut).

### 5. First run

On first start the app creates **`wine-monitor.json`** next to the folder —
your settings file. Open it in Notepad to change:

| Setting | What it does |
|---|---|
| `temp_min_c` / `temp_max_c` | Temperature alert range (°C) |
| `humidity_min_pct` / `humidity_max_pct` | Humidity alert range (%) |
| `tick_ms` | How often it samples (1000 = 1/sec) |
| `smtp_host`, `smtp_user`, `smtp_password`, `smtp_to` | Fill in to get email alerts (empty = off) |

Save, then restart the app.

**Useful extras**

- **Terminal version** (shows readings as plain text — handy on a machine
  without a display, or if you want to watch it live):
  ```bat
  cd C:\WineMonitor
  .venv\Scripts\wine-monitor.exe --headless
  ```
  Stop it with `Ctrl+C`.
- **Data** is saved in `data\wine_monitor.db` (SQLite). You can also export
  any time from the GUI's **Export CSV…** button.
- **Updating later:** download a fresh ZIP, replace the folder contents
  (keep `wine-monitor.json` and `data\` if you want your settings/history),
  double-click `install.bat` again.
- **Uninstall:** delete the folder, the `Start Wine Monitor.vbs` file, and
  the Start Menu shortcut.

---

## Option B — Windows, manual (what install.bat does by hand)

Open **Command Prompt** (or PowerShell):

```bat
cd C:\WineMonitor
py -3 -m venv .venv
.venv\Scripts\activate        :: "(.venv)" appears in your prompt
pip install -e ".[gui]"
wine-monitor                  :: the app
```

(`py -3` is Windows' Python launcher. `deactivate` exits the venv.)

---

## Option C — Linux / Raspberry Pi

```bash
# first time only:
sudo apt update && sudo apt install -y python3 python3-venv

cd wine-monitor
./install.sh                 # normal install
./install.sh --systemd       # also start at boot (Pi with a desktop)
./install.sh --systemd --headless   # headless Pi: terminal loop at boot
wine-monitor                 # run
```

On a Raspberry Pi, `install.sh` also installs the hardware extras
(`RPi.GPIO`, `gpiozero`) so the real GPIO backend can be used there.

## How Windows fits the hardware story

The fermentation bay is the Raspberry Pi (it has the GPIO pins and the
sensors). Your **Windows machine runs the monitoring GUI** — today on the
built-in simulator, and from Phase 2 onward connected to the Pi over your
network to show *real* readings and send actuator commands (heater, fan,
pump). That split is by design: see
[phase2-companion-windows.md](phase2-companion-windows.md).

Because all hardware access goes through one `HardwareBackend` interface,
the Windows app never needs `RPi.GPIO` — that's why `install.bat` skips the
`hardware` extra (it would simply fail to install on Windows).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `install.bat` says "Python was not found" | Install Python from python.org (step 1), tick "Add to PATH", run it again |
| "requires 3.10 or newer" | You have an old Python; install a newer one and re-run |
| SmartScreen warning on install.bat | More info → Run anyway (or right-click → Properties → "Unblock") |
| `wine-monitor` works in terminal but no window appears | Windows: make sure the GUI can create a window; try `wine-monitor` from a terminal to see the error |
| pip fails with a network/SSL error | Antivirus or proxy; retry, or install manually (Option B) to see the exact error |
| App shows old data after updating | The DB is `data\wine_monitor.db` — delete or export it if you want a clean slate |
| Headless Pi: GUI fails at boot | Use `./install.sh --systemd --headless` |

## Where things are

| File | What |
|---|---|
| `install.bat` | Windows installer (double-click) |
| `install.sh` | Linux/Pi installer |
| `wine-monitor.json` | Your settings (created on first run) |
| `data\wine_monitor.db` | Recorded readings (SQLite) |
| `Start Wine Monitor.vbs` | Double-click launcher (Windows) |
