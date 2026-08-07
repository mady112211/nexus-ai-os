import os
import json
from datetime import datetime

class FileManagerPlugin:
    """Real file operations plugin"""

    name = "File Manager"
    slug = "file_manager"

    # Safe directory for NEXUS files
    BASE_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "nexus_files"
    )

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(cls.BASE_DIR, exist_ok=True)

    @classmethod
    def write_file(cls, filename: str, content: str) -> dict:
        """Write content to a file"""
        cls._ensure_dir()
        try:
            safe_name = os.path.basename(filename)
            filepath = os.path.join(cls.BASE_DIR, safe_name)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"📁 File written: {safe_name}")

            return {
                "success": True,
                "filename": safe_name,
                "path": filepath,
                "size": len(content),
                "message": f"File '{safe_name}' saved successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def read_file(cls, filename: str) -> dict:
        """Read content from a file"""
        cls._ensure_dir()
        try:
            safe_name = os.path.basename(filename)
            filepath = os.path.join(cls.BASE_DIR, safe_name)

            if not os.path.exists(filepath):
                return {
                    "success": False,
                    "error": f"File '{safe_name}' not found"
                }

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "filename": safe_name,
                "content": content,
                "size": len(content)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def list_files(cls) -> dict:
        """List all NEXUS files"""
        cls._ensure_dir()
        try:
            files = []
            for f in os.listdir(cls.BASE_DIR):
                filepath = os.path.join(cls.BASE_DIR, f)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        "name": f,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(
                            stat.st_mtime
                        ).strftime("%Y-%m-%d %H:%M"),
                    })

            return {
                "success": True,
                "files": files,
                "total": len(files)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def delete_file(cls, filename: str) -> dict:
        """Delete a file"""
        cls._ensure_dir()
        try:
            safe_name = os.path.basename(filename)
            filepath = os.path.join(cls.BASE_DIR, safe_name)

            if not os.path.exists(filepath):
                return {
                    "success": False,
                    "error": f"File '{safe_name}' not found"
                }

            os.remove(filepath)

            return {
                "success": True,
                "message": f"File '{safe_name}' deleted"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def save_mission_report(cls, mission_title: str, content: str) -> dict:
        """Save a mission report as file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c for c in mission_title if c.isalnum() or c in (' ', '-', '_')
        ).rstrip()
        filename = f"mission_{safe_title[:30]}_{timestamp}.txt"
        return cls.write_file(filename, content)