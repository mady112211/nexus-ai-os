from flask import Blueprint, jsonify, request
from app.database import SessionLocal, Mission, Task
from app.auth.jwt_handler import decode_token
from ai_core.planner.task_creator import create_tasks_for_mission
import traceback
import threading

missions_bp = Blueprint("missions", __name__)

@missions_bp.route("/", methods=["GET"])
def get_missions():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        missions = db.query(Mission).filter(
            Mission.user_id == payload["user_id"]
        ).order_by(Mission.created_at.desc()).all()

        return jsonify({
            "missions": [{
                "id": m.id,
                "title": m.title,
                "goal": m.goal,
                "status": m.status,
                "progress": m.progress,
                "created_at": str(m.created_at)
            } for m in missions]
        })
    finally:
        db.close()

@missions_bp.route("/", methods=["POST"])
def create_mission():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data.get("goal"):
        return jsonify({"error": "Goal is required"}), 400

    db = SessionLocal()
    try:
        mission = Mission(
            user_id=payload["user_id"],
            title=data.get("title", data["goal"][:50]),
            goal=data["goal"],
            status="pending"
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)

        print(f"🧠 AI Planning for: {data['goal'][:50]}")
        print(f"🔄 Calling create_tasks_for_mission...")

        try:
            ai_tasks = create_tasks_for_mission(data["goal"])
            print(f"✅ {len(ai_tasks)} tasks created by AI")
        except Exception as e:
            print(f"❌ AI Planner Error: {str(e)}")
            traceback.print_exc()
            ai_tasks = [
                {"task_name": "Goal Analysis", "description": "Analyze goal", "assigned_agent": "Research Agent", "order_index": 0},
                {"task_name": "Research", "description": "Research phase", "assigned_agent": "Research Agent", "order_index": 1},
                {"task_name": "Strategy", "description": "Strategy phase", "assigned_agent": "Content Agent", "order_index": 2},
                {"task_name": "Implementation", "description": "Implementation", "assigned_agent": "Developer Agent", "order_index": 3},
                {"task_name": "Final Report", "description": "Final report", "assigned_agent": "Research Agent", "order_index": 4},
            ]

        for task_data in ai_tasks:
            task = Task(
                mission_id=mission.id,
                task_name=task_data.get("task_name", "Task"),
                description=task_data.get("description", ""),
                assigned_agent=task_data.get("assigned_agent", "Research Agent"),
                status="pending",
                order_index=task_data.get("order_index", 0)
            )
            db.add(task)

        db.commit()

        return jsonify({
            "message": "Mission created!",
            "mission": {
                "id": mission.id,
                "title": mission.title,
                "goal": mission.goal,
                "status": mission.status,
                "tasks_created": len(ai_tasks),
                "ai_powered": True
            }
        }), 201

    finally:
        db.close()

@missions_bp.route("/<int:mission_id>", methods=["GET"])
def get_mission(mission_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(
            Mission.id == mission_id,
            Mission.user_id == payload["user_id"]
        ).first()

        if not mission:
            return jsonify({"error": "Mission not found"}), 404

        tasks = db.query(Task).filter(
            Task.mission_id == mission_id
        ).order_by(Task.order_index).all()

        return jsonify({
            "id": mission.id,
            "title": mission.title,
            "goal": mission.goal,
            "status": mission.status,
            "progress": mission.progress,
            "result": mission.result,
            "created_at": str(mission.created_at),
            "tasks": [{
                "id": t.id,
                "task_name": t.task_name,
                "description": t.description,
                "assigned_agent": t.assigned_agent,
                "status": t.status,
                "result": t.result
            } for t in tasks]
        })
    finally:
        db.close()

@missions_bp.route("/<int:mission_id>/execute", methods=["POST"])
def execute_mission(mission_id):
    """Start executing a mission"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(
            Mission.id == mission_id,
            Mission.user_id == payload["user_id"]
        ).first()

        if not mission:
            return jsonify({"error": "Mission not found"}), 404

        if mission.status == "running":
            return jsonify({"error": "Mission already running"}), 400

        if mission.status == "completed":
            return jsonify({"error": "Mission already completed"}), 400

    finally:
        db.close()

    # Run in background thread
    def run_mission():
        from ai_core.workflow.engine import WorkflowEngine
        engine = WorkflowEngine(mission_id)
        engine.start()

    thread = threading.Thread(target=run_mission)
    thread.start()

    return jsonify({
        "message": "Mission execution started!",
        "mission_id": mission_id,
        "status": "running"
    })