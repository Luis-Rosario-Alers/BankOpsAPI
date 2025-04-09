from app_dir.extensions import jwt
from app_dir.services.user_service import UserService


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Callback to load user from JWT token"""
    identity = jwt_data["sub"]
    user = UserService.get_user_by_id(identity)
    return user if user else None  # just in case...
