from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from plugins.plugin_manager import PluginManager

plugins_bp = Blueprint("plugins", __name__)

@plugins_bp.route("/", methods=["GET"])
def get_plugins():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    by_category = request.args.get("by_category", "false").lower() == "true"

    if by_category:
        categories = PluginManager.get_plugins_by_category()
        return jsonify({"categories": categories})

    plugins = PluginManager.get_all_plugins()
    return jsonify({"plugins": plugins})

@plugins_bp.route("/<slug>", methods=["GET"])
def get_plugin(slug):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    plugin = PluginManager.get_plugin_by_slug(slug)
    if not plugin:
        return jsonify({"error": "Plugin not found"}), 404

    return jsonify(plugin)

@plugins_bp.route("/<slug>/toggle", methods=["POST"])
def toggle_plugin(slug):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    enabled = data.get("enabled", False)

    result = PluginManager.toggle_plugin(slug, enabled)
    if not result:
        return jsonify({"error": "Plugin not found"}), 404

    return jsonify({
        "message": f"Plugin {'enabled' if enabled else 'disabled'} successfully",
        "plugin": result
    })

@plugins_bp.route("/<slug>/config", methods=["PUT"])
def update_config(slug):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    config = data.get("config", {})

    result = PluginManager.update_plugin_config(slug, config)
    if not result:
        return jsonify({"error": "Plugin not found"}), 404

    return jsonify({
        "message": "Plugin config updated successfully",
        "plugin": result
    })

@plugins_bp.route("/enabled", methods=["GET"])
def get_enabled():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    enabled = PluginManager.get_enabled_plugins()
    return jsonify({"enabled_plugins": enabled})