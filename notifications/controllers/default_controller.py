import connexion

from flask import jsonify

from notifications.models.notification import Notification  # noqa: E501
from notifications import util
from notifications.database import Notification as DBNotification
from notifications.database import db
from notifications.tasks import deliver_notification
import pytz
from datetime import datetime



def create_notification(notification):  # noqa: E501
    """create a notification

     # noqa: E501

    :param notification: the notification to create
    :type notification: dict | bytes

    :rtype: int
    """
    if connexion.request.is_json:
        notification = Notification.from_dict(connexion.request.get_json())  # noqa: E501
        if notification.message_id is None:
            notification.message_id = -1

        email = notification.user_email
        title = notification.title
        description = notification.description
        timestamp = notification.timestamp
        message_id = notification.message_id

        new_notification = DBNotification()
        new_notification.add_notification(
            email,
            title,
            description,
            timestamp,
            False,
            False,
            1,
            message_id
        )
        db.session.add(new_notification)
        db.session.commit()

        time_aware = pytz.timezone('Europe/Rome').localize(
            datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        )

        deliver_notification.apply_async((new_notification.get_id(),), eta=time_aware)


    return new_notification.get_id(), 200




def delete_notification(message):  # noqa: E501
    """delete a notification for a retreated message

     # noqa: E501

    :param message: the message id for the notification to delete
    :type message: int

    :rtype: None
    """
    query = db.session.query(DBNotification).filter(DBNotification.message_id==message)
    if query.count()==0:
        return "Not Found", 404
    
    else:
        query.update(dict(is_deleted=True))
        db.session.commit()
        return "", 200


def get_notifications(user):  # noqa: E501
    """retrieve all (unread) user notifications

     # noqa: E501

    :param user: user&#39;s email
    :type user: str

    :rtype: List[Notification]
    """
    query_notifications = db.session.query(DBNotification).filter_by(user_email=user,is_read=False, is_deleted=False,status=2)
    notifications = [_dbnotifications2notifications(r) for r in query_notifications]
    return jsonify(notifications), 200


def notifications_count(user):  # noqa: E501
    """return the number of unread user notifications

     # noqa: E501

    :param user: user&#39;s email
    :type user: str

    :rtype: int
    """
    query_notifications = db.session.query(DBNotification).filter_by(user_email=user,is_read=False, is_deleted=False,status=2)
    notifications_count = query_notifications.count()
    return notifications_count, 200


def set_notifications_as_read(user):  # noqa: E501
    """set all user notifications as read

     # noqa: E501

    :param user: user&#39;s email
    :type user: str

    :rtype: None
    """
    db.session.query(DBNotification).filter_by(user_email=user,status=2).update(dict(is_read=True))
    db.session.commit()
    return "", 200




def _dbnotifications2notifications(data: DBNotification):
    notification = Notification()
    notification.id = data.id
    notification.user_email = data.user_email
    notification.description = data.description
    notification.title = data.title
    notification.timestamp = data.timestamp
    notification.is_read = data.is_read
    notification.is_deleted = data.is_deleted
    notification.status = data.status
    notification.message_id = data.message_id
    return notification
