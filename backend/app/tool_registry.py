"""
NEXUS Tool Registry
Discovers new APIs the brain doesn't have yet.
"""

import sqlite3
import time
import httpx
import os

from app.helpers import with_retry, extract_json, execute_web_search
from ai_core.gateway import call_ai_sync

DB_PATH = os.path.join(os.path.dirname(__file__), "tools.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            task_keywords TEXT,
            endpoint TEXT NOT NULL,
            method TEXT DEFAULT 'GET',
            auth_type TEXT DEFAULT 'none',
            auth_instructions TEXT,
            docs_url TEXT,
            status TEXT DEFAULT 'pending',
            created_at INTEGER,
            approved_at INTEGER
        )
    """)
    conn.commit()
    conn.close()


init_db()


def get_active_tool(task_description: str):
    """Match against approved tools."""
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tools WHERE status = 'active'").fetchall()
    conn.close()

    task_lower = task_description.lower()
    for row in rows:
        keywords = (row["task_keywords"] or "").lower().split(",")
        if any(kw.strip() and kw.strip() in task_lower for kw in keywords):
            return dict(row)
    return None


def get_tool_by_id(tool_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM tools WHERE id = ?", (tool_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_tools(status: str = None):
    conn = get_conn()
    if status:
        rows = conn.execute("SELECT * FROM tools WHERE status = ?", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tools ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def approve_tool(tool_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE tools SET status = 'active', approved_at = ? WHERE id = ?",
        (int(time.time()), tool_id),
    )
    conn.commit()
    conn.close()
    return get_tool_by_id(tool_id)


def reject_tool(tool_id: int):
    conn = get_conn()
    conn.execute("UPDATE tools SET status = 'rejected' WHERE id = ?", (tool_id,))
    conn.commit()
    conn.close()


def register_tool(data: dict, task_description: str):
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO tools
           (name, description, task_keywords, endpoint, method, auth_type,
            auth_instructions, docs_url, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
        (
            data.get("name", "Unnamed tool"),
            data.get("description", ""),
            task_description,
            data.get("endpoint", ""),
            data.get("method", "GET"),
            data.get("auth_type", "none"),
            data.get("auth_instructions", ""),
            data.get("docs_url", ""),
            int(time.time()),
        ),
    )
    conn.commit()
    tool_id = cur.lastrowid
    conn.close()
    return get_tool_by_id(tool_id)


def discover_tool(task_description: str):
    """Search web for legit free/open API."""
    search = execute_web_search(f"{task_description} free official API OR open source alternative")
    if not search.get("success"):
        return {"success": False, "error": "Discovery web search failed"}

    context_lines = []
    for r in search.get("results", [])[:5]:
        context_lines.append(f"- {r.get('title')}: {r.get('snippet')} ({r.get('url')})")
    context = "\n".join(context_lines) or "No results found."

    system_prompt = """You are an API discovery assistant for the NEXUS system.

STRICT RULES:
- Only identify OFFICIAL free tiers of real companies, OR genuinely open-source /
  self-hostable projects, OR public/government APIs with no cost.
- NEVER suggest leaked API keys, "free API key" reseller sites, scraping a paid
  service, or any workaround to bypass a paywall. If nothing legitimate is found,
  say so honestly.
- Prefer APIs with clear public documentation.

Return ONLY valid JSON:
{
  "found": true/false,
  "name": "tool name",
  "description": "what it does",
  "endpoint": "https://api.example.com/...",
  "method": "GET" | "POST",
  "auth_type": "none" | "api_key" | "bearer",
  "auth_instructions": "how to get a free key, if any",
  "docs_url": "official docs link",
  "reason_if_not_found": "explanation if found=false"
}"""

    prompt = f"Task: {task_description}\n\nWeb search results:\n{context}"

    try:
        response = with_retry(call_ai_sync, prompt, system_prompt, task_type="smart")
        data = extract_json(response)
    except Exception as e:
        return {"success": False, "error": f"Discovery AI call failed: {e}"}

    if not data or not data.get("found"):
        reason = (data or {}).get("reason_if_not_found", "No legitimate free/open API found")
        return {"success": False, "error": reason}

    tool = register_tool(data, task_description)
    return {
        "success": True,
        "status": "pending_approval",
        "message": f"Found candidate tool '{tool['name']}' - awaiting approval.",
        "tool": tool,
    }


def execute_dynamic_tool(tool: dict, params: dict = None):
    """Run an approved tool."""
    if tool.get("status") != "active":
        return {"success": False, "error": "Tool not approved yet"}

    params = params or {}
    headers = {}
    if tool.get("auth_type") == "bearer":
        env_key = f"TOOL_{tool['id']}_KEY"
        key = os.environ.get(env_key)
        if key:
            headers["Authorization"] = f"Bearer {key}"

    try:
        with httpx.Client(timeout=15) as client:
            if tool.get("method", "GET").upper() == "GET":
                resp = client.get(tool["endpoint"], params=params, headers=headers)
            else:
                resp = client.post(tool["endpoint"], json=params, headers=headers)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = resp.text
                return {"success": True, "type": "dynamic_tool", "tool": tool["name"], "data": data}

            return {
                "success": False,
                "error": f"Tool endpoint returned {resp.status_code}",
                "type": "dynamic_tool",
            }
    except Exception as e:
        return {"success": False, "error": str(e), "type": "dynamic_tool"}