# ─────────────────────────────────────────────
#  tools/app_launcher.py — System App Launcher Tool
#
#  Demonstrates:
#    • Inheritance from AgentTool (Requirement #1)
#    • Subprocess application execution on Windows OS
#    • Encapsulated dictionary return structures
# ─────────────────────────────────────────────

import os
import subprocess
import shutil
import re
from tools.base import AgentTool


class AppLauncherTool(AgentTool):
    """
    Derived class inheriting from AgentTool.
    Launches local desktop applications, system utilities, and programs on demand.
    """

    APP_MAPPING = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "mspaint": "mspaint.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "terminal": "wt.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "vscode": "code.cmd",
        "code": "code.cmd",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "settings": "start ms-settings:",
        "control panel": "control.exe",
    }

    def __init__(self) -> None:
        super().__init__(
            name="System App Launcher Tool",
            description="Launch desktop applications (Notepad, Calculator, Chrome, VS Code, Explorer, Settings, etc.)",
            trigger_pattern=r"\b(open|launch|start|run)\s+(app|application|program|calculator|calc|notepad|chrome|vscode|code|explorer|cmd|terminal|paint|spotify|task manager|settings|control panel)\b"
        )

    def execute(self, task: str) -> dict:
        """Implementation of abstract method execute()."""
        task_lower = task.lower()

        # Find target app from task description
        target_app = None
        for alias in self.APP_MAPPING:
            if alias in task_lower:
                target_app = alias
                break

        if not target_app:
            match = re.search(r"\b(?:open|launch|start|run)\s+([a-zA-Z0-9_\-\s]+)", task, re.IGNORECASE)
            if match:
                target_app = match.group(1).strip().lower()

        if not target_app:
            return {
                "tool": self.name,
                "status": "error",
                "result": "Could not identify which application to launch. Example: 'open notepad' or 'launch calculator'."
            }

        cmd = self.APP_MAPPING.get(target_app, target_app)

        try:
            if cmd.startswith("start "):
                os.system(cmd)
            elif shutil.which(cmd) or os.path.exists(cmd):
                subprocess.Popen([cmd], shell=True)
            else:
                os.system(f"start {cmd}")

            return {
                "tool": self.name,
                "status": "success",
                "result": f"Successfully launched application '{target_app.title()}' (Command: '{cmd}')."
            }

        except Exception as exc:
            return {
                "tool": self.name,
                "status": "error",
                "result": f"Failed to launch '{target_app}': {str(exc)}"
            }
