import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

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
