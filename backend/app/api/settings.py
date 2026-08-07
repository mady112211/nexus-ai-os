from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from app.database import SessionLocal, User
from ai_core.memory.memory_manager import MemoryManager

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/profile", methods=["GET"])
def get_profile():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload["user_id"]).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": str(user.created_at),
        })
    finally:
        db.close()

@settings_bp.route("/profile", methods=["PUT"])
def update_profile():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == payload["user_id"]).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if data.get("name"):
            user.name = data["name"]

        db.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
        })
    finally:
        db.close()

@settings_bp.route("/ai", methods=["GET"])
def get_ai_settings():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    import os
    return jsonify({
        "default_model": os.getenv("DEFAULT_MODEL", "google/gemma-4-26b-a4b-it:free"),
        "provider": "openrouter",
        "free_models": [
            "google/gemma-4-26b-a4b-it:free",
            "google/gemma-4-31b-it:free",
            "inclusionai/ling-3.0-tiny:free",
            "poolside/laguna-s-2.1:free",
        ],
        "api_key_set": bool(os.getenv("OPENROUTER_API_KEY")),
    })

@settings_bp.route("/ai", methods=["PUT"])
def update_ai_settings():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    # Save as user preference in memory
    if data.get("default_model"):
        MemoryManager.save_preference(
            user_id=payload["user_id"],
            title="preferred_ai_model",
            value=data["default_model"]
        )

    if data.get("response_style"):
        MemoryManager.save_preference(
            user_id=payload["user_id"],
            title="response_style",
            value=data["response_style"]
        )

    return jsonify({
        "message": "AI settings saved successfully"
    })

@settings_bp.route("/stats", methods=["GET"])
def get_stats():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    from app.database import Mission, Task, Memory
    db = SessionLocal()

    try:
        user_id = payload["user_id"]

        total_missions = db.query(Mission).filter(
            Mission.user_id == user_id
        ).count()

        completed_missions = db.query(Mission).filter(
            Mission.user_id == user_id,
            Mission.status == "completed"
        ).count()

        total_tasks = db.query(Task).join(Mission).filter(
            Mission.user_id == user_id
        ).count()

        total_memories = db.query(Memory).filter(
            Memory.user_id == user_id
        ).count()

        return jsonify({
            "total_missions": total_missions,
            "completed_missions": completed_missions,
            "total_tasks": total_tasks,
            "total_memories": total_memories,
            "success_rate": round(
                (completed_missions / total_missions * 100) if total_missions > 0 else 0
            )
        })
    finally:
        db.close()