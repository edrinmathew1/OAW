# ─────────────────────────────────────────────
#  tools/base.py — Abstract Base Class & Polymorphism (Requirement #1)
#
#  Demonstrates OOP Concepts:
#    1. Abstract Base Class (ABC) & Abstract Method (@abstractmethod)
#    2. Inheritance (Derived tool classes inherit from AgentTool)
#    3. Polymorphism (Invoking execute() on different tool objects)
#    4. Encapsulation (Internal regex pattern and tool execution logic)
# ─────────────────────────────────────────────

from abc import ABC, abstractmethod
import re


class AgentTool(ABC):
    """
    Abstract base class for all tools in the Observable Agent Runtime.
    Demonstrates Abstract Base Class & Method (Requirement #1).
    """

    registry: list["AgentTool"] = []

    def __init__(self, name: str, description: str, trigger_pattern: str) -> None:
        self._name = name                # Encapsulated private attributes
        self._description = description
        self._trigger_pattern = trigger_pattern
        AgentTool.registry.append(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def matches(self, user_input: str) -> bool:
        """Check if user input matches this tool's trigger pattern."""
        return bool(re.search(self._trigger_pattern, user_input, re.IGNORECASE))

    @abstractmethod
    def execute(self, task: str) -> dict:
        """
        Abstract Method (Requirement #1).
        Must be implemented differently by each derived tool class.
        """
        pass
