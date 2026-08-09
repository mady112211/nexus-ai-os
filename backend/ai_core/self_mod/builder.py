import os
import json
import re
from datetime import datetime
from ai_core.gateway import call_ai_sync
from ai_core.self_mod.code_analyzer import CodeAnalyzer


class NexusBuilder:
    """SAFE Autonomous feature builder - only creates new files, never modifies"""

    @staticmethod
    def understand_request(user_request: str) -> dict:
        """Understand what user wants to build"""

        print(f"🧠 Understanding: {user_request}")

        system_prompt = """You are a JSON generator. Return ONLY valid JSON, nothing else.

Return this exact JSON structure:
{
  "feature_name": "Short Name",
  "feature_type": "new_page",
  "description": "Brief description",
  "requires_api": true,
  "api_type": "public_api",
  "icon_suggestion": "📰",
  "complexity": "medium",
  "estimated_files": 1
}

Rules:
- Return ONLY JSON, no other text
- No markdown code blocks
- All fields required"""

        prompt = f"Return JSON for this build request: {user_request}"

        try:
            response = call_ai_sync(prompt, system_prompt)
            print(f"📥 AI Response: {response[:200]}")

            patterns = [
                r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
                r'\{.*\}',
            ]

            for pattern in patterns:
                json_match = re.search(pattern, response, re.DOTALL)
                if json_match:
                    try:
                        understanding = json.loads(json_match.group())
                        if "feature_name" in understanding:
                            print(f"✅ Understood: {understanding.get('feature_name')}")
                            return {"success": True, "understanding": understanding}
                    except json.JSONDecodeError:
                        continue

            print("⚠️ Using fallback")
            return {
                "success": True,
                "understanding": {
                    "feature_name": user_request[:50],
                    "feature_type": "new_page",
                    "description": user_request,
                    "requires_api": True,
                    "icon_suggestion": "✨",
                    "complexity": "medium",
                    "estimated_files": 1,
                }
            }
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def create_build_plan(user_request: str, understanding: dict) -> dict:
        """Create SAFE build plan - only new file"""

        print(f"📋 Creating SAFE build plan...")

        feature_name = understanding.get("feature_name", "Feature")
        slug = re.sub(r'[^a-z0-9]+', '-', feature_name.lower()).strip('-')

        if not slug:
            slug = "new-feature"

        # SAFE: Only create ONE new page file - no modifications!
        steps = [{
            "step": 1,
            "type": "create_file",
            "file": f"frontend/src/app/{slug}/page.tsx",
            "purpose": "New page (self-contained with API calls)",
            "action": "create"
        }]

        icon = understanding.get("icon_suggestion", "✨")

        # Manual instructions for user
        manual_instructions = [
            {
                "step": "Sidebar Update",
                "file": "frontend/src/components/Sidebar.tsx",
                "instruction": f"Add this line to navItems array (before Settings):",
                "code": f"{{ label: '{feature_name}', path: '/{slug}', icon: '{icon}' }},"
            }
        ]

        return {
            "success": True,
            "plan": {
                "feature_name": feature_name,
                "slug": slug,
                "icon": icon,
                "total_steps": len(steps),
                "steps": steps,
                "understanding": understanding,
                "manual_instructions": manual_instructions,
            }
        }

    @staticmethod
    def _create_file(file_path: str, user_request: str, understanding: dict, plan: dict) -> dict:
        """Create a new SELF-CONTAINED page file"""

        example_code = ""
        example = CodeAnalyzer.read_file("frontend/src/app/agents/page.tsx")
        if example["success"]:
            example_code = example["content"][:2500]

        system_prompt = """You are NEXUS Code Generator.
Return ONLY code, no markdown, no explanations.

CRITICAL RULES:
1. Complete SELF-CONTAINED page file
2. Include 'use client' at top
3. Use useState, useEffect from 'react' (spell correctly!)
4. Use useRouter from 'next/navigation'
5. Import Sidebar from '@/components/Sidebar'
6. Import getToken from '@/lib/api' (already exists, use it!)
7. Use direct fetch() for external APIs (no need for api.ts)
8. All imports correct (spell 'react' not 'eact')
9. Balanced braces, parens, JSX tags
10. Complete working page

Pattern to follow:
- Auth check with getToken
- useState for data
- useEffect to fetch data
- Loading state
- Display data
- Error handling"""

        prompt = f"""Create a self-contained page: {file_path}

Request: {user_request}
Feature: {understanding.get('feature_name')}
Description: {understanding.get('description')}

Example pattern (follow this style):
{example_code[:1500]}

Requirements:
- Use direct fetch() to call external public APIs
- Do NOT modify any existing files
- Do NOT import from @/lib/api except getToken
- Complete page with UI
- Handle loading and errors

Generate the complete file. Output ONLY code."""

        try:
            response = call_ai_sync(prompt, system_prompt)

            code = response.strip()
            if code.startswith('```'):
                lines = code.split('\n')
                lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                code = '\n'.join(lines)

            full_path = os.path.join(CodeAnalyzer.PROJECT_ROOT, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(code)

            print(f"   ✅ Created: {file_path}")

            return {
                "success": True,
                "file": file_path,
                "action": "created",
                "lines": code.count('\n') + 1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def build_feature(user_request: str) -> dict:
        """SAFE feature build - only creates new files"""

        print(f"\n🛡️ SAFE NEXUS BUILDER STARTING")
        print(f"📝 Request: {user_request}")

        results = {
            "success": False,
            "user_request": user_request,
            "started_at": datetime.now().isoformat(),
            "steps_completed": [],
            "steps_failed": [],
            "understanding": None,
            "plan": None,
        }

        # Step 1: Understand
        understand = NexusBuilder.understand_request(user_request)
        if not understand["success"]:
            results["error"] = "Failed to understand"
            return results

        results["understanding"] = understand["understanding"]

        # Step 2: Plan (safe - only create)
        plan_result = NexusBuilder.create_build_plan(user_request, understand["understanding"])
        if not plan_result["success"]:
            results["error"] = "Failed to plan"
            return results

        results["plan"] = plan_result["plan"]
        results["manual_instructions"] = plan_result["plan"].get("manual_instructions", [])

        # Step 3: Execute (only create files)
        for step in plan_result["plan"]["steps"]:
            file_path = step["file"]
            print(f"⚙️ Step {step['step']}: {step['purpose']}")

            step_result = NexusBuilder._create_file(
                file_path,
                user_request,
                understand["understanding"],
                plan_result["plan"]
            )

            if step_result["success"]:
                results["steps_completed"].append({
                    "step": step["step"],
                    "file": step["file"],
                    "action": "created",
                })
            else:
                results["steps_failed"].append({
                    "step": step["step"],
                    "file": step["file"],
                    "error": step_result.get("error", "Unknown"),
                })

        results["success"] = len(results["steps_failed"]) == 0
        results["total_steps"] = plan_result["plan"]["total_steps"]
        results["completed_count"] = len(results["steps_completed"])
        results["failed_count"] = len(results["steps_failed"])
        results["finished_at"] = datetime.now().isoformat()

        if results["success"]:
            print(f"\n🎉 SAFE BUILD COMPLETE!")
        else:
            print(f"\n⚠️ BUILD FAILED")

        return results