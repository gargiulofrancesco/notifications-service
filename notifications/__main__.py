#!/usr/bin/env python3

import connexion

from notifications import encoder
from notifications.database import db


_APP = None


def main():
    global _APP
    app = connexion.App(__name__, specification_dir='./swagger/')
    _APP = app.app
    _APP.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Notifications'})
    _APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../notifications.db'
    _APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(_APP)
    db.create_all(app=_APP)
    return app


if __name__ == '__main__':
    app = main()
    app.run(port=5004)


