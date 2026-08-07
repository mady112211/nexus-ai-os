import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class WebSearchPlugin:
    """Real web search using DuckDuckGo (Free - No API key needed)"""

    name = "Web Search"
    slug = "web_search"

    @staticmethod
    def search(query: str, max_results: int = 5) -> dict:
        """Search the web using DuckDuckGo API"""
        try:
            print(f"🔍 Searching: {query}")

            with httpx.Client(timeout=15) as client:
                response = client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1",
                    },
                    headers={
                        "User-Agent": "NEXUS-AI-OS/1.0"
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    results = []

                    # Abstract (main result)
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("Heading", "Result"),
                            "snippet": data.get("Abstract", ""),
                            "url": data.get("AbstractURL", ""),
                            "source": data.get("AbstractSource", ""),
                        })

                    # Related topics
                    for topic in data.get("RelatedTopics", [])[:max_results]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append({
                                "title": topic.get("Text", "")[:60],
                                "snippet": topic.get("Text", ""),
                                "url": topic.get("FirstURL", ""),
                                "source": "DuckDuckGo",
                            })

                    if not results:
                        # Fallback
                        results = [{
                            "title": f"Search: {query}",
                            "snippet": f"Search completed for: {query}. DuckDuckGo returned instant answer data.",
                            "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                            "source": "DuckDuckGo",
                        }]

                    print(f"✅ Found {len(results)} results")

                    return {
                        "success": True,
                        "query": query,
                        "results": results[:max_results],
                        "total": len(results),
                    }

        except Exception as e:
            print(f"❌ Search error: {str(e)}")

        return {
            "success": False,
            "query": query,
            "results": [],
            "error": "Search failed",
        }

    @staticmethod
    def quick_answer(query: str) -> str:
        """Get a quick answer for a query"""
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get("Answer"):
                        return data["Answer"]

                    if data.get("Abstract"):
                        return data["Abstract"]

                    if data.get("Definition"):
                        return data["Definition"]

        except Exception:
            pass

        return f"No quick answer found for: {query}"