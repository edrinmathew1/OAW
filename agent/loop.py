# ─────────────────────────────────────────────
#  agent/loop.py — The ReAct reasoning loop
#
#  Current implementation: regex-based dispatch
#    INPUT → THINKING → LLM → TOOL SELECTED → TOOL RESULT → DONE
#
#  Each step emits a structured log entry so the UI can display
#  the full execution trace in real time.
#
#  TODO (next phase): Replace regex dispatch with Ollama tool_calls
#  so Qwen 2.5 decides which tool to use via structured output.
# ─────────────────────────────────────────────

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    # Avoid circular import — core imports loop, loop type-hints core
    from agent.core import ObservableAgent


def react_loop(
    agent: "ObservableAgent",
    user_input: str,
    on_log: Callable[[dict], None] | None = None,
) -> dict:
    """
    Run one ReAct cycle for the given user input.

    Steps
    -----
    1. INPUT   — echo the user's message
    2. THINKING — signal that we're calling the LLM
    3. LLM     — record the raw model response
    4. TOOL SELECTED (optional) — regex matched a tool
    5. TOOL RESULT (optional)   — tool output
    6. DONE    — cycle complete

    Parameters
    ----------
    agent      : the ObservableAgent providing LLM + tool access
    user_input : the raw user message
    on_log     : optional callback fired on every step (used by the UI)

    Returns
    -------
    dict with keys: user, logs, tool_used, tool_result, response
    """

    result: dict = {
        "user": user_input,
        "logs": [],
        "tool_used": None,
        "tool_result": None,
        "response": "",
    }

    def emit(event: str, detail: str) -> None:
        """Create a log entry, append it to result and agent logs, and notify UI."""
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "detail": detail,
        }
        agent.logs.append(entry)
        result["logs"].append(entry)
        if on_log:
            on_log(entry)

    # ── Step 1 & 2 ──────────────────────────────────────────────────────
    emit("INPUT", user_input)

    # ── Step 3: Tool detection ──────────────────────────────────────────
    tool = agent._detect_tool(user_input)
    tool_observation: str | None = None

    if tool:
        emit("TOOL SELECTED", tool.name)
        tool_out = tool.execute(user_input)
        result["tool_used"] = tool.name
        result["tool_result"] = tool_out["result"]
        tool_observation = tool_out["result"]
        snippet = tool_observation
        emit("TOOL RESULT", snippet[:120] + "…" if len(snippet) > 120 else snippet)

    # ── Step 4: Thinking & LLM call ─────────────────────────────────────
    emit("THINKING", f"Sending to {agent.model}…")
    llm_response = agent._call_ollama(user_input, tool_observation=tool_observation)
    preview = llm_response[:120] + "…" if len(llm_response) > 120 else llm_response
    emit("LLM", preview)

    # ── Step 5: Done ────────────────────────────────────────────────────
    result["response"] = llm_response
    emit("DONE", "Response ready")

    return result

