from flask import Blueprint, jsonify, request
from app.database import SessionLocal, Mission, Task, Agent
from app.auth.jwt_handler import decode_token

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET"])
def get_dashboard():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    
    db = SessionLocal()
    try:
        user_id = payload["user_id"]
        
        # Stats
        total_missions = db.query(Mission).filter(
            Mission.user_id == user_id
        ).count()
        
        active_missions = db.query(Mission).filter(
            Mission.user_id == user_id,
            Mission.status == "running"
        ).count()
        
        completed_missions = db.query(Mission).filter(
            Mission.user_id == user_id,
            Mission.status == "completed"
        ).count()
        
        total_tasks = db.query(Task).join(Mission).filter(
            Mission.user_id == user_id
        ).count()
        
        active_agents = db.query(Agent).filter(
            Agent.is_active == True
        ).count()
        
        # Recent missions
        recent = db.query(Mission).filter(
            Mission.user_id == user_id
        ).order_by(Mission.created_at.desc()).limit(5).all()
        
        recent_missions = [{
            "id": m.id,
            "title": m.title,
            "status": m.status,
            "progress": m.progress,
            "created_at": str(m.created_at)
        } for m in recent]
        
        return jsonify({
            "stats": {
                "total_missions": total_missions,
                "active_missions": active_missions,
                "completed_missions": completed_missions,
                "total_tasks": total_tasks,
                "active_agents": active_agents
            },
            "recent_missions": recent_missions,
            "system": {
                "name": "NEXUS AI OS",
                "version": "0.1.0",
                "status": "operational"
            }
        })
    finally:
        db.close()