import os
from ai_core.gateway import call_ai_sync
from ai_core.self_mod.code_analyzer import CodeAnalyzer
from ai_core.self_mod.backup_manager import BackupManager


class CodeModifier:
    """AI-powered code modification with safety"""

    @staticmethod
    def plan_modification(user_request: str) -> dict:
        """AI plans what to modify"""

        structure = CodeAnalyzer.get_project_structure()
        structure_summary = CodeModifier._summarize_structure(structure)

        system_prompt = """You are NEXUS Self-Modification AI.
Your job is to analyze user requests and plan code changes.

You must respond with ONLY valid JSON:
{
  "understanding": "What user wants",
  "target_files": ["path/to/file1"],
  "change_type": "create",
  "risk_level": "low",
  "description": "What you will do",
  "estimated_changes": "brief summary"
}

Rules:
- Only modify files in backend/ or frontend/src/
- Be specific with file paths
- Assess risk honestly"""

        prompt = f"""User Request: {user_request}

Available Project Structure:
{structure_summary}

Analyze and create a modification plan. Respond with JSON only."""

        try:
            response = call_ai_sync(prompt, system_prompt)
            import json, re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return {"success": True, "plan": plan}
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": "Could not create plan"}

    @staticmethod
    def generate_code(user_request: str, target_file: str) -> dict:
        """AI generates the actual code for a file"""

        current = CodeAnalyzer.read_file(target_file)
        current_content = current.get("content", "") if current["success"] else ""

        system_prompt = """You are NEXUS Code Generator.
Your job is to write complete, working code files.

Rules:
1. Return ONLY the complete file code
2. No markdown, no explanations, no code blocks
3. Just pure code
4. Maintain existing style
5. Complete file - not just changes"""

        prompt = f"""User Request: {user_request}

Target File: {target_file}

Current File Content:
{current_content[:3000] if current_content else "(new file)"}

Generate the complete new code for this file."""

        try:
            response = call_ai_sync(prompt, system_prompt)

            code = response.strip()
            if code.startswith('```'):
                lines = code.split('\n')
                code = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])

            return {
                "success": True,
                "file": target_file,
                "current_code": current_content,
                "new_code": code,
                "lines_before": current_content.count('\n') + 1 if current_content else 0,
                "lines_after": code.count('\n') + 1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def apply_change(target_file: str, new_code: str) -> dict:
        """Apply approved change (with backup)"""

        if not CodeAnalyzer._is_safe_path(target_file):
            return {"success": False, "error": "Path not allowed"}

        backup = BackupManager.backup_file(target_file)

        full_path = os.path.join(CodeAnalyzer.PROJECT_ROOT, target_file)

        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_code)

            return {
                "success": True,
                "file": target_file,
                "backup": backup.get("backup", "no_backup"),
                "size": len(new_code),
                "message": "Code applied successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _summarize_structure(structure: dict, max_items: int = 30) -> str:
        """Create text summary of project structure"""
        lines = []

        def add_items(items, indent=0):
            count = 0
            for item in items:
                if count >= max_items:
                    break
                prefix = "  " * indent
                if item["type"] == "folder":
                    lines.append(f"{prefix}[FOLDER] {item['path']}/")
                    if "children" in item:
                        add_items(item["children"], indent + 1)
                else:
                    lines.append(f"{prefix}[FILE] {item['path']}")
                count += 1

        for folder, items in structure.items():
            lines.append(f"\n{folder}/:")
            add_items(items)

        return "\n".join(lines)