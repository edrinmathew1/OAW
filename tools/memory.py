import re
import json
from datetime import datetime
from config import MEMORY_FILE
from tools.base import AgentTool


class MemoryTool(AgentTool):
    """
    Saves and recalls notes persistently across sessions.
    Trigger words: remember, save, store, recall, retrieve, what do you know about, clear memories
    """

    def __init__(self) -> None:
        super().__init__(
            name="Memory",
            description="Save, search, or clear persistent notes and information",
            trigger_pattern=r"\b(remember|save|store|recall|what do you know about|retrieve|clear memories|memory)\b"
        )
        self._load()

    # ── Private helpers ─────────────────────────────────────────────────

    def _load(self) -> None:
        """Load memories from disk; start fresh if the file doesn't exist."""
        try:
            with open(MEMORY_FILE, "r") as f:
                self.memories: list[dict] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memories = []

    def _save(self) -> None:
        """Persist all memories to disk."""
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memories, f, indent=2)

    # ── Tool interface ───────────────────────────────────────────────────

    def execute(self, task: str) -> dict:
        is_clear = re.search(r"\b(clear memories|delete memories|forget all)\b", task, re.IGNORECASE)
        if is_clear:
            self.memories = []
            self._save()
            return {
                "tool": self.name,
                "status": "success",
                "result": "All saved memories have been cleared."
            }

        is_recall = re.search(
            r"\b(recall|retrieve|what do you know|show memories)\b",
            task,
            re.IGNORECASE
        )

        if is_recall:
            if not self.memories:
                return {
                    "tool": self.name,
                    "status": "success",
                    "result": "No memories saved yet."
                }
            
            # Extract keyword if specific search request
            query_term = re.sub(r"^(recall|retrieve|what do you know about|show memories)\s*", "", task, flags=re.IGNORECASE).strip()
            
            matched = self.memories
            if query_term and len(query_term) > 2:
                matched = [m for m in self.memories if query_term.lower() in m["note"].lower()]

            if not matched:
                return {
                    "tool": self.name,
                    "status": "success",
                    "result": f"No memories found matching '{query_term}'."
                }

            items = "\n".join(
                f"• {m['note']} (saved {m['time']})"
                for m in matched[-10:]
            )
            return {
                "tool": self.name,
                "status": "success",
                "result": f"Saved memories:\n{items}"
            }

        # Default: save mode
        note = re.sub(
            r"^(remember|save|store)\s*(that\s*)?",
            "",
            task,
            flags=re.IGNORECASE
        ).strip()

        if not note:
            note = task

        entry = {
            "note": note,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.memories.append(entry)
        self._save()

        return {
            "tool": self.name,
            "status": "success",
            "result": f'Saved: "{note}"'
        }

