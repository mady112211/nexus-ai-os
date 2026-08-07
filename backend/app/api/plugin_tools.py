from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from plugins.tools.web_search import WebSearchPlugin
from plugins.tools.file_tool import FileManagerPlugin
from plugins.tools.weather import WeatherPlugin
from plugins.plugin_manager import PluginManager

plugin_tools_bp = Blueprint("plugin_tools", __name__)

# ============ WEB SEARCH ============

@plugin_tools_bp.route("/search", methods=["POST"])
def web_search():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    enabled = PluginManager.get_enabled_plugins()
    if "web_search" not in enabled:
        return jsonify({"error": "Web Search plugin is not enabled"}), 400

    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    result = WebSearchPlugin.search(query)
    return jsonify(result)

@plugin_tools_bp.route("/search/quick", methods=["POST"])
def quick_search():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    answer = WebSearchPlugin.quick_answer(query)
    return jsonify({"answer": answer, "query": query})

# ============ FILE MANAGER ============

@plugin_tools_bp.route("/files", methods=["GET"])
def list_files():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    result = FileManagerPlugin.list_files()
    return jsonify(result)

@plugin_tools_bp.route("/files", methods=["POST"])
def write_file():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    enabled = PluginManager.get_enabled_plugins()
    if "file_manager" not in enabled:
        return jsonify({"error": "File Manager plugin is not enabled"}), 400

    data = request.get_json()
    filename = data.get("filename", "").strip()
    content = data.get("content", "").strip()

    if not filename or not content:
        return jsonify({"error": "Filename and content required"}), 400

    result = FileManagerPlugin.write_file(filename, content)
    return jsonify(result)

@plugin_tools_bp.route("/files/<filename>", methods=["GET"])
def read_file(filename):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    result = FileManagerPlugin.read_file(filename)
    return jsonify(result)

@plugin_tools_bp.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    result = FileManagerPlugin.delete_file(filename)
    return jsonify(result)

# ============ WEATHER ============

@plugin_tools_bp.route("/weather", methods=["GET"])
def get_weather():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    city = request.args.get("city", "Karachi").strip()
    result = WeatherPlugin.get_weather(city)
    return jsonify(result)

@plugin_tools_bp.route("/weather/forecast", methods=["GET"])
def get_forecast():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    city = request.args.get("city", "Karachi").strip()
    days = int(request.args.get("days", "3"))
    result = WeatherPlugin.get_forecast(city, days)
    return jsonify(result)