from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from ai_core.gateway import call_gemini_image, call_ai_sync
import httpx
import base64

image_ai_bp = Blueprint("image_ai", __name__)


@image_ai_bp.route("/generate", methods=["POST"])
def generate_image():
    """Generate image from text prompt"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    style = data.get("style", "")

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    if style:
        prompt = f"{prompt}, {style} style"

    # Try Gemini image generation first
    result = call_gemini_image(prompt)

    if result.get("success"):
        return jsonify({
            "success": True,
            "image": f"data:{result['mime_type']};base64,{result['image_data']}",
            "prompt": prompt,
            "source": "gemini",
            "model": result.get("model", "gemini"),
        })

    # Fallback to Pollinations (free unlimited)
    try:
        pollinations_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"

        with httpx.Client(timeout=90) as client:
            response = client.get(pollinations_url)
            if response.status_code == 200:
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return jsonify({
                    "success": True,
                    "image": f"data:image/jpeg;base64,{image_base64}",
                    "prompt": prompt,
                    "source": "pollinations",
                    "model": "pollinations",
                })
    except Exception as e:
        print(f"Pollinations error: {str(e)}")

    return jsonify({"success": False, "error": "All image generators failed"})


@image_ai_bp.route("/styles", methods=["GET"])
def get_styles():
    """Get available image styles"""
    return jsonify({
        "styles": [
            {"id": "realistic", "name": "Realistic", "icon": "📷"},
            {"id": "anime", "name": "Anime", "icon": "🎌"},
            {"id": "3d", "name": "3D Render", "icon": "🎮"},
            {"id": "cartoon", "name": "Cartoon", "icon": "🎨"},
            {"id": "sketch", "name": "Sketch", "icon": "✏️"},
            {"id": "oil painting", "name": "Oil Painting", "icon": "🖼️"},
            {"id": "watercolor", "name": "Watercolor", "icon": "🎭"},
            {"id": "cyberpunk", "name": "Cyberpunk", "icon": "🌆"},
            {"id": "fantasy", "name": "Fantasy", "icon": "🐉"},
            {"id": "minimalist", "name": "Minimalist", "icon": "⚪"},
        ]
    })


@image_ai_bp.route("/enhance-prompt", methods=["POST"])
def enhance_prompt():
    """AI enhances user prompt for better images"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    system = """You are an AI image prompt enhancer.
Take user's simple prompt and make it detailed for better image generation.
Add: composition, lighting, style, colors, mood.
Keep it under 100 words.
Return ONLY the enhanced prompt, no explanations."""

    enhanced = call_ai_sync(f"Enhance this image prompt: {prompt}", system, task_type="fast")

    return jsonify({
        "success": True,
        "original": prompt,
        "enhanced": enhanced.strip() if enhanced else prompt,
    })