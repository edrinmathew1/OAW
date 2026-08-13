# ─────────────────────────────────────────────
#  tools/search.py — Web Search & Public API Tool (Requirement #1 & #4)
#
#  Demonstrates:
#    • Inheritance & Abstract Method implementation
#    • Fetching data from Public Web APIs
#    • Dictionary processing functions: .get(), .keys(), .values(), .items(), .update()
# ─────────────────────────────────────────────

import os
import requests
from tools.base import AgentTool
from config import TAVILY_API_KEY


class WebSearchTool(AgentTool):
    """
    Derived class inheriting from AgentTool.
    Demonstrates Inheritance, Polymorphism, and Dictionary Processing (Requirement #4).
    """

    def __init__(self) -> None:
        super().__init__(
            name="Web Search Tool",
            description="Search the web or Wikipedia public API for real-time information",
            trigger_pattern=r"\b(search|find|who|who's|who is|what|whats|what's|what is|where|where's|where is|when|why|how|latest|lookup|weather|news|score|price|tell me|info)\b"
        )


    def _query_wikipedia_api(self, query: str) -> dict:
        """Fetch summary from Wikipedia REST API and process dictionary response."""
        clean_query = query.replace("search", "").replace("what is", "").replace("who is", "").strip()
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(clean_query)}"
        
        try:
            res = requests.get(url, timeout=3, headers={"User-Agent": "OAW_Agent/1.0"})
            if res.status_code == 200:
                data_dict: dict = res.json()

                # Requirement #4: Dictionary functions processing
                dict_keys = list(data_dict.keys())
                extract_val = data_dict.get("extract", "No extract found.")
                data_dict.update({"processed_status": "success"})

                return {
                    "source": "Wikipedia REST API",
                    "title": data_dict.get("title", clean_query),
                    "summary": extract_val,
                    "keys_count": len(dict_keys)
                }
        except Exception:
            pass

        return {"source": "Fallback", "summary": f"Could not retrieve Wikipedia summary for '{clean_query}'."}

    def execute(self, task: str) -> dict:
        """Implementation of abstract method execute()."""
        # 1. Try Tavily Search API if key is configured
        if TAVILY_API_KEY and TAVILY_API_KEY != "your_tavily_api_key_here":
            try:
                from tavily import TavilyClient
                tavily = TavilyClient(api_key=TAVILY_API_KEY)
                res = tavily.search(query=task, max_results=3)
                results = res.get("results", [])
                
                formatted = []
                for r in results:
                    # Dictionary functions (.get, .items)
                    title = r.get("title", "No Title")
                    content = r.get("content", "")
                    url = r.get("url", "")
                    formatted.append(f"• [{title}]({url}): {content}")

                return {
                    "tool": self.name,
                    "status": "success",
                    "result": "\n\n".join(formatted) if formatted else "No results found."
                }
            except Exception:
                pass

        # 2. Fallback to Public Wikipedia REST API
        wiki_res = self._query_wikipedia_api(task)
        return {
            "tool": self.name,
            "status": "success",
            "result": f"**Source: {wiki_res.get('source')}**\n\n{wiki_res.get('summary')}"
        }
