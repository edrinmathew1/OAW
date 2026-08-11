# ─────────────────────────────────────────────
#  main.py — Primary Entry Point for OAW Desktop Application
#  Flow: Launches AuthDialog (Requirement #2) -> Launches MainWindow (Requirement #3)
# ─────────────────────────────────────────────

import sys
from PyQt6.QtWidgets import QApplication, QDialog
from auth import AuthDialog
from cli import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Step 1: Launch Authentication Dialog (Requirement #2)
    auth_dialog = AuthDialog()
    if auth_dialog.exec() == QDialog.DialogCode.Accepted:
        user_name = auth_dialog.authenticated_user or "Edrin"
        # Step 2: Launch Main Application (Requirement #3)
        window = MainWindow(user_name=user_name)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()