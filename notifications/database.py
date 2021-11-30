import json

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.Unicode(128), nullable=False)
    title = db.Column(db.Unicode(256), nullable=False)
    description = db.Column(db.Unicode(1024), nullable=False)
    timestamp = db.Column(db.Unicode(128), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer, nullable=False)
    message_id = db.Column(db.Integer, nullable=False)

    def __init__(self, *args, **kw):
        super(Notification, self).__init__(*args, **kw)

    def add_notification(self, user_email, title, description,
                         timestamp, is_read, is_deleted, status, message_id):
        self.user_email = user_email
        self.title = title
        self.description = description
        self.timestamp = timestamp
        self.is_read = is_read
        self.is_deleted = is_deleted  
        self.status = status    # 1 if created, 2 if delivered
        self.message_id = message_id

    def get_id(self):
        return self.id
