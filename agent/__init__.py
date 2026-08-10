# agent/__init__.py
# Exposes the main agent class for clean top-level imports.
# Usage: from agent import ObservableAgent

from agent.core import ObservableAgent

__all__ = ["ObservableAgent"]
