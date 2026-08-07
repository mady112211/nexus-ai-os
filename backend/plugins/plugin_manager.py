from app.database import SessionLocal, Plugin

class PluginManager:
    """Manages all NEXUS plugins"""

    @staticmethod
    def get_all_plugins():
        db = SessionLocal()
        try:
            plugins = db.query(Plugin).order_by(Plugin.category, Plugin.name).all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "version": p.version,
                    "category": p.category,
                    "icon": p.icon,
                    "is_enabled": p.is_enabled,
                    "is_installed": p.is_installed,
                    "config": p.config or {},
                    "created_at": str(p.created_at),
                }
                for p in plugins
            ]
        finally:
            db.close()

    @staticmethod
    def get_enabled_plugins():
        db = SessionLocal()
        try:
            plugins = db.query(Plugin).filter(Plugin.is_enabled == True).all()
            return [p.slug for p in plugins]
        finally:
            db.close()

    @staticmethod
    def toggle_plugin(slug: str, enabled: bool):
        db = SessionLocal()
        try:
            plugin = db.query(Plugin).filter(Plugin.slug == slug).first()
            if not plugin:
                return None
            plugin.is_enabled = enabled
            db.commit()
            return {
                "id": plugin.id,
                "name": plugin.name,
                "slug": plugin.slug,
                "is_enabled": plugin.is_enabled,
            }
        finally:
            db.close()

    @staticmethod
    def update_plugin_config(slug: str, config: dict):
        db = SessionLocal()
        try:
            plugin = db.query(Plugin).filter(Plugin.slug == slug).first()
            if not plugin:
                return None
            plugin.config = config
            db.commit()
            return {
                "id": plugin.id,
                "name": plugin.name,
                "slug": plugin.slug,
                "config": plugin.config,
            }
        finally:
            db.close()

    @staticmethod
    def get_plugin_by_slug(slug: str):
        db = SessionLocal()
        try:
            plugin = db.query(Plugin).filter(Plugin.slug == slug).first()
            if not plugin:
                return None
            return {
                "id": plugin.id,
                "name": plugin.name,
                "slug": plugin.slug,
                "description": plugin.description,
                "version": plugin.version,
                "category": plugin.category,
                "icon": plugin.icon,
                "is_enabled": plugin.is_enabled,
                "config": plugin.config or {},
            }
        finally:
            db.close()

    @staticmethod
    def get_plugins_by_category():
        db = SessionLocal()
        try:
            plugins = db.query(Plugin).order_by(Plugin.category, Plugin.name).all()
            categories = {}
            for p in plugins:
                cat = p.category
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append({
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "icon": p.icon,
                    "is_enabled": p.is_enabled,
                    "config": p.config or {},
                })
            return categories
        finally:
            db.close()