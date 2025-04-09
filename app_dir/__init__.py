from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()


def init_app(app):
    db.init_app(app)
    jwt.init_app(app)
