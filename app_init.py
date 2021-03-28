from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os

basedir = os.path.abspath(os.path.dirname(__file__))

migrate = Migrate()

db = SQLAlchemy()
ma = Marshmallow()
# Only dev available


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(basedir, 'db.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    return app
