# ─────────────────────────────────────────────
#  cli.py — PyQt6 GUI entry point
#
#  Wires together:
#    • Tool instantiation  (self._init_tools)
#    • ObservableAgent     (agent/core.py)
#    • AgentWorker         (QThread for non-blocking LLM calls)
#    • MainWindow          (the full PyQt6 UI)
# ─────────────────────────────────────────────

import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QSplitter, QFileDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

from agent.core import ObservableAgent
from tools import WebSearchTool, MemoryTool, CodeExecutionTool, APICallerTool, FileManagementTool


# ─────────────────────────────────────────────
#  AgentWorker — runs agent.process() off the main thread
#  so the GUI never freezes while waiting for Ollama.
# ─────────────────────────────────────────────

class AgentWorker(QThread):
    log_signal    = pyqtSignal(dict)   # fired for every trace step
    result_signal = pyqtSignal(dict)   # fired once with the final result

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
#  MainWindow — full PyQt6 application window
# ─────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        # 1. Register tools FIRST so the registry is populated
        #    before ObservableAgent reads it.
        self._init_tools()
        # 2. Create agent (reads registry)
        self.agent = ObservableAgent()
        # 3. Build the UI
        self.attached_file_path: str | None = None
        self.is_generating: bool = False
        self._build_ui()
        self.worker: AgentWorker | None = None

    # ── Initialization ───────────────────────────────────────────────────

    def _init_tools(self) -> None:
        """Instantiate every tool — each __init__ auto-registers in AgentTool.registry."""
        WebSearchTool()
        MemoryTool()
        CodeExecutionTool()
        APICallerTool()
        FileManagementTool()

    # ── UI construction ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Observable Agent Runtime")
        self.setMinimumSize(1150, 750)
        self.setStyleSheet(self._stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_splitter())

        self._append_chat("agent", "Hello Edrin, how can I help you?")

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

        # ── Header ──────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Observable Agent Runtime")
        title.setObjectName("headerTitle")
        
        # Check connection status
        is_online = self.agent.check_ollama()
        status_str = "● Connected" if is_online else "○ Offline"
        status_color = "#34d399" if is_online else "#f87171"

        self.status_badge = QLabel(f'<span style="color:{status_color}">{status_str}</span>  •  {self.agent.model}')
        self.status_badge.setObjectName("modelBadge")

        clear_btn = QPushButton("Clear Chat")
        clear_btn.setObjectName("actionBtn")
        clear_btn.clicked.connect(self._clear_chat)

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(clear_btn)
        h_layout.addWidget(self.status_badge)
        layout.addWidget(header)

        # ── Chat area ────────────────────────────────────────────────────
        self.chat = QTextEdit()
        self.chat.setObjectName("chatArea")
        self.chat.setReadOnly(True)
        layout.addWidget(self.chat, 1)

        # ── Input bar & File Pill ─────────────────────────────────────────
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        ic_layout = QVBoxLayout(input_container)
        ic_layout.setContentsMargins(16, 8, 16, 16)
        ic_layout.setSpacing(6)

        # Attachment Pill Badge Widget (hidden by default)
        self.pill_widget = QWidget()
        self.pill_widget.setObjectName("pillWidget")
        self.pill_widget.setVisible(False)
        pw_layout = QHBoxLayout(self.pill_widget)
        pw_layout.setContentsMargins(10, 4, 10, 4)
        pw_layout.setSpacing(6)

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

        # Main Input Row
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
            # STOP Prompt clicked!
            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
            self._append_trace('<span style="color:#ef4444;font-weight:600">[CANCELLED] Generation stopped by user.</span>')
            self._on_done()
        else:
            self._send()



    def _build_right_panel(self) -> QWidget:
        right = QWidget()
        right.setObjectName("rightPanel")
        layout = QVBoxLayout(right)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Trace header ─────────────────────────────────────────────────
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

        # ── Trace log ────────────────────────────────────────────────────
        self.trace = QTextEdit()
        self.trace.setObjectName("traceArea")
        self.trace.setReadOnly(True)
        layout.addWidget(self.trace, 1)

        # ── Registered tools panel ───────────────────────────────────────
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

    # ── Action Handlers ─────────────────────────────────────────────────

    def _clear_chat(self) -> None:
        self.chat.clear()
        self._append_chat("agent", "Hello Edrin, how can I help you?")

    def _clear_trace(self) -> None:
        self.trace.clear()

    # ── Event handlers ───────────────────────────────────────────────────

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
            self._append_chat("tool", f"**{result['tool_used']}**\n{result['tool_result']}")
        self._append_chat("agent", result["response"])

    def _on_done(self) -> None:
        self.worker = None
        self.is_generating = False
        self.send_btn.setText("Send")
        self.send_btn.setStyleSheet("background-color: #7c3aed; color: white;")
        self.attached_file_path = None
        self.pill_widget.setVisible(False)

    # ── Rendering helpers ────────────────────────────────────────────────

    def _append_chat(self, role: str, text: str) -> None:
        role_styles = {
            "user":  ("#1e293b", "#8b5cf6", "You"),
            "agent": ("#0f172a", "#a78bfa", "Agent"),
            "tool":  ("#0f1f1a", "#34d399", "Tool"),
        }
        bg, accent, label = role_styles.get(role, ("#1e293b", "#94a3b8", role))
        
        # Format markdown-like code blocks cleanly
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

    # ── Stylesheet ───────────────────────────────────────────────────────

    def _stylesheet(self) -> str:
        return """
        QMainWindow, QWidget {
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: 'Segoe UI', -apple-system, sans-serif;
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
        QScrollBar:vertical { background: #0f172a; width: 6px; }
        QScrollBar::handle:vertical { background: #334155; border-radius: 3px; }
        QSplitter::handle { background: #1e293b; }
        """


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

