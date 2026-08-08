from flask import Blueprint, jsonify, request
from app.auth.jwt_handler import decode_token
from ai_core.notifications import NotificationManager

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("/", methods=["GET"])
def get_notifications():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    unread_only = request.args.get("unread_only", "false").lower() == "true"

    notifications = NotificationManager.get_all(
        payload["user_id"],
        unread_only=unread_only
    )

    unread_count = NotificationManager.get_unread_count(payload["user_id"])

    return jsonify({
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications)
    })

@notifications_bp.route("/unread-count", methods=["GET"])
def unread_count():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    count = NotificationManager.get_unread_count(payload["user_id"])
    return jsonify({"unread_count": count})

@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
def mark_read(notification_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    success = NotificationManager.mark_as_read(
        notification_id,
        payload["user_id"]
    )

    if not success:
        return jsonify({"error": "Notification not found"}), 404

    return jsonify({"message": "Marked as read"})

@notifications_bp.route("/mark-all-read", methods=["POST"])
def mark_all_read():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    NotificationManager.mark_all_read(payload["user_id"])
    return jsonify({"message": "All notifications marked as read"})

@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    success = NotificationManager.delete(notification_id, payload["user_id"])

    if not success:
        return jsonify({"error": "Notification not found"}), 404

    return jsonify({"message": "Notification deleted"})