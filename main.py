# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import CryptoMonitorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoMonitorApp()
    window.show()
    sys.exit(app.exec())
