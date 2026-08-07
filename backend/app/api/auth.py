from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import SessionLocal, User
from app.auth.jwt_handler import create_token
import hashlib

auth_bp = Blueprint("auth", __name__)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    
    # Validation
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Name, email and password required"}), 400
    
    db = SessionLocal()
    try:
        # Check existing user
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            return jsonify({"error": "Email already exists"}), 400
        
        # Create user
        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=hash_password(data["password"])
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create token
        token = create_token(user.id, user.email, user.role)
        
        return jsonify({
            "message": "Account created successfully!",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 201
        
    finally:
        db.close()

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data["email"]).first()
        
        if not user or user.password_hash != hash_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account disabled"}), 401
        
        token = create_token(user.id, user.email, user.role)
        
        return jsonify({
            "message": "Login successful!",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        })
        
    finally:
        db.close()

@auth_bp.route("/me", methods=["GET"])
def get_me():
    from app.auth.jwt_handler import decode_token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        return jsonify({"error": "Token missing"}), 401
    
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": str(user.created_at)
        })
    finally:
        db.close()