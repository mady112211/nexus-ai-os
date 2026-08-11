"""
Shared helpers used by core_brain.py and tool_registry.py
"""

import time
import json
import httpx
from ai_core.gateway import call_ai_sync


def with_retry(func, *args, retries=2, delay=1, **kwargs):
    last_error = None
    for attempt in range(retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    raise last_error


def extract_json(text):
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


def execute_web_search(query):
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
            )
            if response.status_code == 200:
                data = response.json()
                results = []

                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", ""),
                        "snippet": data.get("Abstract", ""),
                        "url": data.get("AbstractURL", ""),
                    })

                for topic in data.get("RelatedTopics", [])[:5]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:80],
                            "snippet": topic.get("Text", ""),
                            "url": topic.get("FirstURL", ""),
                        })

                if results:
                    summary_prompt = f"Summarize for: {query}\n\n"
                    for r in results[:3]:
                        summary_prompt += f"- {r['snippet']}\n"

                    summary = call_ai_sync(
                        summary_prompt,
                        "You are a research assistant. Give clear 3-4 sentence summary.",
                        task_type="fast"
                    )

                    return {
                        "success": True,
                        "type": "web_search",
                        "query": query,
                        "results": results[:5],
                        "summary": summary,
                    }

                return {"success": False, "error": "No results found", "type": "web_search"}
    except Exception as e:
        return {"success": False, "error": str(e), "type": "web_search"}

    return {"success": False, "error": "Search failed", "type": "web_search"}