import os
import shutil
from datetime import datetime


class BackupManager:
    """Manages code backups before modifications"""

    PROJECT_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
    )

    BACKUP_DIR = os.path.join(PROJECT_ROOT, "backend", "code_backups")

    @classmethod
    def _ensure_backup_dir(cls):
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)

    @classmethod
    def backup_file(cls, relative_path: str) -> dict:
        """Create backup of a file"""
        cls._ensure_backup_dir()

        full_path = os.path.join(cls.PROJECT_ROOT, relative_path)
        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = relative_path.replace("/", "_").replace("\\", "_")
        backup_name = f"{timestamp}_{safe_name}"
        backup_path = os.path.join(cls.BACKUP_DIR, backup_name)

        try:
            shutil.copy2(full_path, backup_path)
            return {
                "success": True,
                "original": relative_path,
                "backup": backup_name,
                "backup_path": backup_path,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def list_backups(cls) -> list:
        """List all backups"""
        cls._ensure_backup_dir()
        try:
            backups = []
            for f in sorted(os.listdir(cls.BACKUP_DIR), reverse=True):
                full_path = os.path.join(cls.BACKUP_DIR, f)
                if os.path.isfile(full_path):
                    stat = os.stat(full_path)
                    backups.append({
                        "name": f,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    })
            return backups[:50]
        except Exception:
            return []

    @classmethod
    def restore_backup(cls, backup_name: str, target_path: str) -> dict:
        """Restore a backup"""
        cls._ensure_backup_dir()

        backup_path = os.path.join(cls.BACKUP_DIR, backup_name)
        target_full = os.path.join(cls.PROJECT_ROOT, target_path)

        if not os.path.exists(backup_path):
            return {"success": False, "error": "Backup not found"}

        try:
            shutil.copy2(backup_path, target_full)
            return {"success": True, "restored": target_path}
        except Exception as e:
            return {"success": False, "error": str(e)}