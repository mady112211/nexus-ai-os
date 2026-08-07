from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from ai_core.memory.memory_manager import MemoryManager

memory_bp = Blueprint("memory", __name__)

@memory_bp.route("/", methods=["GET"])
def get_memories():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    memory_type = request.args.get("type")
    memories = MemoryManager.get_memories(
        user_id=payload["user_id"],
        memory_type=memory_type,
        limit=100,
    )

    return jsonify({"memories": memories})

@memory_bp.route("/", methods=["POST"])
def create_memory():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data.get("memory_type") or not data.get("content"):
        return jsonify({"error": "memory_type and content are required"}), 400

    memory_id = MemoryManager.save_memory(
        user_id=payload["user_id"],
        memory_type=data["memory_type"],
        content=data["content"],
        importance=data.get("importance", 5),
    )

    return jsonify({
        "message": "Memory saved successfully",
        "memory_id": memory_id
    }), 201

@memory_bp.route("/preferences", methods=["POST"])
def save_preference():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data.get("title") or not data.get("value"):
        return jsonify({"error": "title and value are required"}), 400

    memory_id = MemoryManager.save_preference(
        user_id=payload["user_id"],
        title=data["title"],
        value=data["value"],
    )

    return jsonify({
        "message": "Preference saved successfully",
        "memory_id": memory_id
    }), 201

@memory_bp.route("/context/last", methods=["GET"])
def get_last_context():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    context = MemoryManager.get_last_project_context(payload["user_id"])

    return jsonify({
        "last_project_context": context
    })

@memory_bp.route("/search", methods=["GET"])
def search_memories():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    keyword = request.args.get("q", "").strip()

    if not keyword:
        return jsonify({"error": "Search keyword is required"}), 400

    results = MemoryManager.search_memories(payload["user_id"], keyword)

    return jsonify({
        "results": results
    })