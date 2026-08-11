# ─────────────────────────────────────────────
#  main.py — Primary Entry Point for OAW Desktop Application
#  Single-Window Architecture: Opens MainWindow with QStackedWidget (Auth -> Agent)
# ─────────────────────────────────────────────

import sys
from PyQt6.QtWidgets import QApplication
from cli import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()