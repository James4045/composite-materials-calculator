# main.py
from PyQt6.QtWidgets import QApplication
import sys
from ui_main import SoundInsulationUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundInsulationUI()
    window.show()
    sys.exit(app.exec())