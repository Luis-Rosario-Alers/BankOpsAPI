import hashlib
import os

from app.extensions import db
from app.models.user_model import User


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def create_user(username, password, email):
        """Create a new user"""
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user details"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.session.commit()
        return user

    @staticmethod
    def set_password(user_id, password: str) -> None:
        """Securely hash and store the password."""
        user = User.query.get(user_id)
        salt = os.urandom(32)
        user.password_salt = salt
        user.password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100000
        )
