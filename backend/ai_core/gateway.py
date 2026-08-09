import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

FREE_MODELS = [
    # Top tier - Best quality
    "openrouter/free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai/gpt-oss-20b:free",
    
    # Middle tier - Good quality
    "nvidia/nemotron-3-super-120b-a12b:free",
    "cohere/north-mini-code:free",
    
    # Reliable fallback - Fast
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    
    # Last resort
    "inclusionai/ling-3.0-tiny:free",
]

def call_ai_sync(prompt: str, system: str = "") -> str:
    """Synchronous AI call — works inside Flask"""
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-actual-key-here":
        print("❌ OPENROUTER_API_KEY missing")
        return _fallback_response(prompt)

    for model_name in FREE_MODELS:
        try:
            print(f"🤖 Trying model: {model_name}")

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
                            {
                                "role": "system",
                                "content": system or "You are NEXUS AI OS, an intelligent AI operating system."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 4000,
                        "temperature": 0.3,
                    }
                )

                print(f"📡 Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    print(f"✅ AI response from: {model_name}")
                    return content
                else:
                    print(f"❌ Error: {response.text[:150]}")

        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)[:80]}")
            continue

    print("⚠️ All models failed, using fallback")
    return _fallback_response(prompt)

async def call_ai(prompt: str, system: str = "", model: str = None) -> str:
    """Async version"""
    return call_ai_sync(prompt, system)

def _fallback_response(prompt: str) -> str:
    return f"AI analysis for: {prompt[:100]}... (AI service not configured)"