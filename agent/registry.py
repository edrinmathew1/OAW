# ─────────────────────────────────────────────
#  agent/registry.py — Tool registry accessor
#
#  The actual registry lives on AgentTool as a class variable
#  (so every tool self-registers on instantiation).
#  This module provides a clean interface for the rest of the
#  codebase to query it without importing AgentTool directly.
# ─────────────────────────────────────────────

from tools.base import AgentTool


class ToolRegistry:
    """
    Read-only interface to the shared AgentTool.registry.

    Tools register themselves automatically when instantiated —
    this class just provides named accessors so agent code
    doesn't need to know about the AgentTool internals.
    """

    @staticmethod
    def all() -> list[AgentTool]:
        """Return all registered tool instances."""
        return list(AgentTool.registry.values())

    @staticmethod
    def get(name: str) -> AgentTool | None:
        """Return a specific tool by name, or None if not found."""
        return AgentTool.registry.get(name)

    @staticmethod
    def names() -> list[str]:
        """Return the names of all registered tools."""
        return list(AgentTool.registry.keys())

    @staticmethod
    def to_ollama_schemas() -> list[dict]:
        """Return all tool schemas in Ollama's tool-calling format."""
        return [tool.to_ollama_schema() for tool in AgentTool.registry.values()]
