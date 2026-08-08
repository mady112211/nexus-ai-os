from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from ai_core.self_mod.code_analyzer import CodeAnalyzer
from ai_core.self_mod.code_modifier import CodeModifier
from ai_core.self_mod.backup_manager import BackupManager

self_mod_bp = Blueprint("self_mod", __name__)


@self_mod_bp.route("/structure", methods=["GET"])
def get_structure():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    structure = CodeAnalyzer.get_project_structure()
    return jsonify({"structure": structure})


@self_mod_bp.route("/read", methods=["POST"])
def read_file():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    path = data.get("path", "")
    result = CodeAnalyzer.read_file(path)
    return jsonify(result)


@self_mod_bp.route("/plan", methods=["POST"])
def plan_change():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    request_text = data.get("request", "").strip()

    if not request_text:
        return jsonify({"error": "Request is required"}), 400

    result = CodeModifier.plan_modification(request_text)
    return jsonify(result)


@self_mod_bp.route("/generate", methods=["POST"])
def generate_code():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    request_text = data.get("request", "").strip()
    target_file = data.get("target_file", "").strip()

    if not request_text or not target_file:
        return jsonify({"error": "Request and target_file required"}), 400

    result = CodeModifier.generate_code(request_text, target_file)
    return jsonify(result)


@self_mod_bp.route("/apply", methods=["POST"])
def apply_change():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    target_file = data.get("target_file", "").strip()
    new_code = data.get("new_code", "")

    if not target_file or not new_code:
        return jsonify({"error": "Missing data"}), 400

    result = CodeModifier.apply_change(target_file, new_code)
    return jsonify(result)


@self_mod_bp.route("/backups", methods=["GET"])
def list_backups():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    backups = BackupManager.list_backups()
    return jsonify({"backups": backups})


@self_mod_bp.route("/search", methods=["POST"])
def search_code():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query required"}), 400

    results = CodeAnalyzer.search_code(query)
    return jsonify({"results": results})