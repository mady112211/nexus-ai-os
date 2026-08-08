from app.database import SessionLocal, Notification

class NotificationManager:
    """Manages user notifications"""

    @staticmethod
    def create(user_id: int, title: str, message: str = "",
               notification_type: str = "info", icon: str = "🔔",
               action_url: str = None):
        """Create a new notification"""
        db = SessionLocal()
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                icon=icon,
                action_url=action_url,
                is_read=False,
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            print(f"🔔 Notification: {title}")
            return notification.id
        finally:
            db.close()

    @staticmethod
    def get_all(user_id: int, limit: int = 50, unread_only: bool = False):
        """Get user's notifications"""
        db = SessionLocal()
        try:
            query = db.query(Notification).filter(
                Notification.user_id == user_id
            )
            if unread_only:
                query = query.filter(Notification.is_read == False)

            notifications = query.order_by(
                Notification.created_at.desc()
            ).limit(limit).all()

            return [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "type": n.notification_type,
                    "icon": n.icon,
                    "is_read": n.is_read,
                    "action_url": n.action_url,
                    "created_at": str(n.created_at),
                }
                for n in notifications
            ]
        finally:
            db.close()

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications"""
        db = SessionLocal()
        try:
            return db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).count()
        finally:
            db.close()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int):
        """Mark notification as read"""
        db = SessionLocal()
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()

            if notification:
                notification.is_read = True
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def mark_all_read(user_id: int):
        """Mark all notifications as read"""
        db = SessionLocal()
        try:
            db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).update({"is_read": True})
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def delete(notification_id: int, user_id: int):
        """Delete a notification"""
        db = SessionLocal()
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()

            if notification:
                db.delete(notification)
                db.commit()
                return True
            return False
        finally:
            db.close()