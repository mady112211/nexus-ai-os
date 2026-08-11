import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from app.api.auth import auth_bp
from app.api.missions import missions_bp
from app.api.agents import agents_bp
from app.api.dashboard import dashboard_bp
from app.api.memory import memory_bp
from app.api.chat import chat_bp
from app.api.settings import settings_bp
from app.api.plugins import plugins_bp
from app.api.plugin_tools import plugin_tools_bp
from app.api.notifications import notifications_bp
from app.api.analytics import analytics_bp
from app.database import init_db
from app.api.workspaces import workspaces_bp
from app.api.self_mod import self_mod_bp
from app.api.image_ai import image_ai_bp
from app.api.core_brain import core_brain_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "nexus-secret-2024")
    app.config["DEBUG"] = False

    CORS(app, origins=["http://localhost:3000"])

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(missions_bp, url_prefix="/api/missions")
    app.register_blueprint(agents_bp, url_prefix="/api/agents")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(memory_bp, url_prefix="/api/memory")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(plugins_bp, url_prefix="/api/plugins")
    app.register_blueprint(plugin_tools_bp, url_prefix="/api/tools")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(workspaces_bp, url_prefix="/api/workspaces")
    app.register_blueprint(self_mod_bp, url_prefix="/api/self-mod")
    app.register_blueprint(image_ai_bp, url_prefix="/api/image-ai")
    app.register_blueprint(core_brain_bp, url_prefix="/api/brain")

    @app.route("/")
    def home():
        return jsonify({
            "name": "NEXUS AI OS",
            "version": "0.9.0",
            "status": "Running",
            "message": "One Command. Infinite Execution.",
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "version": "0.9.0"})

    return app

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized!")
    app = create_app()
    print("🚀 NEXUS AI OS v0.9.0 Starting...")
    print("📍 URL: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    