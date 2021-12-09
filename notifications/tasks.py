from celery import Celery
from celery.schedules import crontab
from notifications.database import Notification
from notifications.database import db
from datetime import datetime
from sqlalchemy import and_
import requests
import os


if os.environ.get('DOCKER') is not None:
    BACKEND = BROKER = 'redis://redis:6379/0' # pragma: no cover
else:
    BACKEND = BROKER = 'redis://localhost:6379/0'

celery = Celery(__name__, backend=BACKEND, broker=BROKER)
_APP = None
LOTTERY_PRIZE = 100

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
    # Runs the lottery every lottery period
    sender.add_periodic_task(
        crontab(hour=16, minute=41, day_of_month=8),
        lottery_task.s(_APP),
        name='lottery task'
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


@celery.task
def lottery_task(app):
    """
    Runs the lottery
    :param app: the flask.current_app object, can be None
    """
    do_task()
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        try:
            url = "http://users_ms_worker:5001/lottery" 
            response = requests.get(url)
            winner_id = response.json()
            url = "http://users_ms_worker:5001/users/by_id/"+str(winner_id)
            response = requests.get(url)

            winner_email = response.json()['email']
            description = "Congratulations! You won " + str(LOTTERY_PRIZE) +" points"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_notification = Notification()
            new_notification.add_notification(
                winner_email,
                "Lottery Win",
                description,
                timestamp,
                False,
                False,
                2,
                -1
            )
            db.session.add(new_notification)
            db.session.commit()
        except Exception:
            return
