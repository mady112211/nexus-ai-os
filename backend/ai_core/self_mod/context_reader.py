import os
import re
from ai_core.self_mod.code_analyzer import CodeAnalyzer


class ContextReader:
    """Reads context around a file - imports, related files, patterns"""

    @classmethod
    def get_file_context(cls, target_file: str) -> dict:
        """Get complete context for a file"""

        # Read main file
        main_file = CodeAnalyzer.read_file(target_file)
        if not main_file["success"]:
            return {"success": False, "error": "File not found"}

        content = main_file["content"]

        # Extract imports
        imports = cls._extract_imports(content, target_file)

        # Find related files
        related_files = cls._find_related_files(target_file, imports)

        # Read related files (short version)
        related_content = {}
        for rel_file in related_files[:5]:  # Max 5 related files
            rel_data = CodeAnalyzer.read_file(rel_file)
            if rel_data["success"]:
                # Only first 100 lines to save tokens
                lines = rel_data["content"].split('\n')
                related_content[rel_file] = '\n'.join(lines[:100])

        # Find similar pattern files
        similar_files = cls._find_similar_files(target_file)

        return {
            "success": True,
            "target_file": target_file,
            "content": content,
            "imports": imports,
            "related_files": related_content,
            "similar_files": similar_files,
            "file_type": cls._get_file_type(target_file),
        }

    @classmethod
    def _extract_imports(cls, content: str, file_path: str) -> list:
        """Extract all imports from file"""
        imports = []

        if file_path.endswith(('.tsx', '.ts')):
            # TypeScript/React imports
            pattern = r"import\s+.*?\s+from\s+['\"](.+?)['\"]"
            imports = re.findall(pattern, content)
        elif file_path.endswith('.py'):
            # Python imports
            pattern = r"(?:from\s+(\S+)\s+import|import\s+(\S+))"
            matches = re.findall(pattern, content)
            imports = [m[0] or m[1] for m in matches]

        return imports

    @classmethod
    def _find_related_files(cls, target_file: str, imports: list) -> list:
        """Find files related through imports"""
        related = []
        base_dir = os.path.dirname(target_file)

        for imp in imports:
            # Skip external packages
            if imp.startswith('.') or imp.startswith('@/') or imp.startswith('app.') or imp.startswith('ai_core.'):
                # Resolve relative path
                resolved = cls._resolve_import(imp, target_file)
                if resolved:
                    related.append(resolved)

        return related

    @classmethod
    def _resolve_import(cls, imp: str, from_file: str) -> str:
        """Resolve an import path"""
        # Frontend @/ imports
        if imp.startswith('@/'):
            path = imp.replace('@/', 'frontend/src/')
            # Try .tsx first
            for ext in ['.tsx', '.ts', '/page.tsx', '/index.tsx']:
                test_path = path + ext
                full = os.path.join(CodeAnalyzer.PROJECT_ROOT, test_path)
                if os.path.exists(full):
                    return test_path.replace("\\", "/")

        # Python imports
        if imp.startswith('app.') or imp.startswith('ai_core.'):
            path = 'backend/' + imp.replace('.', '/') + '.py'
            full = os.path.join(CodeAnalyzer.PROJECT_ROOT, path)
            if os.path.exists(full):
                return path.replace("\\", "/")

        return None

    @classmethod
    def _find_similar_files(cls, target_file: str, max_files: int = 3) -> list:
        """Find files with similar structure/purpose"""
        similar = []
        target_name = os.path.basename(target_file)
        target_dir = os.path.dirname(target_file)

        # If it's a page.tsx, find other pages
        if target_name == 'page.tsx':
            parent = os.path.dirname(target_dir)
            parent_full = os.path.join(CodeAnalyzer.PROJECT_ROOT, parent)

            if os.path.exists(parent_full):
                for item in os.listdir(parent_full):
                    item_path = os.path.join(parent_full, item)
                    if os.path.isdir(item_path):
                        page_file = os.path.join(item_path, 'page.tsx')
                        if os.path.exists(page_file):
                            rel = os.path.relpath(page_file, CodeAnalyzer.PROJECT_ROOT)
                            rel = rel.replace("\\", "/")
                            if rel != target_file:
                                similar.append(rel)

        return similar[:max_files]

    @classmethod
    def _get_file_type(cls, file_path: str) -> str:
        """Determine file type"""
        if file_path.endswith('.tsx'):
            return 'react_component'
        if file_path.endswith('.ts'):
            return 'typescript'
        if file_path.endswith('.py'):
            return 'python'
        if file_path.endswith('.css'):
            return 'css'
        return 'unknown'

    @classmethod
    def build_context_prompt(cls, context: dict) -> str:
        """Build a comprehensive prompt with context"""

        prompt = f"""=== TARGET FILE ===
Path: {context['target_file']}
Type: {context['file_type']}

=== CURRENT CODE ===
{context['content']}

"""

        if context['similar_files']:
            prompt += "\n=== SIMILAR FILES (follow their patterns) ===\n"
            for sim_file in context['similar_files'][:2]:
                sim_data = CodeAnalyzer.read_file(sim_file)
                if sim_data["success"]:
                    lines = sim_data["content"].split('\n')
                    prompt += f"\n--- {sim_file} (first 80 lines) ---\n"
                    prompt += '\n'.join(lines[:80])
                    prompt += "\n"

        if context['imports']:
            prompt += f"\n=== FILE IMPORTS ===\n{', '.join(context['imports'][:10])}\n"

        return prompt