# ─────────────────────────────────────────────
#  tools/base.py — Abstract base class for all tools
#
#  OOP concepts demonstrated:
#    • Abstract Base Class (ABC) — enforces the execute() contract
#    • Class-level registry dict — shared across all subclasses
#    • Polymorphism — every tool is a BaseTool, called the same way
# ─────────────────────────────────────────────

import re
from abc import ABC, abstractmethod


class AgentTool(ABC):
    """
    Abstract base class every tool must inherit from.

    Subclasses MUST implement:
        execute(task: str) -> dict

    Registering a tool is automatic — instantiating a subclass
    adds it to AgentTool.registry under its name.
    """

    # Shared registry across all subclasses (class variable, not instance)
    registry: dict[str, "AgentTool"] = {}

    def __init__(self, name: str, description: str, trigger_pattern: str) -> None:
        self.name = name
        self.description = description
        # Pre-compile the regex for performance
        self.trigger_pattern = re.compile(trigger_pattern, re.IGNORECASE)
        # Auto-register in the class-level registry
        AgentTool.registry[name] = self

    # ── Abstract interface (subclasses must implement) ──────────────────

    @abstractmethod
    def execute(self, task: str) -> dict:
        """Run the tool with the given task string. Return a result dict."""
        pass

    # ── Concrete helpers (inherited as-is by all subclasses) ────────────

    def matches(self, text: str) -> bool:
        """Return True if this tool's trigger pattern fires on the text."""
        return bool(self.trigger_pattern.search(text))

    def to_ollama_schema(self) -> dict:
        """Return the Ollama-compatible JSON schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name.lower().replace(" ", "_"),
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "The task to execute"
                        }
                    },
                    "required": ["task"]
                }
            }
        }
