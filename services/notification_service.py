from models import db
from models.notification import Notification

def notify_user(user_id, title, message, link=None):
    """
    Creates an in-app notification for a given user.
    """
    if not user_id:
        return None
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            link=link
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None
