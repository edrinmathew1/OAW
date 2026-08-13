# ─────────────────────────────────────────────
#  cli.py — PyQt6 GUI Application (Requirements #2 & #3)
#
#  Features Single-Window Architecture:
#    • Screen 0: AuthView (Login & Registration with 7 RegEx functions & Exception handling)
#    • Screen 1: AgentView (ChatGPT-style Chat, ReAct Trace Panel, File Attach Badge)
#    • 4 Layout Managers: QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter
#    • 5 PyQt Widgets: QLineEdit, QTextEdit, QPushButton, QLabel, QStackedWidget/QTabWidget
#    • 5 Signal-Slot Connections
#    • 3 Event Handling Overrides (keyPressEvent, closeEvent, enterEvent)
# ─────────────────────────────────────────────

import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QSplitter, QFileDialog, QMessageBox, QFormLayout,
    QStackedWidget, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QKeyEvent, QCloseEvent

from agent.core import ObservableAgent
from tools import WebSearchTool, MemoryTool, CodeExecutionTool, APICallerTool, FileManagementTool, AppLauncherTool
from auth import AuthValidator, ValidationError, load_users, save_users



# ─────────────────────────────────────────────
#  AgentWorker — runs agent.process() off main thread
# ─────────────────────────────────────────────

class AgentWorker(QThread):
    log_signal    = pyqtSignal(dict)
    result_signal = pyqtSignal(dict)

    def __init__(self, agent: ObservableAgent, user_input: str) -> None:
        super().__init__()
        self.agent = agent
        self.user_input = user_input

    def run(self) -> None:
        result = self.agent.process(
            self.user_input,
            on_log=lambda entry: self.log_signal.emit(entry),
        )
        self.result_signal.emit(result)


# ─────────────────────────────────────────────
#  MainWindow — Single-Window Application
# ─────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.user_name: str = "Edrin"
        self.attached_file_path: str | None = None
        self.is_generating: bool = False

        self._init_tools()
        self.agent = ObservableAgent()
        self._build_ui()
        self.worker: AgentWorker | None = None

    def _init_tools(self) -> None:
        """Instantiate tools inheriting from AgentTool."""
        from tools.base import AgentTool
        AgentTool.registry.clear()
        WebSearchTool()
        MemoryTool()
        CodeExecutionTool()
        APICallerTool()
        FileManagementTool()
        AppLauncherTool()


    # ── UI Construction ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Observable Agent Runtime (OAW)")
        self.setMinimumSize(1150, 750)
        self.setStyleSheet(self._stylesheet())

        # QStackedWidget for seamless screen switching (Auth -> Agent)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Screen 0: Auth Screen
        self.stack.addWidget(self._build_auth_view())

        # Screen 1: Agent Runtime Screen
        self.stack.addWidget(self._build_agent_view())

        # Start on Auth View
        self.stack.setCurrentIndex(0)

    # ── Screen 0: Auth View ──────────────────────────────────────────────

    def _build_auth_view(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        auth_box = QWidget()
        auth_box.setFixedSize(440, 520)
        auth_box.setObjectName("authBox")

        box_layout = QVBoxLayout(auth_box)
        box_layout.setContentsMargins(24, 24, 24, 24)

        # Header Title
        title = QLabel("⚡ Observable Agent Runtime")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #8b5cf6; margin-bottom: 4px;")

        subtitle = QLabel("Sign in or create an account to unlock OAW AI Agent")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8; margin-bottom: 16px;")

        box_layout.addWidget(title)
        box_layout.addWidget(subtitle)

        # Error Banner Label
        self.auth_error_label = QLabel("")
        self.auth_error_label.setStyleSheet("color: #f87171; font-size: 12px; font-weight: 600; margin-bottom: 8px;")
        self.auth_error_label.setWordWrap(True)
        self.auth_error_label.setVisible(False)
        box_layout.addWidget(self.auth_error_label)

        # Tab Widget for Login / Register
        self.auth_tabs = QTabWidget()
        self.auth_tabs.addTab(self._build_login_form(), "🔑 Login")
        self.auth_tabs.addTab(self._build_register_form(), "📝 Register")
        box_layout.addWidget(self.auth_tabs)

        layout.addWidget(auth_box)
        return container

    def _build_login_form(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(16, 20, 16, 20)
        form.setSpacing(12)

        self.login_user_input = QLineEdit("edrin")
        self.login_pass_input = QLineEdit("Password123!")
        self.login_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_pass_input.returnPressed.connect(self._handle_inapp_login)

        form.addRow("Username:", self.login_user_input)
        form.addRow("Password:", self.login_pass_input)

        btn_login = QPushButton("Login to OAW")
        btn_login.setObjectName("sendBtn")
        btn_login.clicked.connect(self._handle_inapp_login)
        form.addRow(btn_login)

        btn_guest = QPushButton("🚀 Quick Guest Access")
        btn_guest.setObjectName("actionBtn")
        btn_guest.clicked.connect(self._handle_guest_login)
        form.addRow(btn_guest)

        return widget

    def _build_register_form(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(8)

        self.reg_name_input = QLineEdit()
        self.reg_name_input.setPlaceholderText("e.g. Edrin Mathew")

        self.reg_user_input = QLineEdit()
        self.reg_user_input.setPlaceholderText("e.g. edrin_dev")

        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("e.g. edrin@oaw.io")

        self.reg_pass_input = QLineEdit()
        self.reg_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_pass_input.setPlaceholderText("Min 6 chars (digit & special char)")

        self.reg_phone_input = QLineEdit()
        self.reg_phone_input.setPlaceholderText("10-digit phone number")

        self.reg_dev_input = QLineEdit()
        self.reg_dev_input.setPlaceholderText("DEV-XXXX (e.g. DEV-1001)")

        form.addRow("Full Name:", self.reg_name_input)
        form.addRow("Username:", self.reg_user_input)
        form.addRow("Email:", self.reg_email_input)
        form.addRow("Password:", self.reg_pass_input)
        form.addRow("Phone:", self.reg_phone_input)
        form.addRow("Dev Key:", self.reg_dev_input)

        btn_register = QPushButton("Create Account")
        btn_register.setObjectName("sendBtn")
        btn_register.clicked.connect(self._handle_inapp_registration)
        form.addRow(btn_register)

        return widget

    def _handle_guest_login(self) -> None:

        self.user_name = "Edrin Mathew"
        self.auth_error_label.setVisible(False)
        self.chat.clear()
        self._append_chat("agent", f"Hello {self.user_name}, how can I help you?")
        self.stack.setCurrentIndex(1)

    def _handle_inapp_login(self) -> None:
        user = self.login_user_input.text().strip()
        pwd = self.login_pass_input.text()

        try:
            self.auth_error_label.setVisible(False)
            if not user or not pwd:
                raise ValidationError("Please enter both Username and Password.")

            users = load_users()
            if user not in users or users[user]["password"] != pwd:
                raise ValidationError("Invalid Username or Password.")

            self.user_name = users[user].get("full_name", user)
            # Switch to Agent Screen seamlessly!
            self.chat.clear()
            self._append_chat("agent", f"Hello {self.user_name}, how can I help you?")
            self.stack.setCurrentIndex(1)

        except ValidationError as ve:
            self.auth_error_label.setText(f"❌ {str(ve)}")
            self.auth_error_label.setVisible(True)
        except Exception as e:
            self.auth_error_label.setText(f"❌ Error: {str(e)}")
            self.auth_error_label.setVisible(True)

    def _handle_inapp_registration(self) -> None:
        try:
            self.auth_error_label.setVisible(False)
            full_name = AuthValidator.format_full_name(self.reg_name_input.text())
            username = AuthValidator.validate_username(self.reg_user_input.text())
            email = AuthValidator.validate_email(self.reg_email_input.text())
            pwd = AuthValidator.validate_password(self.reg_pass_input.text())
            phone = AuthValidator.validate_phone(self.reg_phone_input.text())
            dev_key = AuthValidator.validate_dev_key(self.reg_dev_input.text())

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

            self.user_name = full_name
            # Switch to Agent Screen seamlessly!
            self.chat.clear()
            self._append_chat("agent", f"Hello {self.user_name}, how can I help you?")
            self.stack.setCurrentIndex(1)

        except ValidationError as ve:
            self.auth_error_label.setText(f"❌ {str(ve)}")
            self.auth_error_label.setVisible(True)
        except Exception as e:
            self.auth_error_label.setText(f"❌ Error: {str(e)}")
            self.auth_error_label.setVisible(True)


    # ── Screen 1: Agent View ─────────────────────────────────────────────

    def _build_agent_view(self) -> QWidget:
        central_agent = QWidget()
        root = QHBoxLayout(central_agent)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._make_splitter())
        return central_agent

    def _make_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([720, 430])
        splitter.setHandleWidth(1)
        return splitter

    def _build_left_panel(self) -> QWidget:
        left = QWidget()
        left.setObjectName("leftPanel")
        layout = QVBoxLayout(left)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Widget
        header = QWidget()
        header.setObjectName("header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Observable Agent Runtime")
        title.setObjectName("headerTitle")
        
        is_online = self.agent.check_ollama()
        status_str = "● Connected" if is_online else "○ Offline"
        status_color = "#34d399" if is_online else "#f87171"

        self.status_badge = QLabel(f'<span style="color:{status_color}">{status_str}</span>  •  {self.agent.model}')
        self.status_badge.setObjectName("modelBadge")

        clear_btn = QPushButton("Clear Chat")
        clear_btn.setObjectName("actionBtn")
        clear_btn.clicked.connect(self._clear_chat)

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("actionBtn")
        logout_btn.clicked.connect(self._logout)

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(clear_btn)
        h_layout.addWidget(logout_btn)
        h_layout.addWidget(self.status_badge)
        layout.addWidget(header)

        # Chat Area
        self.chat = QTextEdit()
        self.chat.setObjectName("chatArea")
        self.chat.setReadOnly(True)
        layout.addWidget(self.chat, 1)

        # Input Container
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        ic_layout = QVBoxLayout(input_container)
        ic_layout.setContentsMargins(16, 8, 16, 16)
        ic_layout.setSpacing(6)

        # Attachment Pill Widget
        self.pill_widget = QWidget()
        self.pill_widget.setObjectName("pillWidget")
        self.pill_widget.setVisible(False)
        pw_layout = QHBoxLayout(self.pill_widget)
        pw_layout.setContentsMargins(10, 4, 10, 4)

        self.pill_label = QLabel("📎 attached_file.txt")
        self.pill_label.setObjectName("pillLabel")

        self.remove_file_btn = QPushButton("✕")
        self.remove_file_btn.setObjectName("removeFileBtn")
        self.remove_file_btn.setFixedSize(18, 18)
        self.remove_file_btn.clicked.connect(self._remove_attached_file)

        pw_layout.addWidget(self.pill_label)
        pw_layout.addWidget(self.remove_file_btn)
        pw_layout.addStretch()
        ic_layout.addWidget(self.pill_widget)

        # Input Bar Row
        input_bar = QWidget()
        input_bar.setObjectName("inputBar")
        i_layout = QHBoxLayout(input_bar)
        i_layout.setContentsMargins(0, 0, 0, 0)
        i_layout.setSpacing(10)

        self.attach_btn = QPushButton("📎 Attach")
        self.attach_btn.setObjectName("attachBtn")
        self.attach_btn.clicked.connect(self._attach_file)

        self.input = QLineEdit()
        self.input.setObjectName("inputField")
        self.input.setPlaceholderText("Ask anything or give instructions for attached file...")
        self.input.returnPressed.connect(self._on_send_click)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.clicked.connect(self._on_send_click)

        i_layout.addWidget(self.attach_btn)
        i_layout.addWidget(self.input)
        i_layout.addWidget(self.send_btn)
        ic_layout.addWidget(input_bar)

        layout.addWidget(input_container)
        return left

    def _build_right_panel(self) -> QWidget:
        right = QWidget()
        right.setObjectName("rightPanel")
        layout = QVBoxLayout(right)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Trace Header
        trace_header_widget = QWidget()
        trace_header_widget.setObjectName("traceHeaderWidget")
        th_layout = QHBoxLayout(trace_header_widget)
        th_layout.setContentsMargins(16, 12, 16, 12)

        trace_header = QLabel("Execution Trace")
        trace_header.setObjectName("traceHeader")

        clear_trace_btn = QPushButton("Clear Trace")
        clear_trace_btn.setObjectName("actionBtn")
        clear_trace_btn.clicked.connect(self._clear_trace)

        th_layout.addWidget(trace_header)
        th_layout.addStretch()
        th_layout.addWidget(clear_trace_btn)
        layout.addWidget(trace_header_widget)

        # Trace Log
        self.trace = QTextEdit()
        self.trace.setObjectName("traceArea")
        self.trace.setReadOnly(True)
        layout.addWidget(self.trace, 1)

        # Tools Panel
        tools_widget = QWidget()
        tools_widget.setObjectName("toolsWidget")
        t_layout = QVBoxLayout(tools_widget)
        t_layout.setContentsMargins(16, 12, 16, 12)
        t_layout.setSpacing(6)

        tools_label = QLabel("Registered Tools")
        tools_label.setObjectName("toolsLabel")
        t_layout.addWidget(tools_label)

        for tool in self.agent.tools:
            item = QLabel(f"<b>◆ {tool.name}</b><br><span style='color:#64748b;font-size:11px;'>{tool.description}</span>")
            item.setObjectName("toolItem")
            t_layout.addWidget(item)

        layout.addWidget(tools_widget)
        return right

    # ── Requirement #3: Event Handling Overrides ─────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Pressing Esc cancels generation, Ctrl+L clears chat."""
        if event.key() == Qt.Key.Key_Escape:
            if self.is_generating and self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
                self._append_trace('<span style="color:#ef4444;font-weight:600">[CANCELLED] Stopped via ESC key.</span>')
                self._on_done()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_L:
            self._clear_chat()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Prompt confirmation dialog box before exiting (Requirement #3)."""
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit Observable Agent Runtime?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)

    # ── Action Handlers ──────────────────────────────────────────────────

    def _logout(self) -> None:
        self.stack.setCurrentIndex(0)

    def _attach_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Record or Text File", "", "Text/Data Files (*.txt *.csv);;All Files (*)"
        )
        if file_path:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(data_dir, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(data_dir, filename)
            
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.copy(file_path, dest_path)

            self.attached_file_path = dest_path
            self.pill_label.setText(f"📎 {filename}")
            self.pill_widget.setVisible(True)

    def _remove_attached_file(self) -> None:
        self.attached_file_path = None
        self.pill_widget.setVisible(False)

    def _on_send_click(self) -> None:
        if self.is_generating:
            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
            self._append_trace('<span style="color:#ef4444;font-weight:600">[CANCELLED] Generation stopped by user.</span>')
            self._on_done()
        else:
            self._send()

    def _clear_chat(self) -> None:
        self.chat.clear()
        self._append_chat("agent", f"Hello {self.user_name}, how can I help you?")

    def _clear_trace(self) -> None:
        self.trace.clear()

    def _send(self) -> None:
        text = self.input.text().strip()
        if not text and not self.attached_file_path:
            return
        if self.worker is not None and self.worker.isRunning():
            return

        display_text = text
        full_task_text = text

        if self.attached_file_path:
            filename = os.path.basename(self.attached_file_path)
            display_text = f"<b>📎 {filename}</b><br>{text if text else 'Process attached file'}"
            full_task_text = f'process file "{self.attached_file_path}": {text if text else "process file"}'

        self.input.clear()
        self.is_generating = True
        self.send_btn.setText("⏹ Stop")
        self.send_btn.setStyleSheet("background-color: #ef4444; color: white;")
        
        self._append_chat("user", display_text)
        self._append_trace("─" * 36)

        self.worker = AgentWorker(self.agent, full_task_text)
        self.worker.log_signal.connect(self._on_log)
        self.worker.result_signal.connect(self._on_result)
        self.worker.finished.connect(self._on_done)
        self.worker.start()

    def _on_log(self, entry: dict) -> None:
        color_map = {
            "INPUT":         "#64748b",
            "THINKING":      "#a78bfa",
            "LLM":           "#60a5fa",
            "TOOL SELECTED": "#34d399",
            "TOOL RESULT":   "#fbbf24",
            "DONE":          "#6ee7b7",
        }
        color = color_map.get(entry["event"], "#94a3b8")
        self._append_trace(
            f'<span style="color:#475569">[{entry["time"]}]</span> '
            f'<span style="color:{color};font-weight:600">{entry["event"]}</span> '
            f'<span style="color:#cbd5e1">{entry["detail"]}</span>'
        )

    def _on_result(self, result: dict) -> None:
        if result.get("tool_result"):
            # Route raw tool output to Execution Trace side-panel for full observability
            tool_name = result.get("tool_used", "Tool")
            tool_res = str(result.get("tool_result"))
            preview = tool_res[:400] + "..." if len(tool_res) > 400 else tool_res
            self._append_trace(
                f'<span style="color:#34d399;font-weight:600">[{tool_name}] Observation:</span><br>'
                f'<span style="color:#cbd5e1;font-size:11px;">{preview}</span>'
            )
        self._append_chat("agent", result["response"])


    def _on_done(self) -> None:
        self.worker = None
        self.is_generating = False
        self.send_btn.setText("Send")
        self.send_btn.setStyleSheet("background-color: #7c3aed; color: white;")
        self.attached_file_path = None
        self.pill_widget.setVisible(False)

    def _append_chat(self, role: str, text: str) -> None:
        role_styles = {
            "user":  ("#1e293b", "#8b5cf6", "You"),
            "agent": ("#0f172a", "#a78bfa", "Agent"),
            "tool":  ("#0f1f1a", "#34d399", "Tool"),
        }
        bg, accent, label = role_styles.get(role, ("#1e293b", "#94a3b8", role))
        
        formatted = (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&lt;b&gt;", "<b>")
            .replace("&lt;/b&gt;", "</b>")
            .replace("&lt;br&gt;", "<br>")
            .replace("\n", "<br>")
        )
        html = (
            f'<div style="margin:8px 0;padding:12px 16px;'
            f'background:{bg};border-left:3px solid {accent};border-radius:8px">'
            f'<div style="color:{accent};font-size:11px;font-weight:700;'
            f'margin-bottom:4px;letter-spacing:1px">{label.upper()}</div>'
            f'<div style="color:#e2e8f0;font-size:14px;line-height:1.6">{formatted}</div>'
            f'</div>'
        )
        self.chat.append(html)
        self.chat.moveCursor(QTextCursor.MoveOperation.End)

    def _append_trace(self, html: str) -> None:
        self.trace.append(
            f'<div style="font-family:monospace;font-size:12px;line-height:1.8;'
            f'color:#94a3b8">{html}</div>'
        )
        self.trace.moveCursor(QTextCursor.MoveOperation.End)

    def _stylesheet(self) -> str:
        return """
        QMainWindow, QWidget {
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: 'Segoe UI', -apple-system, sans-serif;
        }
        #authBox {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
        }
        #leftPanel  { background-color: #0f172a; }
        #header     { background-color: #0f172a; border-bottom: 1px solid #1e293b; }
        #headerTitle { font-size: 16px; font-weight: 700; color: #f8fafc; }
        #modelBadge {
            font-size: 11px; color: #94a3b8;
            background: #1e293b; padding: 4px 12px; border-radius: 12px;
            border: 1px solid #334155;
        }
        #chatArea {
            background-color: #0f172a; border: none;
            padding: 20px; color: #e2e8f0; font-size: 14px;
        }
        #inputContainer { background-color: #0f172a; border-top: 1px solid #1e293b; }
        #pillWidget {
            background-color: #1e293b; border: 1px solid #334155;
            border-radius: 12px;
        }
        #pillLabel { font-size: 12px; font-weight: 600; color: #a78bfa; }
        #removeFileBtn {
            background-color: transparent; color: #94a3b8;
            border: none; font-size: 12px; font-weight: bold;
        }
        #removeFileBtn:hover { color: #f87171; }
        #attachBtn {
            background-color: #1e293b; color: #e2e8f0;
            border: 1px solid #334155; border-radius: 10px;
            padding: 10px 14px; font-size: 13px; font-weight: 600;
        }
        #attachBtn:hover { background-color: #334155; color: #f8fafc; }
        #inputField {
            background-color: #1e293b; border: 1px solid #334155;
            border-radius: 10px; padding: 10px 16px;
            color: #e2e8f0; font-size: 14px;
        }
        #inputField:focus { border: 1px solid #8b5cf6; }
        #sendBtn {
            background-color: #7c3aed; color: white;
            border: none; border-radius: 10px;
            padding: 10px 22px; font-size: 14px; font-weight: 600;
        }
        #sendBtn:hover { background-color: #6d28d9; }
        #actionBtn {
            background-color: #1e293b; color: #94a3b8;
            border: 1px solid #334155; border-radius: 8px;
            padding: 5px 12px; font-size: 12px; font-weight: 600;
        }
        #actionBtn:hover { background-color: #334155; color: #f8fafc; }
        #rightPanel { background-color: #080f1e; border-left: 1px solid #1e293b; }
        #traceHeaderWidget { border-bottom: 1px solid #1e293b; background-color: #080f1e; }
        #traceHeader {
            font-size: 12px; font-weight: 700; color: #64748b;
            letter-spacing: 1.5px; text-transform: uppercase;
        }
        #traceArea {
            background-color: #080f1e; border: none; padding: 14px;
            font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px;
        }
        #toolsWidget { background-color: #0a1628; border-top: 1px solid #1e293b; }
        #toolsLabel {
            font-size: 11px; font-weight: 700; color: #475569;
            letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px;
        }
        #toolItem { font-size: 12px; color: #64748b; padding: 3px 0; }
        QTabBar::tab { background: #0f172a; color: #94a3b8; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
        QTabBar::tab:selected { background: #7c3aed; color: white; font-weight: bold; }
        QScrollBar:vertical { background: #0f172a; width: 6px; }
        QScrollBar::handle:vertical { background: #334155; border-radius: 3px; }
        QSplitter::handle { background: #1e293b; }
        """
