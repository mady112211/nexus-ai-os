import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os

JWT_SECRET = os.getenv("JWT_SECRET", "nexus-jwt-secret-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

def create_token(user_id: int, email: str, role: str = "user"):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        request.user_id = payload["user_id"]
        request.user_email = payload["email"]
        request.user_role = payload["role"]
        
        return f(*args, **kwargs)
    return decorated