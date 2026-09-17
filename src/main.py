import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

# Determine whether to use the simulator. On non‑Linux or when SIMULATE env var is set, we import a stub.
SIMULATE = os.getenv("SIMULATE", "0") == "1" or not sys.platform.startswith("linux")
if SIMULATE:
    try:
        from simulator import GPIO  # type: ignore
    except ImportError:
        # Provide a minimal stub if simulator package is missing
        class GPIO:
            OUT = IN = None
            BOARD = BCM = None
            @staticmethod
            def setmode(_):
                pass
            @staticmethod
            def setup(_, mode):
                pass
            @staticmethod
            def output(_, val):
                print(f"[SIMULATE] GPIO output: {val}")
            @staticmethod
            def input(_):
                return 0
    print("Running with GPIO simulator")
else:
    import RPi.GPIO as GPIO
    print("Running on actual Raspberry Pi GPIO")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wine Monitor")
        self.setGeometry(100, 100, 800, 600)
        label = QLabel("Hello, Wine Monitor!", self)
        label.move(50, 50)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
