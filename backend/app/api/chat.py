from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from app.database import SessionLocal, Mission, Task
from ai_core.gateway import call_ai_sync
from ai_core.planner.task_creator import create_tasks_for_mission
from ai_core.memory.memory_manager import MemoryManager
import traceback

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/message", methods=["POST"])
def send_message():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    user_id = payload["user_id"]

    # Get last context from memory
    last_context = MemoryManager.get_last_project_context(user_id)
    context_text = ""

    if last_context and last_context.get("parsed_content"):
        pc = last_context["parsed_content"]
        if isinstance(pc, dict):
            context_text = f"""
Previous Project Context:
- Title: {pc.get('mission_title', 'N/A')}
- Goal: {pc.get('goal', 'N/A')}
"""

    # Determine intent
    system_prompt = """You are NEXUS AI OS — an intelligent AI operating system.

Your job is to understand user messages and respond in JSON format.

Rules:
1. If user wants to create/build/make/develop/plan something → intent: "create_mission"
2. If user is asking a question → intent: "answer"
3. If user wants to continue previous work → intent: "continue"
4. Always respond with valid JSON only

Response format:
{
  "intent": "create_mission" | "answer" | "continue",
  "mission_title": "title here (only for create_mission)",
  "mission_goal": "detailed goal (only for create_mission)",
  "response": "your message to user"
}"""

    prompt = f"""User message: {message}

{context_text}

Analyze the intent and respond in JSON format."""

    try:
        ai_response = call_ai_sync(prompt, system_prompt)

        import json
        import re

        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)

        if json_match:
            parsed = json.loads(json_match.group())
            intent = parsed.get("intent", "answer")

            if intent == "create_mission":
                # Auto create mission
                db = SessionLocal()
                try:
                    goal = parsed.get("mission_goal", message)
                    title = parsed.get("mission_title", message[:50])

                    mission = Mission(
                        user_id=user_id,
                        title=title,
                        goal=goal,
                        status="pending"
                    )
                    db.add(mission)
                    db.commit()
                    db.refresh(mission)

                    # AI tasks
                    try:
                        ai_tasks = create_tasks_for_mission(goal)
                    except Exception:
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
                        "intent": "create_mission",
                        "response": parsed.get("response", f"Mission '{title}' has been created with {len(ai_tasks)} tasks. You can now execute it from the Missions page."),
                        "mission": {
                            "id": mission.id,
                            "title": mission.title,
                            "goal": mission.goal,
                            "status": mission.status,
                            "tasks_count": len(ai_tasks)
                        }
                    })

                finally:
                    db.close()

            elif intent == "continue":
                if last_context and last_context.get("parsed_content"):
                    pc = last_context["parsed_content"]
                    return jsonify({
                        "intent": "continue",
                        "response": f"I found your previous project: '{pc.get('mission_title', 'Unknown')}'. Goal was: {pc.get('goal', 'N/A')[:100]}. Would you like me to create a new mission to continue this work?",
                        "last_context": last_context["parsed_content"]
                    })
                else:
                    return jsonify({
                        "intent": "answer",
                        "response": "I don't have any previous project context saved. Please create a new mission."
                    })

            else:
                return jsonify({
                    "intent": "answer",
                    "response": parsed.get("response", ai_response)
                })

        else:
            return jsonify({
                "intent": "answer",
                "response": ai_response
            })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "intent": "answer",
            "response": f"I understood your request: '{message}'. How can I help you further?"
        })