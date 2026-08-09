import os
import re
import json
from ai_core.gateway import call_ai_sync
from ai_core.self_mod.code_analyzer import CodeAnalyzer
from ai_core.self_mod.backup_manager import BackupManager
from ai_core.self_mod.context_reader import ContextReader
from ai_core.self_mod.code_validator import CodeValidator


class SmartModifier:
    """Intelligent code modification with context awareness"""

    MAX_RETRIES = 2

    @staticmethod
    def smart_plan(user_request: str) -> dict:
        """Enhanced planning with better context"""

        structure = CodeAnalyzer.get_project_structure()
        structure_summary = SmartModifier._compact_structure(structure)

        system_prompt = """You are NEXUS Smart Planner.
You analyze user requests and create precise modification plans.

CRITICAL: Only use files that EXIST in the project structure below.
Do NOT invent file paths. Only choose from the actual files shown.

Response format (ONLY valid JSON):
{
  "understanding": "Clear statement of what user wants",
  "target_files": ["exact/path/to/file.tsx"],
  "change_type": "modify",
  "risk_level": "low",
  "description": "Specific description of changes",
  "reasoning": "Why these files were chosen"
}

Rules:
- ONLY use file paths from the structure below
- Never invent or guess file paths
- Prefer 1-2 files over many
- Use exact paths shown (frontend/src/app/... or backend/...)
- Common Next.js pattern: pages are at frontend/src/app/PAGE_NAME/page.tsx
- Assess risk: low (text/color), medium (logic), high (structure)"""

        prompt = f"""User Request: {user_request}

Project Structure (ONLY use files from here):
{structure_summary}

Create a focused modification plan. Choose the MINIMUM files needed.
IMPORTANT: Only use file paths that appear in the structure above."""

        try:
            response = call_ai_sync(prompt, system_prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())

                # Validate target files exist
                if "target_files" in plan:
                    valid_files = []
                    for file_path in plan["target_files"]:
                        full_path = os.path.join(CodeAnalyzer.PROJECT_ROOT, file_path)
                        if os.path.exists(full_path):
                            valid_files.append(file_path)
                        else:
                            print(f"⚠️ AI suggested non-existent file: {file_path}")

                    if not valid_files:
                        return {
                            "success": False,
                            "error": f"AI suggested files that don't exist: {plan['target_files']}. Try being more specific with the file path."
                        }

                    plan["target_files"] = valid_files

                return {"success": True, "plan": plan}
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": "Could not create plan"}

    @staticmethod
    def smart_generate(user_request: str, target_file: str) -> dict:
        """Generate code with full context and validation"""

        context = ContextReader.get_file_context(target_file)
        if not context["success"]:
            return {"success": False, "error": context.get("error", "Context failed")}

        context_prompt = ContextReader.build_context_prompt(context)

        last_error = None
        for attempt in range(SmartModifier.MAX_RETRIES + 1):
            print(f"🧠 Generation attempt {attempt + 1}/{SmartModifier.MAX_RETRIES + 1}")

            result = SmartModifier._generate_attempt(
                user_request,
                target_file,
                context_prompt,
                context["content"],
                previous_error=last_error
            )

            if result["success"]:
                validation = CodeValidator.validate(result["new_code"], target_file)
                comparison = CodeValidator.compare_with_original(
                    result["new_code"],
                    context["content"]
                )

                if validation["valid"] and len(comparison["warnings"]) == 0:
                    print(f"✅ Code validated successfully")
                    result["validation"] = validation
                    result["current_code"] = context["content"]
                    result["lines_before"] = context["content"].count('\n') + 1
                    result["lines_after"] = result["new_code"].count('\n') + 1
                    return result
                else:
                    all_issues = validation["errors"] + validation["warnings"] + comparison["warnings"]
                    last_error = "; ".join(all_issues[:3])
                    print(f"⚠️ Validation issues: {last_error}")

                    if attempt == SmartModifier.MAX_RETRIES:
                        result["validation"] = validation
                        result["comparison_warnings"] = comparison["warnings"]
                        result["current_code"] = context["content"]
                        result["lines_before"] = context["content"].count('\n') + 1
                        result["lines_after"] = result["new_code"].count('\n') + 1
                        result["has_warnings"] = True
                        return result
            else:
                last_error = result.get("error", "Unknown")

        return {"success": False, "error": last_error or "Generation failed"}

    @staticmethod
    def _generate_attempt(user_request: str, target_file: str,
                         context_prompt: str, original_code: str,
                         previous_error: str = None) -> dict:
        """Single generation attempt"""

        error_instruction = ""
        if previous_error:
            error_instruction = f"""
IMPORTANT - PREVIOUS ATTEMPT HAD ISSUES:
{previous_error}

Fix these issues in your new code. Be extra careful with:
- Complete file (all opening/closing tags)
- All imports included (spell correctly: 'react' not 'eact')
- Balanced braces and parens
- No markdown blocks
- Correct import statements
"""

        system_prompt = f"""You are NEXUS Smart Code Generator.
Your job is to write PERFECT, COMPLETE, WORKING code.

CRITICAL RULES:
1. Return ONLY the complete file code
2. NO markdown blocks, NO explanations, NO comments about changes
3. Complete file from first line to last line
4. Maintain the exact style of existing code
5. Include ALL imports needed - spell them correctly
6. Balance ALL braces, parens, and JSX tags
7. Include 'use client' if using React hooks
8. Preserve existing functionality unless explicitly asked to change
9. Follow patterns from similar files if shown
10. Import from 'react' NOT 'eact'
11. Import from 'next/navigation' NOT 'ext/navigation'

{error_instruction}
"""

        prompt = f"""User Request: {user_request}

{context_prompt}

=== YOUR TASK ===
Generate the COMPLETE new code for: {target_file}

Requirements:
- Complete file (nothing missing)
- Working code (no syntax errors)
- Follow existing patterns
- All tags/braces balanced
- Correct import spellings
- Ready to save and run

Output ONLY the code, nothing else."""

        try:
            response = call_ai_sync(prompt, system_prompt)

            code = response.strip()

            if code.startswith('```'):
                lines = code.split('\n')
                lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                code = '\n'.join(lines)

            if code.startswith("Here"):
                match = re.search(r"^(import |'use |from |def |class |const )", code, re.MULTILINE)
                if match:
                    code = code[match.start():]

            return {
                "success": True,
                "file": target_file,
                "new_code": code,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def smart_apply(target_file: str, new_code: str, skip_validation: bool = False) -> dict:
        """Apply with final validation and backup"""

        if not CodeAnalyzer._is_safe_path(target_file):
            return {"success": False, "error": "Path not allowed"}

        if not skip_validation:
            validation = CodeValidator.validate(new_code, target_file)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Validation failed: " + "; ".join(validation["errors"]),
                    "validation": validation
                }

        backup = BackupManager.backup_file(target_file)

        full_path = os.path.join(CodeAnalyzer.PROJECT_ROOT, target_file)

        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_code)

            print(f"✅ Applied smart change to {target_file}")

            return {
                "success": True,
                "file": target_file,
                "backup": backup.get("backup", "no_backup"),
                "size": len(new_code),
                "message": "Smart modification applied!",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _compact_structure(structure: dict, max_items: int = 80) -> str:
        """Compact structure summary"""
        lines = []

        def add_items(items, indent=0, count=[0]):
            for item in items:
                if count[0] >= max_items:
                    return
                prefix = "  " * indent
                if item["type"] == "folder":
                    lines.append(f"{prefix}{item['path']}/")
                    if "children" in item:
                        add_items(item["children"], indent + 1, count)
                else:
                    lines.append(f"{prefix}{item['path']}")
                    count[0] += 1

        for folder, items in structure.items():
            lines.append(f"\n{folder}:")
            add_items(items)

        return "\n".join(lines)