# ─────────────────────────────────────────────
#  auth.py — Login & Registration System (Requirement #2)
#
#  Demonstrates:
#    • All 7 Python RegEx functions: fullmatch, match, search, findall, compile, sub, split
#    • Exception handling & custom validation exceptions
#    • PyQt6 GUI Login and Registration forms with Dialog boxes
# ─────────────────────────────────────────────

import os
import json
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt


USER_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")


class ValidationError(Exception):
    """Custom exception class for user validation errors."""
    pass


class AuthValidator:
    """
    Demonstrates all 7 Python Regular Expression functions for input validation.
    """
    
    # 1. re.compile() — Pre-compiled regex object for Developer ID
    DEV_KEY_PATTERN = re.compile(r"^DEV-\d{4}$")

    @staticmethod
    def validate_username(username: str) -> str:
        # 2. re.sub() — Sanitize extra spaces
        clean_user = re.sub(r"\s+", " ", username).strip()
        # 3. re.match() — Check if username starts with a letter and is 3-20 chars
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{2,19}$", clean_user):
            raise ValidationError("Username must start with a letter and be 3-20 characters long (letters, numbers, underscores).")
        return clean_user

    @staticmethod
    def validate_email(email: str) -> str:
        email = email.strip()
        # 4. re.fullmatch() — Exact match for standard email address
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValidationError("Invalid email address format (e.g. edrin@oaw.io).")
        return email

    @staticmethod
    def validate_password(password: str) -> str:
        # 5. re.search() — Check for required password complexity (digit & special char)
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit (0-9).")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",./<>?]", password):
            raise ValidationError("Password must contain at least one special character.")
        return password

    @staticmethod
    def validate_phone(phone: str) -> str:
        # 6. re.findall() — Extract all digits from phone string
        digits = "".join(re.findall(r"\d+", phone))
        if len(digits) != 10:
            raise ValidationError("Phone number must contain exactly 10 digits.")
        return digits

    @staticmethod
    def validate_dev_key(dev_key: str) -> str:
        dev_key = dev_key.strip()
        # Uses re.compile() object
        if not AuthValidator.DEV_KEY_PATTERN.match(dev_key):
            raise ValidationError("Developer Key must match format DEV-XXXX (e.g. DEV-1001).")
        return dev_key

    @staticmethod
    def format_full_name(name_input: str) -> str:
        # 7. re.split() — Split name by spaces or commas
        parts = re.split(r"[\s,]+", name_input.strip())
        return " ".join(p.capitalize() for p in parts if p)


def load_users() -> dict:
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users(users: dict) -> None:
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# Initial default user for seamless login
def ensure_default_user():
    users = load_users()
    if "edrin" not in users:
        users["edrin"] = {
            "full_name": "Edrin Mathew",
            "email": "edrin@oaw.io",
            "password": "Password123!",
            "phone": "9876543210",
            "dev_key": "DEV-1001"
        }
        save_users(users)


ensure_default_user()


class AuthDialog(QDialog):
    """
    PyQt6 Login and Registration Dialog Box (Requirement #2 & #3).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("OAW — User Authentication")
        self.setMinimumSize(420, 480)
        self.authenticated_user: str | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header Title
        title = QLabel("⚡ Observable Agent Runtime")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #8b5cf6; margin-bottom: 10px;")
        layout.addWidget(title)

        # Tab Widget for Login / Registration
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_login_tab(), "🔑 Login")
        self.tabs.addTab(self._build_register_tab(), "📝 Register")
        layout.addWidget(self.tabs)

        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
            QLabel { color: #e2e8f0; font-size: 13px; }
            QLineEdit { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 8px; color: #e2e8f0; }
            QLineEdit:focus { border: 1px solid #8b5cf6; }
            QPushButton { background-color: #7c3aed; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #6d28d9; }
            QTabWidget::pane { border: 1px solid #334155; border-radius: 8px; background: #0f172a; }
            QTabBar::tab { background: #1e293b; color: #94a3b8; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #7c3aed; color: white; font-weight: bold; }
        """)

    def _build_login_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(15, 20, 15, 20)
        form.setSpacing(12)

        self.login_user = QLineEdit("edrin")
        self.login_pass = QLineEdit("Password123!")
        self.login_pass.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Username:", self.login_user)
        form.addRow("Password:", self.login_pass)

        btn_login = QPushButton("Login to OAW")
        btn_login.clicked.connect(self._handle_login)
        form.addRow(btn_login)

        return widget

    def _build_register_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(15, 15, 15, 15)
        form.setSpacing(10)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("e.g. Edrin Mathew")

        self.reg_user = QLineEdit()
        self.reg_user.setPlaceholderText("e.g. edrin_dev")

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("e.g. edrin@oaw.io")

        self.reg_pass = QLineEdit()
        self.reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_pass.setPlaceholderText("Min 6 chars (digit & special char)")

        self.reg_phone = QLineEdit()
        self.reg_phone.setPlaceholderText("10-digit mobile number")

        self.reg_dev_key = QLineEdit()
        self.reg_dev_key.setPlaceholderText("DEV-XXXX (e.g. DEV-1001)")

        form.addRow("Full Name:", self.reg_name)
        form.addRow("Username:", self.reg_user)
        form.addRow("Email:", self.reg_email)
        form.addRow("Password:", self.reg_pass)
        form.addRow("Phone:", self.reg_phone)
        form.addRow("Dev Key:", self.reg_dev_key)

        btn_reg = QPushButton("Create Account")
        btn_reg.clicked.connect(self._handle_registration)
        form.addRow(btn_reg)

        return widget

    def _handle_login(self) -> None:
        user = self.login_user.text().strip()
        pwd = self.login_pass.text()

        try:
            if not user or not pwd:
                raise ValidationError("Please fill in both Username and Password.")

            users = load_users()
            if user not in users or users[user]["password"] != pwd:
                raise ValidationError("Invalid Username or Password.")

            self.authenticated_user = users[user].get("full_name", user)
            QMessageBox.information(self, "Success", f"Welcome back, {self.authenticated_user}!")
            self.accept()

        except ValidationError as ve:
            QMessageBox.warning(self, "Login Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"Unexpected error: {str(e)}")

    def _handle_registration(self) -> None:
        try:
            full_name = AuthValidator.format_full_name(self.reg_name.text())
            username = AuthValidator.validate_username(self.reg_user.text())
            email = AuthValidator.validate_email(self.reg_email.text())
            pwd = AuthValidator.validate_password(self.reg_pass.text())
            phone = AuthValidator.validate_phone(self.reg_phone.text())
            dev_key = AuthValidator.validate_dev_key(self.reg_dev_key.text())

            users = load_users()
            if username in users:
                raise ValidationError(f"Username '{username}' is already registered.")

            users[username] = {
                "full_name": full_name,
                "email": email,
                "password": pwd,
                "phone": phone,
                "dev_key": dev_key
            }
            save_users(users)

            QMessageBox.information(
                self, "Registration Successful",
                f"Account created successfully for {full_name}!\nYou can now log in."
            )
            self.tabs.setCurrentIndex(0)

        except ValidationError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
