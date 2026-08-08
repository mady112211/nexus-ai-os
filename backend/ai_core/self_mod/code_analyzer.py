import os

class CodeAnalyzer:
    """Analyzes NEXUS's own codebase"""

    PROJECT_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
    )

    ALLOWED_FOLDERS = ["backend", "frontend/src"]
    ALLOWED_EXTENSIONS = [".py", ".tsx", ".ts", ".css"]
    BLOCKED_FILES = [".env", "nexus.db", "package-lock.json"]

    @classmethod
    def get_project_structure(cls) -> dict:
        """Get overall project structure"""
        structure = {}
        for folder in cls.ALLOWED_FOLDERS:
            folder_path = os.path.join(cls.PROJECT_ROOT, folder)
            if os.path.exists(folder_path):
                structure[folder] = cls._scan_folder(folder_path)
        return structure

    @classmethod
    def _scan_folder(cls, path: str, max_depth: int = 4) -> list:
        """Recursively scan folder"""
        items = []
        try:
            for entry in os.listdir(path):
                if entry.startswith('.') or entry in ['node_modules', '__pycache__', 'venv', '.next']:
                    continue

                full_path = os.path.join(path, entry)
                relative_path = os.path.relpath(full_path, cls.PROJECT_ROOT)

                if os.path.isfile(full_path):
                    ext = os.path.splitext(entry)[1]
                    if ext in cls.ALLOWED_EXTENSIONS:
                        items.append({
                            "type": "file",
                            "name": entry,
                            "path": relative_path.replace("\\", "/"),
                            "size": os.path.getsize(full_path),
                        })
                elif os.path.isdir(full_path) and max_depth > 0:
                    items.append({
                        "type": "folder",
                        "name": entry,
                        "path": relative_path.replace("\\", "/"),
                        "children": cls._scan_folder(full_path, max_depth - 1),
                    })
        except Exception:
            pass
        return items

    @classmethod
    def read_file(cls, relative_path: str) -> dict:
        """Read a file safely"""
        if not cls._is_safe_path(relative_path):
            return {"success": False, "error": "Path not allowed"}

        full_path = os.path.join(cls.PROJECT_ROOT, relative_path)

        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "success": True,
                "path": relative_path,
                "content": content,
                "size": len(content),
                "lines": content.count('\n') + 1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def _is_safe_path(cls, relative_path: str) -> bool:
        """Check if path is allowed"""
        normalized = relative_path.replace("\\", "/")

        for blocked in cls.BLOCKED_FILES:
            if blocked in normalized:
                return False

        for folder in cls.ALLOWED_FOLDERS:
            if normalized.startswith(folder):
                return True

        return False

    @classmethod
    def search_code(cls, query: str) -> list:
        """Search for text in code files"""
        results = []
        for folder in cls.ALLOWED_FOLDERS:
            folder_path = os.path.join(cls.PROJECT_ROOT, folder)
            if os.path.exists(folder_path):
                results.extend(cls._search_in_folder(folder_path, query))
        return results[:20]

    @classmethod
    def _search_in_folder(cls, path: str, query: str) -> list:
        matches = []
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', 'venv', '.next']]

                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext not in cls.ALLOWED_EXTENSIONS:
                        continue

                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if query.lower() in content.lower():
                            relative = os.path.relpath(full_path, cls.PROJECT_ROOT)
                            matches.append({
                                "path": relative.replace("\\", "/"),
                                "name": file,
                                "matches": content.lower().count(query.lower()),
                            })
                    except Exception:
                        continue
        except Exception:
            pass
        return matches