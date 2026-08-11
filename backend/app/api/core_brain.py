from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from ai_core.gateway import call_ai_sync, call_gemini_image
from app.helpers import with_retry, extract_json, execute_web_search
from app.tool_registry import get_active_tool, discover_tool, execute_dynamic_tool
import httpx
import re
import base64

core_brain_bp = Blueprint("core_brain", __name__)


def detect_intent(user_message: str) -> dict:
    """Brain detects user intent"""
    system_prompt = """You are NEXUS Core Brain Intent Detector.
Analyze user command in ANY language and return ONLY valid JSON:
{
  "intent": "web_search" | "generate_image" | "youtube_analyze" | "youtube_ideas" | "youtube_script" | "build_feature" | "chat" | "multi_step",
  "language": "detected language",
  "translated_to_english": "english translation",
  "extracted_data": {
    "query": "search query",
    "image_prompt": "image description",
    "url": "youtube url",
    "topic": "content topic",
    "feature_description": "feature to build"
  },
  "steps": ["step1", "step2"],
  "is_complex": true/false
}"""

    try:
        response = with_retry(call_ai_sync, user_message, system_prompt, task_type="smart")
        parsed = extract_json(response)
        if parsed:
            return parsed
    except Exception as e:
        print(f"❌ detect_intent failed: {e}")

    return {
        "intent": "chat",
        "language": "unknown",
        "translated_to_english": user_message,
        "extracted_data": {},
        "steps": ["chat"],
        "is_complex": False,
    }


def execute_image_generation(prompt: str) -> dict:
    try:
        result = call_gemini_image(prompt)

        if result.get("success"):
            return {
                "success": True,
                "type": "image_generation",
                "image": f"data:{result['mime_type']};base64,{result['image_data']}",
                "prompt": prompt,
                "source": "gemini",
            }

        pollinations_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"

        with httpx.Client(timeout=90) as client:
            response = with_retry(client.get, pollinations_url, retries=1)
            if response.status_code == 200:
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return {
                    "success": True,
                    "type": "image_generation",
                    "image": f"data:image/jpeg;base64,{image_base64}",
                    "prompt": prompt,
                    "source": "pollinations",
                }

        return {"success": False, "error": "Both image sources failed", "type": "image_generation"}
    except Exception as e:
        return {"success": False, "error": str(e), "type": "image_generation"}


def execute_youtube_analysis(url: str) -> dict:
    try:
        patterns = [r'(?:v=|\/)([0-9A-Za-z_-]{11})', r'youtu\.be\/([0-9A-Za-z_-]{11})']
        video_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break

        if not video_id:
            return {"success": False, "error": "Invalid YouTube URL", "type": "youtube_analysis"}

        with httpx.Client(timeout=15) as client:
            response = with_retry(
                client.get,
                f"https://www.youtube.com/oembed?url=https://youtube.com/watch?v={video_id}&format=json"
            )

            if response.status_code == 200:
                info = response.json()
                analysis_prompt = f"Video: {info.get('title')}\nChannel: {info.get('author_name')}\n\nAnalyze briefly."
                analysis = call_ai_sync(analysis_prompt, "You are a YouTube analyzer.", task_type="fast")

                return {
                    "success": True,
                    "type": "youtube_analysis",
                    "title": info.get("title"),
                    "author": info.get("author_name"),
                    "thumbnail": info.get("thumbnail_url"),
                    "video_id": video_id,
                    "analysis": analysis,
                }

            return {"success": False, "error": f"YouTube returned {response.status_code}", "type": "youtube_analysis"}
    except Exception as e:
        return {"success": False, "error": str(e), "type": "youtube_analysis"}


def execute_content_generation(topic: str, content_type: str = "ideas") -> dict:
    try:
        if content_type == "ideas":
            system = 'Generate 5 creative content ideas. Return JSON: {"ideas": [{"title": "...", "description": "..."}]}'
            prompt = f"Generate 5 content ideas about: {topic}"
        else:
            system = "Write engaging content."
            prompt = f"Write about: {topic}"

        response = with_retry(call_ai_sync, prompt, system, task_type="smart")

        if content_type == "ideas":
            data = extract_json(response)
            if data:
                return {
                    "success": True,
                    "type": "content_ideas",
                    "topic": topic,
                    "ideas": data.get("ideas", []),
                }

        return {
            "success": True,
            "type": "content" if content_type != "ideas" else "content_ideas",
            "topic": topic,
            "content": response,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "type": "content_generation"}


def execute_build_feature(description: str) -> dict:
    try:
        system = 'You are a feature planner. Return JSON: {"feature": "...", "steps": ["..."], "apis_needed": ["..."]}'
        response = with_retry(call_ai_sync, description, system, task_type="smart")
        data = extract_json(response)

        if data:
            return {
                "success": True,
                "type": "build_feature",
                "feature": data.get("feature", description),
                "steps": data.get("steps", []),
                "apis_needed": data.get("apis_needed", []),
            }

        return {
            "success": True,
            "type": "build_feature",
            "feature": description,
            "plan": response,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "type": "build_feature"}


def execute_chat(message: str) -> dict:
    try:
        response = with_retry(
            call_ai_sync,
            message,
            "You are NEXUS AI. Reply in user's language. Be concise.",
            task_type="fast"
        )
        return {"success": True, "type": "chat", "response": response}
    except Exception as e:
        return {"success": False, "error": str(e), "type": "chat"}


def run_step(step: str, extracted: dict, user_message: str) -> dict:
    if step == "web_search":
        return execute_web_search(extracted.get("query", user_message))
    if step == "generate_image":
        return execute_image_generation(extracted.get("image_prompt", user_message))
    if step == "youtube_analyze":
        return execute_youtube_analysis(extracted.get("url", user_message))
    if step == "youtube_ideas":
        return execute_content_generation(extracted.get("topic", user_message), "ideas")
    if step == "youtube_script":
        return execute_content_generation(extracted.get("topic", user_message), "script")
    if step == "build_feature":
        return execute_build_feature(extracted.get("feature_description", user_message))
    if step == "chat":
        return execute_chat(user_message)

    # Unknown step - try tool discovery
    active_tool = get_active_tool(step)
    if active_tool:
        return execute_dynamic_tool(active_tool)

    discovery = discover_tool(step)
    return discovery


@core_brain_bp.route("/process", methods=["POST"])
def process_command():
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({"error": "Message required"}), 400

        print(f"\n🧠 CORE BRAIN: {user_message}")

        intent_data = detect_intent(user_message)
        print(f"📋 Intent: {intent_data.get('intent')}")
        print(f"🌍 Language: {intent_data.get('language')}")

        results = {
            "success": True,
            "user_message": user_message,
            "intent": intent_data.get("intent"),
            "language": intent_data.get("language"),
            "translated": intent_data.get("translated_to_english"),
            "steps_executed": [],
            "results": [],
        }

        intent = intent_data.get("intent", "chat")
        extracted = intent_data.get("extracted_data", {}) or {}

        if intent == "multi_step":
            steps = intent_data.get("steps") or ["chat"]
            for step in steps:
                result = run_step(step, extracted, user_message)
                results["results"].append(result)
                results["steps_executed"].append(step)
        else:
            result = run_step(intent, extracted, user_message)
            results["results"].append(result)
            results["steps_executed"].append(intent)

        print(f"✅ Executed: {results['steps_executed']}")
        return jsonify(results)

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "success": False,
            "error": "Processing failed",
            "details": str(e),
        }), 500


@core_brain_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    return jsonify({
        "capabilities": [
            {"icon": "🔍", "name": "Web Search", "example": "Search AI news"},
            {"icon": "🎨", "name": "Image Generation", "example": "Create sunset image"},
            {"icon": "🎬", "name": "YouTube Analysis", "example": "Analyze [YouTube URL]"},
            {"icon": "💡", "name": "Content Ideas", "example": "5 video ideas about cooking"},
            {"icon": "📝", "name": "Script Writing", "example": "Write script about AI"},
            {"icon": "🛠️", "name": "Build Feature", "example": "Build a weather page"},
            {"icon": "💬", "name": "Multi-language Chat", "example": "Any language conversation"},
            {"icon": "⚡", "name": "Multi-step Tasks", "example": "Search AND create image"},
        ]
    })