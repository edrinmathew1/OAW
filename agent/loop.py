# ─────────────────────────────────────────────
#  agent/loop.py — ReAct Reasoning & Automatic Tool Switching Loop
# ─────────────────────────────────────────────

from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from agent.core import ObservableAgent


def react_loop(
    agent: "ObservableAgent",
    user_input: str,
    on_log: Callable[[dict], None] | None = None,
) -> dict:
    """
    Run one full ReAct cycle with automatic tool detection & intelligent auto-switching fallback.
    """

    result: dict = {
        "user": user_input,
        "logs": [],
        "tool_used": None,
        "tool_result": None,
        "response": "",
    }

    def emit(event: str, detail: str) -> None:
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "detail": detail,
        }
        agent.logs.append(entry)
        result["logs"].append(entry)
        if on_log:
            on_log(entry)

    emit("INPUT", user_input)

    # ── Step 1: Initial Tool Detection ──────────────────────────────────
    tool = agent._detect_tool(user_input)

    # Fallback auto-detection for real-time / web informational queries
    input_lower = user_input.lower()
    if not tool:
        web_keywords = ["weather", "news", "score", "who", "what", "whats", "what's", "where", "when", "why", "how", "latest", "price", "today", "current", "search", "lookup"]
        if any(kw in input_lower for kw in web_keywords):
            tool = next((t for t in agent.tools if t.name == "Web Search Tool"), None)

    tool_observation: str | None = None

    if tool:
        emit("TOOL SELECTED", tool.name)
        tool_out = tool.execute(user_input)
        result["tool_used"] = tool.name
        result["tool_result"] = tool_out["result"]
        tool_observation = tool_out["result"]
        snippet = tool_observation
        emit("TOOL RESULT", snippet[:120] + "…" if len(snippet) > 120 else snippet)

    # ── Step 2: Call LLM with Tool Observation ──────────────────────────
    emit("THINKING", f"Sending to {agent.model}…")
    llm_response = agent._call_ollama(user_input, tool_observation=tool_observation)

    # ── Step 3: LLM Refusal Auto-Switching Fallback ─────────────────────
    # If no tool was used initially and LLM states it lacks tools/access, run Web Search automatically!
    if not tool and any(phrase in llm_response.lower() for phrase in [
        "don't have", "do not have", "cannot", "can't", "search", "internet", "tool", "real-time"
    ]):
        web_tool = next((t for t in agent.tools if t.name == "Web Search Tool"), None)
        if web_tool:
            emit("TOOL SELECTED", f"{web_tool.name} (Auto-Switch)")
            tool_out = web_tool.execute(user_input)
            result["tool_used"] = web_tool.name
            result["tool_result"] = tool_out["result"]
            tool_observation = tool_out["result"]
            snippet = tool_observation
            emit("TOOL RESULT", snippet[:120] + "…" if len(snippet) > 120 else snippet)

            emit("THINKING", "Re-synthesizing final response with web search observation…")
            llm_response = agent._call_ollama(user_input, tool_observation=tool_observation)

    preview = llm_response[:120] + "…" if len(llm_response) > 120 else llm_response
    emit("LLM", preview)

    result["response"] = llm_response
    emit("DONE", "Response ready")

    return result
