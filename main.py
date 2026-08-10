# ─────────────────────────────────────────────
#  main.py — Main Application Entry Point
#  Launches the Observable Agent Runtime GUI
# ─────────────────────────────────────────────

import sys
from PyQt6.QtWidgets import QApplication
from cli import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()