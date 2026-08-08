from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from app.database import SessionLocal, Workspace, WorkspaceMember, Invitation, User, Mission

workspaces_bp = Blueprint("workspaces", __name__)


@workspaces_bp.route("/", methods=["GET"])
def get_workspaces():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        user_id = payload["user_id"]

        owned = db.query(Workspace).filter(Workspace.owner_id == user_id).all()
        member_ws = db.query(Workspace).join(WorkspaceMember).filter(
            WorkspaceMember.user_id == user_id
        ).all()

        all_ws = list({w.id: w for w in owned + member_ws}.values())

        return jsonify({
            "workspaces": [
                {
                    "id": w.id,
                    "name": w.name,
                    "description": w.description,
                    "icon": w.icon,
                    "is_owner": w.owner_id == user_id,
                    "created_at": str(w.created_at),
                }
                for w in all_ws
            ]
        })
    finally:
        db.close()


@workspaces_bp.route("/", methods=["POST"])
def create_workspace():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    db = SessionLocal()
    try:
        workspace = Workspace(
            name=data["name"],
            description=data.get("description", ""),
            owner_id=payload["user_id"],
            icon=data.get("icon", "🏢"),
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=payload["user_id"],
            role="admin"
        )
        db.add(member)
        db.commit()

        return jsonify({
            "message": "Workspace created!",
            "workspace": {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "icon": workspace.icon,
            }
        }), 201
    finally:
        db.close()


@workspaces_bp.route("/<int:workspace_id>", methods=["GET"])
def get_workspace(workspace_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        members = db.query(WorkspaceMember, User).join(
            User, WorkspaceMember.user_id == User.id
        ).filter(WorkspaceMember.workspace_id == workspace_id).all()

        missions_count = db.query(Mission).filter(
            Mission.workspace_id == workspace_id
        ).count()

        return jsonify({
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "icon": workspace.icon,
            "is_owner": workspace.owner_id == payload["user_id"],
            "missions_count": missions_count,
            "members": [
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "role": m.role,
                    "joined_at": str(m.joined_at),
                }
                for m, u in members
            ]
        })
    finally:
        db.close()


@workspaces_bp.route("/<int:workspace_id>/invite", methods=["POST"])
def invite_member(workspace_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    db = SessionLocal()
    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        # Check if user exists
        user = db.query(User).filter(User.email == data["email"]).first()

        if user:
            # Add directly as member
            existing = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id
            ).first()

            if existing:
                return jsonify({"error": "User already a member"}), 400

            member = WorkspaceMember(
                workspace_id=workspace_id,
                user_id=user.id,
                role=data.get("role", "member")
            )
            db.add(member)
            db.commit()

            return jsonify({
                "message": f"{user.name} added to workspace!",
                "added": True
            })
        else:
            # Create invitation
            invitation = Invitation(
                workspace_id=workspace_id,
                email=data["email"],
                role=data.get("role", "member"),
                invited_by=payload["user_id"]
            )
            db.add(invitation)
            db.commit()

            return jsonify({
                "message": f"Invitation sent to {data['email']}",
                "added": False
            })
    finally:
        db.close()


@workspaces_bp.route("/<int:workspace_id>/members/<int:user_id>", methods=["DELETE"])
def remove_member(workspace_id, user_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace or workspace.owner_id != payload["user_id"]:
            return jsonify({"error": "Not authorized"}), 403

        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        ).first()

        if member:
            db.delete(member)
            db.commit()
            return jsonify({"message": "Member removed"})

        return jsonify({"error": "Member not found"}), 404
    finally:
        db.close()


@workspaces_bp.route("/<int:workspace_id>", methods=["DELETE"])
def delete_workspace(workspace_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()
    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            return jsonify({"error": "Not found"}), 404
        if workspace.owner_id != payload["user_id"]:
            return jsonify({"error": "Only owner can delete"}), 403

        db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id
        ).delete()

        db.delete(workspace)
        db.commit()

        return jsonify({"message": "Workspace deleted"})
    finally:
        db.close()