from PyQt6.QtWidgets import QApplication
import sys
from ui_main import SoundInsulationUI
import matplotlib
import traceback

matplotlib.use("QtAgg")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = SoundInsulationUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"[FATAL ERROR] {e}", flush=True)
        traceback.print_exc()