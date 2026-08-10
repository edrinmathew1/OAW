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
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QSplitter,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

from agent.core import ObservableAgent
from tools import WebSearchTool, MemoryTool, CodeExecutionTool, APICallerTool


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
        self._build_ui()
        self.worker: AgentWorker | None = None

    # ── Initialization ───────────────────────────────────────────────────

    def _init_tools(self) -> None:
        """Instantiate every tool — each __init__ auto-registers in AgentTool.registry."""
        WebSearchTool()
        MemoryTool()
        CodeExecutionTool()
        APICallerTool()

    # ── UI construction ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Observable Agent Runtime")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(self._stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_splitter())

        self._append_chat(
            "agent",
            "Hello! I'm your local AI agent running on Qwen 2.5. "
            "I can search the web, remember notes, and execute code. "
            "What do you need?"
        )

    def _make_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([680, 380])
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

        # ── Input bar ────────────────────────────────────────────────────
        input_bar = QWidget()
        input_bar.setObjectName("inputBar")
        i_layout = QHBoxLayout(input_bar)
        i_layout.setContentsMargins(16, 12, 16, 12)
        i_layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setObjectName("inputField")
        self.input.setPlaceholderText("Ask anything — search, remember, run code, call API…")
        self.input.returnPressed.connect(self._send)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.clicked.connect(self._send)

        i_layout.addWidget(self.input)
        i_layout.addWidget(self.send_btn)
        layout.addWidget(input_bar)

        return left

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
        self._append_chat(
            "agent",
            "Chat cleared. I'm ready for your next request!"
        )

    def _clear_trace(self) -> None:
        self.trace.clear()


    # ── Event handlers ───────────────────────────────────────────────────

    def _send(self) -> None:
        text = self.input.text().strip()
        if not text or self.worker is not None:
            return

        self.input.clear()
        self.send_btn.setEnabled(False)
        self.send_btn.setText("…")
        self._append_chat("user", text)
        self._append_trace("─" * 36)

        self.worker = AgentWorker(self.agent, text)
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
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")

    # ── Rendering helpers ────────────────────────────────────────────────

    def _append_chat(self, role: str, text: str) -> None:
        role_styles = {
            "user":  ("#1e293b", "#e2e8f0", "You"),
            "agent": ("#0f172a", "#a78bfa", "Agent"),
            "tool":  ("#0f1f1a", "#34d399", "Tool"),
        }
        bg, accent, label = role_styles.get(role, ("#1e293b", "#94a3b8", role))
        escaped = (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        html = (
            f'<div style="margin:8px 0;padding:12px 16px;'
            f'background:{bg};border-left:3px solid {accent};border-radius:4px">'
            f'<div style="color:{accent};font-size:11px;font-weight:700;'
            f'margin-bottom:4px;letter-spacing:1px">{label.upper()}</div>'
            f'<div style="color:#e2e8f0;font-size:14px;line-height:1.6">{escaped}</div>'
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
            font-family: 'Segoe UI', sans-serif;
        }
        #leftPanel  { background-color: #0f172a; }
        #header     { background-color: #0f172a; border-bottom: 1px solid #1e293b; }
        #headerTitle { font-size: 15px; font-weight: 700; color: #e2e8f0; }
        #modelBadge {
            font-size: 11px; color: #64748b;
            background: #1e293b; padding: 4px 10px; border-radius: 12px;
        }
        #chatArea {
            background-color: #0f172a; border: none;
            padding: 16px; color: #e2e8f0; font-size: 14px;
        }
        #inputBar   { background-color: #0f172a; border-top: 1px solid #1e293b; }
        #inputField {
            background-color: #1e293b; border: 1px solid #334155;
            border-radius: 8px; padding: 10px 14px;
            color: #e2e8f0; font-size: 14px;
        }
        #inputField:focus { border: 1px solid #a78bfa; }
        #sendBtn {
            background-color: #7c3aed; color: white;
            border: none; border-radius: 8px;
            padding: 10px 20px; font-size: 14px; font-weight: 600;
        }
        #sendBtn:hover    { background-color: #6d28d9; }
        #actionBtn {
            background-color: #1e293b; color: #94a3b8;
            border: 1px solid #334155; border-radius: 6px;
            padding: 4px 10px; font-size: 11px; font-weight: 600;
        }
        #actionBtn:hover { background-color: #334155; color: #f8fafc; }
        #rightPanel { background-color: #080f1e; border-left: 1px solid #1e293b; }
        #traceHeaderWidget { border-bottom: 1px solid #1e293b; background-color: #080f1e; }
        #traceHeader {
            font-size: 12px; font-weight: 700; color: #64748b;
            letter-spacing: 1.5px; text-transform: uppercase;
        }

        #traceArea {
            background-color: #080f1e; border: none; padding: 12px;
            font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px;
        }
        #toolsWidget { background-color: #0a1628; border-top: 1px solid #1e293b; }
        #toolsLabel  {
            font-size: 11px; font-weight: 700; color: #475569;
            letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px;
        }
        #toolItem    { font-size: 12px; color: #64748b; padding: 2px 0; }
        QScrollBar:vertical          { background: #0f172a; width: 6px; }
        QScrollBar::handle:vertical  { background: #334155; border-radius: 3px; }
        QSplitter::handle            { background: #1e293b; }
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
