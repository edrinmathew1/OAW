# ─────────────────────────────────────────────
#  tools/file_tool.py — File Management & Processing Tool for AI Agent
#
#  Demonstrates File Modes (w, r, a, w+, r+), File Methods (read, readlines, write, seek, tell, close),
#  RegEx Validations, and File Backup creation within the AI Agent Runtime.
# ─────────────────────────────────────────────

import os
import re
from tools.base import AgentTool
from file_manager import (
    read_all_records, append_record, search_record, update_record,
    delete_record, create_backup, process_file_with_prompt,
    validate_id, validate_email, validate_date, validate_tool_code,
    DEFAULT_FILE, BACKUP_FILE
)


class FileManagementTool(AgentTool):
    """
    Handles file operations, uploads, natural language transformations, and backups.
    Trigger words: file, read file, process file, modify file, backup file, update file, delete from file
    """

    def __init__(self) -> None:
        super().__init__(
            name="File Manager Tool",
            description="Process text/record files, apply transformations, validate fields via RegEx, and create backups",
            trigger_pattern=r"\b(file|read file|process file|modify file|backup file|update file|delete from file|open file)\b"
        )

    def execute(self, task: str) -> dict:
        # Extract file path if provided in task
        path_match = re.search(r"['\"]?([a-zA-Z0-9_\-\\/:\.]+\.(?:txt|csv))['\"]?", task)
        filepath = path_match.group(1) if path_match else DEFAULT_FILE

        task_lower = task.lower()

        # 1. Backup Operation
        if "backup" in task_lower:
            msg = create_backup(filepath)
            return {
                "tool": self.name,
                "status": "success",
                "result": f"Backup Operation Completed:\n{msg}"
            }

        # 2. Read Operation
        if "read" in task_lower or "show" in task_lower:
            records = read_all_records(filepath)
            formatted = "\n".join(r.strip() for r in records)
            return {
                "tool": self.name,
                "status": "success",
                "result": f"File Contents of '{os.path.basename(filepath)}' ({len(records)} lines):\n{formatted}"
            }

        # 3. Append / Add Record
        if "append" in task_lower or "add" in task_lower:
            record_match = re.search(r"(?:append|add)\s+(?:record|line)?\s*[:\-]?\s*(.*)", task, re.IGNORECASE)
            record_str = record_match.group(1).strip() if record_match else "105|OAW-105|Agent Tool|dev@oaw.io|2026-08-10|Active"
            msg = append_record(record_str, filepath)
            return {
                "tool": self.name,
                "status": "success",
                "result": f"Append Operation Completed:\n{msg}\nAppended Line: {record_str}"
            }

        # 4. Prompt Processing / Modification (Default for process/modify/transform)
        if os.path.exists(filepath):
            f_in = open(filepath, "r", encoding="utf-8")
            try:
                content = f_in.read()
            finally:
                f_in.close()

            modified_content, status_msg = process_file_with_prompt(content, task, filename=os.path.basename(filepath))
            return {
                "tool": self.name,
                "status": "success",
                "result": f"{status_msg}\n\nModified Content Preview:\n{modified_content[:500]}"
            }

        return {
            "tool": self.name,
            "status": "error",
            "result": f"File '{filepath}' not found."
        }
