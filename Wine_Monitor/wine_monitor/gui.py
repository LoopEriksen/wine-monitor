import importlib.util
import subprocess
import sys

# ---------------------------------------------------------------------------
# Dependency check & auto‑install on first run
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = [
    "tkinter",  # stdlib – may be missing on minimal Linux installs
    "matplotlib",
    "requests",
]

def _is_package_available(name: str) -> bool:
    """Return True if *name* is importable.

    ``importlib.util.find_spec`` works for standard library modules and
    pip‑installed packages. It will return ``None`` if the module cannot be
    found.
    """
    return importlib.util.find_spec(name) is not None

def _prompt_and_install_missing() -> None:
    """Check for missing dependencies and try to install them.

    The function will:
    1. Detect which packages from ``REQUIRED_PACKAGES`` are missing.
    2. If *tkinter* is missing, it will warn the user and exit because it
       cannot create a GUI dialog.
    3. For other missing packages, it will ask the user to allow an
       automatic ``pip install``.  After successful installation the
       application will exit and the user can restart it.
    """
    missing = [pkg for pkg in REQUIRED_PACKAGES if not _is_package_available(pkg)]
    if not missing:
        return
    # Tell the user which packages are missing.
    missing_str = "\n".join(f"- {p}" for p in missing)
    print("The Wine Fermentation Monitor requires the following packages: \n" + missing_str)
    if "tkinter" in missing:
        print("tkinter is not installable via pip on this system. Please install it manually (e.g., using your distro's package manager).")
        sys.exit(1)
    # Ask if we should attempt pip install
    try:
        ans = input("Install missing packages now? (y/n): ")
    except EOFError:
        ans = "n"
    if ans.lower() != "y":
        print("Installation aborted. Exiting.")
        sys.exit(1)
    # Install all missing packages with pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("Dependencies installed. Please restart the app.")
    except Exception as exc:
        print(f"Failed to install packages: {exc}\nRun 'pip install' manually.")
    sys.exit(0)

# Run the dependency check before importing GUI libraries
_prompt_and_install_missing()

import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random
from datetime import datetime
import threading
import requests
from .ai_client import query_ai

class SensorSimulator:
    def __init__(self):
        self.history = []  # list of tuples (timestamp, humidity, temp_wine, temp_outside)

    def read_sensors(self):
        # Replace with actual sensor reads
        humidity = random.uniform(30, 80)
        temp_wine = random.uniform(15, 25)
        temp_outside = random.uniform(10, 30)
        timestamp = datetime.now()
        self.history.append((timestamp, humidity, temp_wine, temp_outside))
        # Keep history length limited
        if len(self.history) > 2000:
            self.history.pop(0)
        return timestamp, humidity, temp_wine, temp_outside

class App:
    def __init__(self, root):
        self.root = root
        root.title("Wine Fermentation Monitor")
        self.sensor = SensorSimulator()

        # Current readings frame
        readings_frame = ttk.LabelFrame(root, text="Current Readings")
        readings_frame.pack(fill="x", padx=5, pady=5)

        self.humidity_var = tk.StringVar(value="N/A")
        self.temp_wine_var = tk.StringVar(value="N/A")
        self.temp_outside_var = tk.StringVar(value="N/A")
        ttk.Label(readings_frame, text="Humidity:").grid(row=0, column=0, sticky="e")
        ttk.Label(readings_frame, textvariable=self.humidity_var).grid(row=0, column=1, sticky="w")
        ttk.Label(readings_frame, text="Wine Temp:").grid(row=1, column=0, sticky="e")
        ttk.Label(readings_frame, textvariable=self.temp_wine_var).grid(row=1, column=1, sticky="w")
        ttk.Label(readings_frame, text="Outside Temp:").grid(row=2, column=0, sticky="e")
        ttk.Label(readings_frame, textvariable=self.temp_outside_var).grid(row=2, column=1, sticky="w")

        # Plot frame
        plot_frame = ttk.LabelFrame(root, text="Trend")
        plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.fig, self.axs = plt.subplots(3, 1, figsize=(6, 8), sharex=True)
        self.fig.tight_layout(pad=3)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Button to open AI chat window
        chat_button = ttk.Button(root, text="Wine Expert Chat", command=self.open_chat_window)
        chat_button.pack(pady=5)

        self.update_interval = 750  # ms
        self.update_loop()

    def update_loop(self):
        # Read sensors
        ts, hum, temp_w, temp_o = self.sensor.read_sensors()
        # Update current readings
        self.humidity_var.set(f"{hum:.1f} %")
        self.temp_wine_var.set(f"{temp_w:.1f} °C")
        self.temp_outside_var.set(f"{temp_o:.1f} °C")

        # Update plots
        times = [t for t, _, _, _ in self.sensor.history]
        hums = [h for _, h, _, _ in self.sensor.history]
        twines = [tw for _, _, tw, _ in self.sensor.history]
        toffs = [to for _, _, _, to in self.sensor.history]
        # Convert times to timestamps relative to first entry
        if times:
            t0 = times[0]
            x = [(t - t0).total_seconds() / 60 for t in times]  # minutes
            self.axs[0].clear()
            self.axs[0].plot(x, hums, color="blue")
            self.axs[0].set_ylabel("Humidity %")
            self.axs[0].set_xlim(left=0, right=max(x))
            self.axs[0].grid(True)

            self.axs[1].clear()
            self.axs[1].plot(x, twines, color="red")
            self.axs[1].set_ylabel("Wine Temp °C")
            self.axs[1].grid(True)

            self.axs[2].clear()
            self.axs[2].plot(x, toffs, color="green")
            self.axs[2].set_ylabel("Outside Temp °C")
            self.axs[2].set_xlabel("Minutes")
            self.axs[2].grid(True)

            self.fig.canvas.draw()

        # Schedule next update
        self.root.after(self.update_interval, self.update_loop)

    # ---------------------------------------------------------------------
    # AI chat window
    # ---------------------------------------------------------------------
    def open_chat_window(self):
        """Open a popup window for the user to chat with the AI wine expert."""
        chat_win = tk.Toplevel(self.root)
        chat_win.title("Wine Expert Chat")
        chat_win.geometry("400x300")
        chat_win.resizable(False, False)

        # Conversation display
        text_area = tk.Text(chat_win, state="disabled", wrap="word")
        text_area.pack(expand=True, fill="both", padx=5, pady=5)

        # Input field
        entry = ttk.Entry(chat_win)
        entry.pack(fill="x", padx=5, pady=5)
        entry.focus_set()

        def on_enter(event=None):
            question = entry.get().strip()
            if not question:
                return
            # Append user question to chat
            self._append_text(text_area, f"You: {question}\n")
            entry.delete(0, "end")
            # Query AI in background thread to keep UI responsive
            threading.Thread(target=self._chat_query, args=(question, text_area), daemon=True).start()

        entry.bind("<Return>", on_enter)

    def _chat_query(self, question, text_area):
        try:
            answer = query_ai(question)
            self._append_text(text_area, f"Wine Expert: {answer}\n")
        except Exception as e:
            self._append_text(text_area, f"Error: {e}\n")

    def _append_text(self, widget, text):
        widget.configure(state="normal")
        widget.insert("end", text)
        widget.configure(state="disabled")
        widget.see("end")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
