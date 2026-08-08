from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from app.database import SessionLocal, Mission, Task, Memory, Notification
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/overview", methods=["GET"])
def get_overview():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        user_id = payload["user_id"]

        # Mission stats
        total_missions = db.query(Mission).filter(
            Mission.user_id == user_id
        ).count()

        completed = db.query(Mission).filter(
            Mission.user_id == user_id,
            Mission.status == "completed"
        ).count()

        running = db.query(Mission).filter(
            Mission.user_id == user_id,
            Mission.status == "running"
        ).count()

        pending = db.query(Mission).filter(
            Mission.user_id == user_id,
            Mission.status == "pending"
        ).count()

        # Task stats
        total_tasks = db.query(Task).join(Mission).filter(
            Mission.user_id == user_id
        ).count()

        completed_tasks = db.query(Task).join(Mission).filter(
            Mission.user_id == user_id,
            Task.status == "completed"
        ).count()

        # Agent usage
        agent_usage = db.query(
            Task.assigned_agent,
            func.count(Task.id).label("count")
        ).join(Mission).filter(
            Mission.user_id == user_id
        ).group_by(Task.assigned_agent).all()

        # Missions per day (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_missions = db.query(
            func.date(Mission.created_at).label("date"),
            func.count(Mission.id).label("count")
        ).filter(
            Mission.user_id == user_id,
            Mission.created_at >= seven_days_ago
        ).group_by(func.date(Mission.created_at)).all()

        # Memory stats
        total_memories = db.query(Memory).filter(
            Memory.user_id == user_id
        ).count()

        # Success rate
        success_rate = 0
        if total_missions > 0:
            success_rate = round((completed / total_missions) * 100)

        # Average tasks per mission
        avg_tasks = 0
        if total_missions > 0:
            avg_tasks = round(total_tasks / total_missions, 1)

        return jsonify({
            "missions": {
                "total": total_missions,
                "completed": completed,
                "running": running,
                "pending": pending,
                "success_rate": success_rate,
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "avg_per_mission": avg_tasks,
            },
            "agents": [
                {"name": a[0] or "Unassigned", "count": a[1]}
                for a in agent_usage
            ],
            "daily_activity": [
                {"date": str(d[0]), "count": d[1]}
                for d in daily_missions
            ],
            "memory": {
                "total_saved": total_memories,
            }
        })
    finally:
        db.close()

@analytics_bp.route("/timeline", methods=["GET"])
def get_timeline():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        user_id = payload["user_id"]

        recent_missions = db.query(Mission).filter(
            Mission.user_id == user_id
        ).order_by(Mission.created_at.desc()).limit(10).all()

        return jsonify({
            "timeline": [
                {
                    "id": m.id,
                    "title": m.title,
                    "status": m.status,
                    "progress": m.progress,
                    "created_at": str(m.created_at),
                }
                for m in recent_missions
            ]
        })
    finally:
        db.close()