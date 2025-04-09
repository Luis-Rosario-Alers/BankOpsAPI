from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required

from app_dir.constants.http_status import HTTP_BAD_REQUEST, HTTP_OK, HTTP_SERVER_ERROR
from app_dir.services.user_service import UserService

user_bp = Blueprint("user", __name__)


@user_bp.route("/password", methods=["POST"])
@jwt_required()
def change_password():
    """
    Change the password of the authenticated user.

    :param current_password: The current password of the user is
    :param new_password: The new password to set for the user
    :return: JSON response with a message
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return (
            jsonify({"error": "Current password and new password are required"}),
            HTTP_BAD_REQUEST,
        )

    user = get_current_user()

    try:
        UserService.set_password(user.username, new_password, current_password)
        return jsonify({"message": "Password updated successfully"}), HTTP_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@user_bp.route("", methods=["POST"])
def register_user():
    """
    Register a new user

    :param email: The email of the user
    :param username: username for the new user
    :param password: password for the new user
    :return: JSON response with user information
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    if not username or not password or not email:
        return (
            jsonify({"error": "Username, password, and email are required"}),
            HTTP_BAD_REQUEST,
        )
    try:
        user = UserService.create_user(username, password, email)
        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "user": {
                        "id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            ),
            HTTP_OK,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
