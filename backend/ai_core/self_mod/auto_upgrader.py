import os
import json
import re
from datetime import datetime
from ai_core.gateway import call_ai_sync
from ai_core.self_mod.code_analyzer import CodeAnalyzer


class AutoUpgrader:
    """NEXUS analyzes itself and suggests improvements"""

    @staticmethod
    def scan_system() -> dict:
        """Scan entire NEXUS system for issues"""

        print("🔍 Starting system scan...")

        structure = CodeAnalyzer.get_project_structure()

        stats = AutoUpgrader._count_files(structure)
        issues = AutoUpgrader._detect_issues(structure)

        return {
            "success": True,
            "scanned_at": datetime.now().isoformat(),
            "stats": stats,
            "issues": issues,
            "total_issues": len(issues),
        }

    @staticmethod
    def _count_files(structure: dict) -> dict:
        counts = {
            "total_files": 0,
            "tsx_files": 0,
            "python_files": 0,
            "css_files": 0,
            "folders": 0,
        }

        def scan(items):
            for item in items:
                if item["type"] == "folder":
                    counts["folders"] += 1
                    if "children" in item:
                        scan(item["children"])
                else:
                    counts["total_files"] += 1
                    if item["path"].endswith('.tsx'):
                        counts["tsx_files"] += 1
                    elif item["path"].endswith('.py'):
                        counts["python_files"] += 1
                    elif item["path"].endswith('.css'):
                        counts["css_files"] += 1

        for folder, items in structure.items():
            scan(items)

        return counts

    @staticmethod
    def _detect_issues(structure: dict) -> list:
        issues = []

        def check_files(items):
            for item in items:
                if item["type"] == "folder" and "children" in item:
                    check_files(item["children"])
                elif item["type"] == "file":
                    file_issues = AutoUpgrader._analyze_file(item["path"])
                    issues.extend(file_issues)

        for folder, items in structure.items():
            check_files(items)

        return issues

    @staticmethod
    def _analyze_file(file_path: str) -> list:
        issues = []

        result = CodeAnalyzer.read_file(file_path)
        if not result["success"]:
            return issues

        content = result["content"]
        line_count = content.count('\n') + 1

        if line_count > 500 and file_path.endswith('.tsx'):
            issues.append({
                "file": file_path,
                "type": "code_quality",
                "severity": "medium",
                "title": "Large file",
                "description": f"File has {line_count} lines",
                "suggestion": "Split into smaller components"
            })

        if 'console.log' in content and file_path.endswith(('.tsx', '.ts')):
            count = content.count('console.log')
            if count > 0:
                issues.append({
                    "file": file_path,
                    "type": "code_quality",
                    "severity": "low",
                    "title": "Console.log statements",
                    "description": f"Found {count} console.log statements",
                    "suggestion": "Remove console.log for production"
                })

        todos = re.findall(r'(?:TODO|FIXME|XXX)[\s:]+(.+)', content, re.IGNORECASE)
        if todos:
            issues.append({
                "file": file_path,
                "type": "todo",
                "severity": "low",
                "title": f"{len(todos)} TODO comments",
                "description": f"First TODO: {todos[0][:100]}",
                "suggestion": "Address pending TODOs"
            })

        if file_path.endswith(('.tsx', '.ts', '.py')):
            async_count = content.count('async ')
            try_count = content.count('try')
            if async_count > 3 and try_count < async_count / 2:
                issues.append({
                    "file": file_path,
                    "type": "error_handling",
                    "severity": "medium",
                    "title": "Missing error handling",
                    "description": f"{async_count} async ops, {try_count} try blocks",
                    "suggestion": "Add try/catch"
                })

        if len(content.strip()) < 20:
            issues.append({
                "file": file_path,
                "type": "empty_file",
                "severity": "high",
                "title": "Empty file",
                "description": f"Only {len(content)} characters",
                "suggestion": "Remove or implement"
            })

        return issues

    @staticmethod
    def generate_suggestions() -> dict:
        print("🧠 AI generating suggestions...")

        scan_result = AutoUpgrader.scan_system()

        if not scan_result["success"]:
            return {"success": False, "error": "Scan failed"}

        stats = scan_result["stats"]
        issues = scan_result["issues"][:10]

        issues_text = ""
        for i, issue in enumerate(issues, 1):
            issues_text += f"\n{i}. [{issue['severity'].upper()}] {issue['file']}\n"
            issues_text += f"   Issue: {issue['title']}\n"
            issues_text += f"   Suggestion: {issue['suggestion']}\n"

        stats_text = f"""
Project Statistics:
- Total Files: {stats['total_files']}
- React Components: {stats['tsx_files']}
- Python Files: {stats['python_files']}
- Folders: {stats['folders']}
"""

        system_prompt = """You are NEXUS Self-Improvement AI.

Response format (ONLY valid JSON):
{
  "improvements": [
    {
      "id": 1,
      "title": "Short title",
      "priority": "high",
      "category": "performance",
      "description": "What needs to change",
      "benefit": "How this helps users",
      "estimated_impact": "high",
      "auto_implementable": true,
      "files_affected": ["path/to/file"]
    }
  ]
}

Rules:
- Generate 3-5 improvements
- Priority: high/medium/low
- Category: performance/security/UX/feature/quality
- Be specific and actionable"""

        prompt = f"""Analyze NEXUS AI OS and suggest improvements.

{stats_text}

Issues:
{issues_text if issues else "No major issues"}

Focus on:
1. UX improvements
2. Missing features
3. Code quality
4. Performance

Return JSON only."""

        try:
            response = call_ai_sync(prompt, system_prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                return {
                    "success": True,
                    "scan_stats": stats,
                    "issues_found": len(scan_result["issues"]),
                    "improvements": suggestions.get("improvements", []),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": "Could not generate"}

    @staticmethod
    def get_quick_wins() -> dict:
        scan = AutoUpgrader.scan_system()
        if not scan["success"]:
            return {"success": False, "error": "Scan failed"}

        quick_wins = []

        for issue in scan["issues"]:
            if issue["type"] == "code_quality" and issue["severity"] == "low":
                if "console.log" in issue["title"]:
                    quick_wins.append({
                        "type": "remove_console_logs",
                        "file": issue["file"],
                        "action": "Remove console.log statements",
                        "safe": True,
                    })

        return {
            "success": True,
            "quick_wins": quick_wins[:5],
        }