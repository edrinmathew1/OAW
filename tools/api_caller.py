import re
import json
import requests
from tools.base import AgentTool


class APICallerTool(AgentTool):
    """
    Makes arbitrary HTTP calls on the user's behalf.
    Trigger words: call api, fetch url, http, get request, post request, put request, delete request, fetch api
    """

    def __init__(self) -> None:
        super().__init__(
            name="API Caller",
            description="Call an external HTTP API (GET, POST, PUT, DELETE) and return the response",
            trigger_pattern=r"\b(call api|fetch url|http|get request|post request|put request|delete request|fetch api|api)\b"
        )

    def execute(self, task: str) -> dict:
        # Extract URL (http:// or https://)
        url_match = re.search(r"https?://[^\s\"'>]+", task)
        
        if not url_match:
            return {
                "tool": self.name,
                "status": "error",
                "result": "No valid URL found in task (URL must start with http:// or https://)."
            }

        url = url_match.group(0)
        
        # Determine HTTP method
        method = "GET"
        if re.search(r"\bpost\b", task, re.IGNORECASE):
            method = "POST"
        elif re.search(r"\bput\b", task, re.IGNORECASE):
            method = "PUT"
        elif re.search(r"\bdelete\b", task, re.IGNORECASE):
            method = "DELETE"
        
        # Extract potential JSON body if POST or PUT
        data = None
        json_match = re.search(r"\{.*\}", task, re.DOTALL)
        if json_match and method in ("POST", "PUT"):
            try:
                data = json.loads(json_match.group(0))
            except Exception:
                pass

        try:
            headers = {"User-Agent": "ObservableAgent/1.0", "Accept": "application/json"}
            if method == "POST":
                resp = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == "PUT":
                resp = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=10)
            else:
                resp = requests.get(url, headers=headers, timeout=10)
            
            status_code = resp.status_code
            try:
                formatted_body = json.dumps(resp.json(), indent=2)
            except Exception:
                formatted_body = resp.text[:1000]

            return {
                "tool": self.name,
                "status": "success" if resp.ok else "error",
                "result": f"[{method} {url}] Status: {status_code}\n\nResponse:\n{formatted_body}"
            }
        except Exception as exc:
            return {
                "tool": self.name,
                "status": "error",
                "result": f"HTTP Request failed for {url}: {exc}"
            }


