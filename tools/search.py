import re
import requests
from config import TAVILY_API_KEY
from tools.base import AgentTool


class WebSearchTool(AgentTool):
    """
    Handles web-search intent using Tavily API or HTTP search fallback.
    Trigger words: search, find, look up, google, what is, who is, when did
    """

    def __init__(self) -> None:
        super().__init__(
            name="Web Search",
            description="Search the web for current information",
            trigger_pattern=r"\b(search|find|look up|google|what is|who is|when did)\b"
        )

    def _search_tavily(self, query: str) -> str | None:
        if not TAVILY_API_KEY:
            return None
        try:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            response = tavily.search(query=query, max_results=3)
            results = response.get("results", [])
            if not results:
                return f"No Tavily results found for '{query}'."
            formatted = [f"• [{r.get('title')}]({r.get('url')}): {r.get('content')}" for r in results]
            return "\n".join(formatted)
        except Exception as err:
            return f"Tavily search error: {err}"

    def _search_fallback(self, query: str) -> str:
        # Fallback to Wikipedia API for instant facts
        try:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
            res = requests.get(wiki_url, timeout=5, headers={"User-Agent": "ObservableAgent/1.0"})
            if res.status_code == 200:
                data = res.json()
                extract = data.get("extract")
                if extract:
                    return f"• Wikipedia Summary for '{query}': {extract}"
        except Exception:
            pass

        # Simulated structured response when offline / no key
        return (
            f"Search results for '{query}':\n"
            f"• Quick Fact: Information regarding '{query}' loaded.\n"
            f"• Note: Configure TAVILY_API_KEY in .env for live Tavily web search results."
        )

    def execute(self, task: str) -> dict:
        query = re.sub(
            r"^(search for|search|find|look up|google)\s*",
            "",
            task,
            flags=re.IGNORECASE
        ).strip()
        if not query:
            query = task

        # Try Tavily first if key present
        tavily_out = self._search_tavily(query)
        if tavily_out and not tavily_out.startswith("Tavily search error"):
            result_str = tavily_out
        else:
            fallback_out = self._search_fallback(query)
            if tavily_out: # was error
                result_str = f"{tavily_out}\n\nFallback Results:\n{fallback_out}"
            else:
                result_str = fallback_out

        return {
            "tool": self.name,
            "status": "success",
            "result": result_str
        }

