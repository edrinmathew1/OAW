# ─────────────────────────────────────────────
#  agent/core.py — ObservableAgent orchestrator
#
#  Wires together:
#    • ToolRegistry  — knows which tools are available
#    • ReAct loop    — drives the Thought→Action→Observation cycle
#    • Ollama client — sends messages to the local LLM
# ─────────────────────────────────────────────

from __future__ import annotations

from datetime import datetime
from typing import Callable

import requests

from config import OLLAMA_URL, MODEL, AGENT_NAME
from agent.registry import ToolRegistry
from agent.loop import react_loop
from tools.base import AgentTool


class ObservableAgent:
    """
    The central orchestrator.

    Responsibilities
    ----------------
    - Maintain conversation history (multi-turn context)
    - Call the Ollama LLM endpoint
    - Delegate tool detection to ToolRegistry
    - Delegate the reasoning cycle to react_loop()
    - Accumulate a session-level log of all events
    """

    def __init__(self) -> None:
        self.name: str = AGENT_NAME
        self.model: str = MODEL

        # Live reference to registered tools
        self.tools: list[AgentTool] = ToolRegistry.all()
        if not self.tools:
            from tools import WebSearchTool, MemoryTool, CodeExecutionTool, APICallerTool, FileManagementTool, AppLauncherTool
            WebSearchTool()
            MemoryTool()
            CodeExecutionTool()
            APICallerTool()
            FileManagementTool()
            AppLauncherTool()
            self.tools = ToolRegistry.all()



        # Conversation history sent to the LLM on every turn
        self.history: list[dict] = []

        # Full session log (all emit() entries across all turns)
        self.logs: list[dict] = []

        # System prompt shown to the LLM as context
        tool_names = ", ".join(t.name for t in self.tools)
        self.system_prompt: str = (
            "You are a helpful AI agent with access to tools.\n"
            "When a user asks something, reason about which tool to use if any.\n"
            f"Available tools: {tool_names}.\n"
            "Be concise and clear. If you use a tool, say so briefly."
        )

    # ── Health check ───────────────────────────────────────────────────

    def check_ollama(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            url = OLLAMA_URL.replace("/api/chat", "/api/tags")
            res = requests.get(url, timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    # ── Private helpers ─────────────────────────────────────────────────

    def _log(self, event: str, detail: str) -> dict:
        """Create and store a timestamped log entry."""
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "detail": detail,
        }
        self.logs.append(entry)
        return entry

    def _detect_tool(self, text: str) -> AgentTool | None:
        """Return the first tool whose trigger pattern matches the text."""
        # Prioritize FileManagementTool if request contains file path or 'process file'
        if "process file" in text.lower() or ".txt" in text.lower() or ".csv" in text.lower():
            for tool in self.tools:
                if tool.name == "File Manager Tool":
                    return tool

        for tool in self.tools:
            if tool.matches(text):
                return tool
        return None


    def _call_ollama(self, user_message: str, tool_observation: str | None = None) -> str:
        """
        Append the user message (and optional tool observation) to history, POST to Ollama,
        and return the assistant reply. Updates history with the assistant's response.
        """
        if tool_observation:
            prompt = (
                f"User request: {user_message}\n\n"
                f"Tool Observation / Data:\n{tool_observation}\n\n"
                "Provide a clear, helpful response using the tool observation above."
            )
            self.history.append({"role": "user", "content": prompt})
        else:
            self.history.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt + " Keep answers clear, direct, and concise."},
                *self.history,
            ],
            "options": {
                "num_predict": 256,   # Limit response length for 3-5x faster generation
                "temperature": 0.2,   # Fast greedy sampling
                "top_k": 20,
                "top_p": 0.8,
            },
            "keep_alive": "30m",      # Keep model loaded in memory so it never unloads
            "stream": False,
        }


        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            reply: str = response.json()["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except requests.exceptions.ConnectionError:
            return "ERROR: Cannot connect to Ollama. Make sure it's running with: ollama serve"
        except Exception as exc:
            return f"ERROR: {exc}"

    # ── Public interface ─────────────────────────────────────────────────

    def process(
        self,
        user_input: str,
        on_log: Callable[[dict], None] | None = None,
    ) -> dict:
        """
        Run one full ReAct cycle and return the result dict.

        Parameters
        ----------
        user_input : the raw user message
        on_log     : optional callback fired on every trace step (used by GUI)
        """
        return react_loop(self, user_input, on_log)

