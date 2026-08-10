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
    Handles file operations, uploads, natural language transformations, Q&A on documents, and backups.
    Trigger words: file, read file, process file, modify file, backup file, update file, delete from file
    """

    def __init__(self) -> None:
        super().__init__(
            name="File Manager Tool",
            description="Process text/record files, read document contents, answer questions, apply transformations, and create backups",
            trigger_pattern=r"\b(file|read file|process file|modify file|backup file|update file|delete from file|open file)\b"
        )

    def _extract_filepath(self, task: str) -> str:
        """Extract valid file path supporting paths with spaces and quotes."""
        # 1. Match double quoted path
        m1 = re.search(r"\"([^\"]+\.(?:txt|csv))\"", task, re.IGNORECASE)
        if m1 and os.path.exists(m1.group(1).strip()):
            return m1.group(1).strip()

        # 2. Match single quoted path
        m2 = re.search(r"'([^']+\.(?:txt|csv))'", task, re.IGNORECASE)
        if m2 and os.path.exists(m2.group(1).strip()):
            return m2.group(1).strip()

        # 3. Match 'process file <path>:' format
        m3 = re.search(r"process file\s+[\"']?([^:\"'\n\r]+\.(?:txt|csv))[\"']?", task, re.IGNORECASE)
        if m3 and os.path.exists(m3.group(1).strip()):
            return m3.group(1).strip()

        # 4. Match any Windows path format (e.g. C:\...)
        m4 = re.search(r"([A-Za-z]:\\[^:\"'\n\r]+?\.(?:txt|csv))", task, re.IGNORECASE)
        if m4 and os.path.exists(m4.group(1).strip()):
            return m4.group(1).strip()

        # 5. Match plain relative filename
        m5 = re.search(r"([^\s\"'\n\r]+\.(?:txt|csv))", task, re.IGNORECASE)
        if m5:
            cand = m5.group(1).strip().rstrip(":")
            if os.path.exists(cand):
                return cand
            # Check inside data/ directory
            data_cand = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", cand)
            if os.path.exists(data_cand):
                return data_cand

        return DEFAULT_FILE

    def execute(self, task: str) -> dict:
        filepath = self._extract_filepath(task)
        task_lower = task.lower()

        if not os.path.exists(filepath):
            return {
                "tool": self.name,
                "status": "error",
                "result": f"File '{filepath}' not found on disk."
            }

        # 1. Backup Operation
        if "backup" in task_lower:
            msg = create_backup(filepath)
            return {
                "tool": self.name,
                "status": "success",
                "result": f"Backup Operation Completed:\n{msg}"
            }

        # 2. Check if modification is requested (e.g. convert, uppercase, format, remove, append, delete, change)
        is_modification = any(kw in task_lower for kw in [
            "uppercase", "lowercase", "convert", "format", "remove deprecated",
            "delete record", "append record", "modify line", "replace text", "change email"
        ])

        if is_modification:
            f_in = open(filepath, "r", encoding="utf-8")
            try:
                content = f_in.read()
            finally:
                f_in.close()

            modified_content, status_msg = process_file_with_prompt(content, task, filename=os.path.basename(filepath))
            return {
                "tool": self.name,
                "status": "success",
                "result": f"{status_msg}\n\nModified Content Preview:\n{modified_content}"
            }

        # 3. Default: Read file content & return for Document Q&A / Answer questions
        f_in = open(filepath, "r", encoding="utf-8")
        try:
            content = f_in.read()
        finally:
            f_in.close()

        lines = content.strip().splitlines()
        filename = os.path.basename(filepath)

        return {
            "tool": self.name,
            "status": "success",
            "result": f"Document '{filename}' read successfully ({len(lines)} lines).\n\nDocument Content:\n{content}"
        }

