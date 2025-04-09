from app_dir.extensions import db
from app_dir.models.user_model import User


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def create_user(username, password, email):
        """Create a new user"""
        try:
            if UserService.get_user_by_username(username):
                raise SystemError("Username already exists")
        except ValueError:
            # we pass because internally the function has error
            # handling for not finding a user,
            # but in this case, we want to NOT find a user.
            # this is why we pass.
            pass
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user details"""
        user = UserService.get_user_by_id(user_id)

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
        if old_password and new_password:
            if not user.check_password(old_password):
                raise ValueError("Incorrect password.")
        user.set_password(new_password)
        db.session.commit()
