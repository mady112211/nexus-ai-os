import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Smart model selection based on task
GEMINI_MODELS = {
    "fast": "gemini-3.5-flash",
    "smart": "gemini-3-pro-preview",
    "code": "gemini-3.5-flash",
    "vision": "gemini-3.5-flash",
    "research": "gemini-3-pro-preview",
    "image": "gemini-3.1-flash-image",
}

FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]

FREE_MODELS_OPENROUTER = [
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
]


def call_gemini(prompt: str, system: str = "", task_type: str = "fast", image_data: str = None) -> str:
    """Smart Gemini call with task-based model selection"""

    if not GEMINI_API_KEY:
        return None

    # Choose best model for task
    primary_model = GEMINI_MODELS.get(task_type, "gemini-3.5-flash")
    models_to_try = [primary_model] + [m for m in FALLBACK_MODELS if m != primary_model]

    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    for model_name in models_to_try:
        try:
            print(f"🌟 Gemini [{task_type}]: {model_name}")

            # Build parts (text + optional image)
            parts = [{"text": full_prompt}]
            if image_data:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                })

            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{GEMINI_BASE_URL}/{model_name}:generateContent",
                    params={"key": GEMINI_API_KEY},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": parts
                        }],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 8000,
                        }
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"✅ Response from: {model_name}")
                    return content
                else:
                    print(f"❌ {model_name}: {response.status_code}")

        except Exception as e:
            print(f"❌ Error {model_name}: {str(e)[:80]}")
            continue

    return None


def call_gemini_image(prompt: str) -> dict:
    """Generate image using Gemini Image models"""

    if not GEMINI_API_KEY:
        return {"success": False, "error": "No API key"}

    image_models = [
        "gemini-3.1-flash-image",
        "gemini-3-pro-image",
        "gemini-2.5-flash-image",
    ]

    for model_name in image_models:
        try:
            print(f"🎨 Generating image with: {model_name}")

            with httpx.Client(timeout=90) as client:
                response = client.post(
                    f"{GEMINI_BASE_URL}/{model_name}:generateContent",
                    params={"key": GEMINI_API_KEY},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "responseModalities": ["Image"],
                        }
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    parts = data["candidates"][0]["content"]["parts"]
                    for part in parts:
                        if "inline_data" in part or "inlineData" in part:
                            image_data = part.get("inline_data", part.get("inlineData", {}))
                            return {
                                "success": True,
                                "image_data": image_data.get("data"),
                                "mime_type": image_data.get("mime_type", "image/png"),
                                "model": model_name,
                            }
                else:
                    print(f"❌ {model_name}: {response.status_code}")

        except Exception as e:
            print(f"❌ Error: {str(e)[:80]}")
            continue

    return {"success": False, "error": "All image models failed"}


def call_openrouter(prompt: str, system: str = "") -> str:
    """OpenRouter fallback"""

    if not OPENROUTER_API_KEY:
        return None

    for model_name in FREE_MODELS_OPENROUTER:
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "NEXUS AI OS",
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system or "You are NEXUS AI OS."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 4000,
                        "temperature": 0.3,
                    }
                )

                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]

        except Exception:
            continue

    return None


def call_ai_sync(prompt: str, system: str = "", task_type: str = "fast") -> str:
    """Smart AI call - Gemini first with task type, OpenRouter fallback"""

    result = call_gemini(prompt, system, task_type=task_type)
    if result:
        return result

    print("⚠️ Gemini unavailable, trying OpenRouter...")
    result = call_openrouter(prompt, system)
    if result:
        return result

    return _fallback_response(prompt)


async def call_ai(prompt: str, system: str = "", model: str = None) -> str:
    return call_ai_sync(prompt, system)


def _fallback_response(prompt: str) -> str:
    return f"AI analysis for: {prompt[:100]}... (AI service unavailable)"