from app.extensions import db
from app.models.user_model import User
from app.services.auth_service import AuthService


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def create_user(username, password, email):
        """Create a new user"""
        user = User(username=username, email=email)
        user.set_password(password)

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
    def set_new_password(username, new_password: str, old_password: str) -> None:
        """
        Securely hash and store the password
        or change password depending on params.
        """
        user = UserService.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        if old_password and new_password:
            if not AuthService.authenticate_user(username, old_password):
                raise ValueError("User authentication failed")
        user.set_password(new_password)
        db.session.commit()
