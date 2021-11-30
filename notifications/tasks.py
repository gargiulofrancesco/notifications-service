from celery import Celery
from notifications.database import Notification
from notifications.database import db
from datetime import datetime
from sqlalchemy import and_

BACKEND = BROKER = 'redis://redis:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)
_APP = None


def do_task():
    global _APP
    if _APP is None:
        from notifications.__main__ import main
        _APP = main().app



@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    celery beat support function
    """
    # Checks for unsent and overdue messages every 5 minutes
    sender.add_periodic_task(
        300.0,
        send_unsent_past_due.s(_APP),
        name='crash recovery'
    )


@celery.task
def send_unsent_past_due(app):
    """
    task to periodically send unsent messages past due
    useful in case of catastrophic failure of celery

    :param app: the flask.current_app object, can be None
    """
    global _APP
    do_task()
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        query = db.session.query(Notification).filter(and_(
            Notification.status == 1,
            Notification.timestamp <= datetime.now().strftime('%Y-%m-%dT%H:%M'))
        )
        for row in query:
            deliver_notification(row.get_id())




@celery.task
def deliver_notification(notification_id):
    do_task()
    with _APP.app_context():
        db.session.query(Notification).filter(Notification.id==notification_id).update(dict(status=2))
        db.session.commit()

    return 0
