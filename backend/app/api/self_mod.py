from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from ai_core.self_mod.code_analyzer import CodeAnalyzer
from ai_core.self_mod.code_modifier import CodeModifier
from ai_core.self_mod.smart_modifier import SmartModifier
from ai_core.self_mod.backup_manager import BackupManager
from ai_core.self_mod.auto_upgrader import AutoUpgrader

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
    """Smart planning"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    request_text = data.get("request", "").strip()

    if not request_text:
        return jsonify({"error": "Request is required"}), 400

    # Use smart planner
    result = SmartModifier.smart_plan(request_text)
    return jsonify(result)


@self_mod_bp.route("/generate", methods=["POST"])
def generate_code():
    """Smart code generation with context and validation"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    request_text = data.get("request", "").strip()
    target_file = data.get("target_file", "").strip()

    if not request_text or not target_file:
        return jsonify({"error": "Request and target_file required"}), 400

    # Use smart generator
    result = SmartModifier.smart_generate(request_text, target_file)
    return jsonify(result)


@self_mod_bp.route("/apply", methods=["POST"])
def apply_change():
    """Apply with validation"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    target_file = data.get("target_file", "").strip()
    new_code = data.get("new_code", "")
    force = data.get("force", False)

    if not target_file or not new_code:
        return jsonify({"error": "Missing data"}), 400

    # Use smart applier
    result = SmartModifier.smart_apply(target_file, new_code, skip_validation=force)
    return jsonify(result)


@self_mod_bp.route("/backups", methods=["GET"])
def list_backups():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    backups = BackupManager.list_backups()
    return jsonify({"backups": backups})


@self_mod_bp.route("/restore", methods=["POST"])
def restore_backup():
    """Restore from backup"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    backup_name = data.get("backup_name", "")
    target_path = data.get("target_path", "")

    if not backup_name or not target_path:
        return jsonify({"error": "Missing data"}), 400

    result = BackupManager.restore_backup(backup_name, target_path)
    return jsonify(result)


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

    from ai_core.self_mod.auto_upgrader import AutoUpgrader


@self_mod_bp.route("/scan", methods=["GET"])
def scan_system():
    """Scan system for issues"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    result = AutoUpgrader.scan_system()
    return jsonify(result)


@self_mod_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    """Get AI improvement suggestions"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    result = AutoUpgrader.generate_suggestions()
    return jsonify(result)


@self_mod_bp.route("/quick-wins", methods=["GET"])
def quick_wins():
    """Get quick auto-implementable fixes"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    result = AutoUpgrader.get_quick_wins()
    return jsonify(result)