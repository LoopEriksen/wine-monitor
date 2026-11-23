#!/usr/bin/env bash
#
# Wine Monitor installer — for Linux (Raspberry Pi and any other Linux box).
#
# What it does (safe to re-run):
#   1. Checks that Python 3.10+ is available.
#   2. Creates a virtual environment in .venv/ (dependencies never touch the
#      system Python).
#   3. Installs Wine Monitor + the GUI extra into the venv
#      (plus hardware extras automatically when running on a Raspberry Pi).
#   4. Creates the default config file wine-monitor.json next to the app.
#   5. Puts a `wine-monitor` command in your PATH (~/.local/bin or /usr/local/bin).
#   6. Optionally installs a systemd service so the GUI starts at boot
#      (pass --systemd; GUI on the Pi needs a desktop session / X, or run
#      headless instead — see the printed notes).
#
# Usage:
#   ./install.sh               # normal install
#   ./install.sh --systemd     # also install the autostart service
#   ./install.sh --headless    # hint the service to run the terminal loop
#
set -euo pipefail

cd "$(dirname "$0")"

SYSTEMD=0
HEADLESS_HINT=0
for arg in "$@"; do
  case "$arg" in
    --systemd) SYSTEMD=1 ;;
    --headless) HEADLESS_HINT=1 ;;
    -h|--help) grep '^# ' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg (try --help)"; exit 1 ;;
  esac
done

say()  { printf '\n\033[1;32m== %s ==\033[0m\n' "$*"; }
warn() { printf '\033[1;33m   ! %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m   x %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
say "1/5 Checking Python"
# ---------------------------------------------------------------------------
if command -v python3 >/dev/null; then
  PY=python3
else
  die "python3 not found. On Raspberry Pi OS: sudo apt update && sudo apt install -y python3 python3-venv"
fi
PYVERSION=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
PYOK=$("$PY" -c 'import sys; print(1 if sys.version_info >= (3, 10) else 0)')
if [ "$PYOK" != "1" ]; then
  die "Python $PYVERSION found, but Wine Monitor needs Python 3.10 or newer."
fi
echo "   Python $PYVERSION at $(command -v $PY)"

# venv module is a separate package on some distros.
if ! "$PY" -c 'import venv' >/dev/null 2>&1; then
  warn "python3-venv is missing; trying to install it (needs sudo)."
  sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv \
    || die "Could not install python3-venv. Run: sudo apt install -y python3-venv"
fi

# matplotlib's Qt5 backend wants a GL library on bare Linux (incl. Pi).
if command -v apt-get >/dev/null && ! ldconfig -p 2>/dev/null | grep -q libEGL; then
  warn "libEGL not found; installing mesa libraries (needed by the GUI)."
  sudo apt-get update -qq && sudo apt-get install -y -qq libegl1 libgl1 \
    || warn "Could not install libegl1/libgl1 automatically — the GUI may need: sudo apt install -y libegl1 libgl1"
fi

# ---------------------------------------------------------------------------
say "2/5 Creating virtual environment (.venv/)"
# ---------------------------------------------------------------------------
if [ -d .venv ]; then
  echo "   .venv already exists — updating it."
else
  "$PY" -m venv .venv
fi
./.venv/bin/python -m pip install --quiet --upgrade pip

# ---------------------------------------------------------------------------
say "3/5 Installing Wine Monitor into .venv"
# ---------------------------------------------------------------------------
ON_PI=0
if [ -f /sys/firmware/devicetree/base/model ]; then
  if grep -qi "raspberry pi" /sys/firmware/devicetree/base/model; then
    ON_PI=1
  fi
fi
EXTRAS="gui,dev"
if [ "$ON_PI" = "1" ]; then
  EXTRAS="gui,hardware,dev"
  echo "   Raspberry Pi detected — including hardware extras (RPi.GPIO, gpiozero)."
fi
./.venv/bin/python -m pip install --quiet ".[$EXTRAS]"
echo "   Installed with extras: $EXTRAS"

# ---------------------------------------------------------------------------
say "4/5 Writing default config (wine-monitor.json)"
# ---------------------------------------------------------------------------
if [ -f wine-monitor.json ]; then
  echo "   wine-monitor.json already exists — leaving it alone."
else
  ./.venv/bin/python -c "from wine_monitor.config import Config; Config().save('wine-monitor.json')"
  echo "   Created wine-monitor.json (edit it to set thresholds, tick rate, email alerts)."
fi
mkdir -p data

# ---------------------------------------------------------------------------
say "5/5 Creating the 'wine-monitor' command"
# ---------------------------------------------------------------------------
VENV_BIN="$PWD/.venv/bin"
LOCAL_BIN="$HOME/.local/bin"
if [ -w "$VENV_BIN/wine-monitor" ]; then
  mkdir -p "$LOCAL_BIN"
  ln -sf "$VENV_BIN/wine-monitor" "$LOCAL_BIN/wine-monitor"
  case ":$PATH:" in
    *":$LOCAL_BIN:"*) echo "   Linked into $LOCAL_BIN (already in your PATH)." ;;
    *)
      echo "   Linked into $LOCAL_BIN — add it to your PATH by appending this to ~/.bashrc:"
      echo "     export PATH=\"\$HOME/.local/bin:\$PATH\""
      ;;
  esac
fi

# ---------------------------------------------------------------------------
# Optional systemd service
# ---------------------------------------------------------------------------
if [ "$SYSTEMD" = "1" ]; then
  say "Installing systemd service (wine-monitor.service)"
  UNIT=/etc/systemd/system/wine-monitor.service
  RUNMODE="$([ "$HEADLESS_HINT" = "1" ] && echo "headless" || echo "gui")"
  sudo tee "$UNIT" >/dev/null <<EOF
[Unit]
Description=Wine Monitor ($RUNMODE)
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
Environment=PATH=$VENV_BIN:/usr/bin:/bin
ExecStart=$VENV_BIN/wine-monitor $([ "$HEADLESS_HINT" = "1" ] && echo "--headless")
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable wine-monitor.service
  echo "   Service enabled. Start now with:  sudo systemctl start wine-monitor"
  echo "   Logs:                             journalctl -u wine-monitor -f"
  [ "$RUNMODE" = "gui" ] && warn "GUI needs a display; on a headless Pi use ./install.sh --systemd --headless"
fi

say "Done! How to run"
echo "   GUI:       wine-monitor          (or: ./.venv/bin/wine-monitor)"
echo "   Terminal:  wine-monitor --headless"
echo "   Config:    $PWD/wine-monitor.json"
echo "   Data:      $PWD/data/wine_monitor.db"
echo "   Uninstall: rm -rf .venv && sudo rm /etc/systemd/system/wine-monitor.service 2>/dev/null || true"
