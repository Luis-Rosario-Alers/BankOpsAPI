from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


db = SQLAlchemy(model_class=Base)
jwt = JWTManager()


def init_extensions(app):
    """Initialize all Flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
