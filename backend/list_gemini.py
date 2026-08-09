import httpx
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

r = httpx.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    params={"key": key}
)

if r.status_code == 200:
    data = r.json()
    print("AVAILABLE GEMINI MODELS:")
    print("=" * 70)
    for model in data.get("models", []):
        name = model.get("name", "").replace("models/", "")
        methods = model.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            print(f"✅ {name}")
else:
    print(f"Error: {r.status_code}")
    print(r.text)