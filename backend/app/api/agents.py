from flask import Blueprint, jsonify, request
from app.database import SessionLocal, Agent
from app.auth.jwt_handler import decode_token

agents_bp = Blueprint("agents", __name__)

@agents_bp.route("/", methods=["GET"])
def get_agents():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    
    db = SessionLocal()
    try:
        agents = db.query(Agent).all()
        return jsonify({
            "agents": [{
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "description": a.description,
                "is_active": a.is_active,
                "status": "ready" if a.is_active else "offline"
            } for a in agents]
        })
    finally:
        db.close()

@agents_bp.route("/<int:agent_id>", methods=["GET"])
def get_agent(agent_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        
        return jsonify({
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description,
            "is_active": agent.is_active
        })
    finally:
        db.close()