import logging
import os

import connexion
from flask_testing import TestCase

from notifications.encoder import JSONEncoder
from notifications.database import db


class BaseTestCase(TestCase):

    def create_app(self):
        self._cleanup()
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = JSONEncoder
        app.add_api('swagger.yaml')
        app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./T_notifications.db'
        db.init_app(app.app)
        db.create_all(app=app.app)
        return app.app


    @staticmethod
    def _cleanup():
        if os.path.exists('./T_notifications.db'):
            os.remove('./T_notifications.db')
        if os.path.exists('./notifications/test/T_notifications.db'):
            os.remove('./notifications/test/T_notifications.db')
