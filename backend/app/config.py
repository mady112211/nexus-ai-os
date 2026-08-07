import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App
    APP_NAME = "NEXUS AI OS"
    VERSION = "0.1.0"
    DEBUG = True
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "nexus-secret-key-2024")
    JWT_SECRET = os.getenv("JWT_SECRET", "nexus-jwt-secret-2024")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nexus.db")
    
    # AI
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo")
    
    # CORS
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:5000"]

config = Config()