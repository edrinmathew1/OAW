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
    """

    @staticmethod
    def all() -> list[AgentTool]:
        """Return all registered tool instances."""
        return list(AgentTool.registry)

    @staticmethod
    def get(name: str) -> AgentTool | None:
        """Return a specific tool by name, or None if not found."""
        return next((tool for tool in AgentTool.registry if tool.name.lower() == name.lower()), None)

    @staticmethod
    def names() -> list[str]:
        """Return the names of all registered tools."""
        return [tool.name for tool in AgentTool.registry]

    @staticmethod
    def to_ollama_schemas() -> list[dict]:
        """Return all tool schemas in Ollama's tool-calling format."""
        return [tool.to_ollama_schema() for tool in AgentTool.registry if hasattr(tool, "to_ollama_schema")]

