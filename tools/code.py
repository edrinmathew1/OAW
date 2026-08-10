import re
import sys
import io
import contextlib
from config import E2B_API_KEY
from tools.base import AgentTool


class CodeExecutionTool(AgentTool):
    """
    Detects and runs Python code blocks or calculations.
    Trigger words: run, execute, code, python, script, function, calculate, compute
    """

    def __init__(self) -> None:
        super().__init__(
            name="Code Execution",
            description="Execute or analyze Python code",
            trigger_pattern=r"\b(run|execute|code|python|script|function|calculate|compute)\b"
        )

    def _execute_e2b(self, code: str) -> dict | None:
        if not E2B_API_KEY:
            return None
        try:
            from e2b_code_interpreter import Sandbox
            with Sandbox(api_key=E2B_API_KEY) as sandbox:
                execution = sandbox.run_code(code)
                output = []
                if execution.logs.stdout:
                    output.append(f"stdout:\n" + "\n".join(execution.logs.stdout))
                if execution.logs.stderr:
                    output.append(f"stderr:\n" + "\n".join(execution.logs.stderr))
                if execution.error:
                    output.append(f"Error: {execution.error.name} - {execution.error.value}")
                res = "\n".join(output) if output else "Code executed cleanly with no output."
                return {
                    "tool": self.name,
                    "status": "error" if execution.error else "success",
                    "result": f"[E2B Sandbox Output]\n{res}"
                }
        except Exception as err:
            return {
                "tool": self.name,
                "status": "error",
                "result": f"E2B Sandbox execution error: {err}"
            }

    def execute(self, task: str) -> dict:
        # Extract a fenced code block (`python ... ` or ```python ... ```)
        code_match = re.search(
            r"`{1,3}(?:python)?\s*(.*?)`{1,3}",
            task,
            re.DOTALL
        )

        code: str | None = None
        if code_match and code_match.group(1).strip():
            code = code_match.group(1).strip()
        elif re.search(r"\b(calculate|compute|eval)\b", task, re.IGNORECASE):
            # Extract math expression after calculate/compute
            math_expr = re.sub(r"^.*?\b(calculate|compute|eval)\b\s*", "", task, flags=re.IGNORECASE).strip()
            if math_expr:
                code = f"print({math_expr})"


        if code:
            # Try E2B sandbox if configured
            e2b_res = self._execute_e2b(code)
            if e2b_res:
                return e2b_res

            # Fallback to local python execution with stdout capture
            stdout_buf = io.StringIO()
            stderr_buf = io.StringIO()
            scope: dict = {}

            try:
                with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                    exec(code, scope)
                
                stdout_out = stdout_buf.getvalue().strip()
                stderr_out = stderr_buf.getvalue().strip()

                result_parts = []
                if stdout_out:
                    result_parts.append(f"Output:\n{stdout_out}")
                if stderr_out:
                    result_parts.append(f"Stderr:\n{stderr_out}")
                if not result_parts:
                    # Check if scope created any variable outputs
                    user_vars = {k: v for k, v in scope.items() if not k.startswith("__")}
                    if user_vars:
                        vars_str = ", ".join(f"{k} = {v}" for k, v in user_vars.items())
                        result_parts.append(f"Variables set: {vars_str}")
                    else:
                        result_parts.append("Code executed successfully with no output.")

                return {
                    "tool": self.name,
                    "status": "success",
                    "result": "\n".join(result_parts)
                }
            except Exception as exc:
                return {
                    "tool": self.name,
                    "status": "error",
                    "result": f"Execution error ({type(exc).__name__}): {exc}"
                }

        # No code block found
        return {
            "tool": self.name,
            "status": "success",
            "result": (
                f"Code task acknowledged: '{task}'\n"
                "Provide a python code block (```python ... ```) or math expression to execute."
            )
        }

