from notifications.database import db
from notifications.database import Notification as DBNotification


def create_notification(email, title, description, timestamp, message_id, is_read, is_deleted, status):

    notification = DBNotification()
    notification.user_email = email
    notification.title = title
    notification.description = description
    notification.timestamp = timestamp
    notification.message_id = message_id
    notification.is_read = is_read
    notification.is_deleted = is_deleted
    notification.status = status
    db.session.add(notification)
    db.session.commit()

def get_notifications_by_message_id(message_id):
    notifications = db.session.query(DBNotification).filter(DBNotification.message_id==message_id)
    return notifications

def get_notification_by_id(id):
    notification = db.session.query(DBNotification).filter(DBNotification.id==id)
    return notification