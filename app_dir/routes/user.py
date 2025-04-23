from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required

from app_dir.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_OK,
    HTTP_RESOURCE_NOT_FOUND,
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
)
from app_dir.models.account_model import Account
from app_dir.services.user_service import UserService

# Change from singular to plural for consistency
user_bp = Blueprint("users", __name__)


@user_bp.route("", methods=["POST"])
def create_user():
    """
    Create a new user.

    Request JSON:
        * email (str): Email address for the new user
        * username (str): Username for the new user
        * password (str): Password for the new user

    :status 201: User created successfully
    :status 400: Missing required fields
    :status 500: Server error

    :return: JSON with user information
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
            HTTP_CREATED,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@user_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """
    Get a user by ID.

    Requires JWT authentication.

    :param user_id: The ID of the user to retrieve
    :type user_id: str

    :reqheader Authorization: JWT token required

    :status 200: User retrieved successfully
    :status 401: Not authorized to access this user
    :status 404: User not found
    :status 500: Server error

    :return: JSON with user information
    """
    try:

        current_user = get_current_user()

        # Only allow access to own user or admin role
        if str(current_user.user_id) != user_id and "admin" not in current_user.roles:
            return (
                jsonify({"error": "Not authorized to access this user"}),
                HTTP_UNAUTHORIZED,
            )

        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), HTTP_RESOURCE_NOT_FOUND

        return (
            jsonify(
                {
                    "user": {
                        "id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                    }
                }
            ),
            HTTP_OK,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@user_bp.route("/current", methods=["GET"])
@jwt_required()
def get_current_user_profile():
    """
    Get the current authenticated user's profile.

    Requires JWT authentication.

    :reqheader Authorization: JWT token required

    :status 200: Profile retrieved successfully
    :status 401: Not authenticated
    :status 500: Server error

    :return: JSON with user information
    """
    try:
        current_user = get_current_user()
        return (
            jsonify({"user": current_user.get_user_profile()}),
            HTTP_OK,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@user_bp.route("/<user_id>/password", methods=["PUT"])
@jwt_required()
def update_password(user_id):
    """
    Update a user's password.

    Requires JWT authentication.

    :param user_id: The ID of the user whose password to update
    :type user_id: str

    :reqheader Authorization: JWT token required

    Request JSON:
        * current_password (str): The current password of the user
        * new_password (str): The new password to set

    :status 200: Password updated successfully
    :status 400: Missing required fields or invalid current password
    :status 401: Not authorized to update this user's password
    :status 500: Server error

    :return: JSON with a success message
    """
    current_user = get_current_user()

    # Only allow users to change their own password
    if str(current_user.user_id) != user_id:
        return (
            jsonify({"error": "Not authorized to update this user's password"}),
            HTTP_UNAUTHORIZED,
        )

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

    try:
        UserService.set_new_password(
            current_user.username, new_password, current_password
        )
        return jsonify({"message": "Password updated successfully"}), HTTP_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@user_bp.route("/<user_id>/accounts", methods=["GET"])
@jwt_required()
def get_accounts(user_id):
    """
    Get all accounts for the authenticated user.

    Requires JWT authentication.

    :reqheader Authorization: JWT token required

    :status 200: Successfully retrieved accounts
    :status 500: Server error

    :return: JSON contains a list of accounts
    """
    try:
        current_user = get_current_user()
        return_user = UserService.get_user_by_id(user_id)
        if not current_user == return_user and not [
            True for role in current_user.roles.split() if role.upper() == "ADMIN"
        ]:
            raise ValueError("Unauthorized to retrieve accounts for this user")
        accounts = Account.query.filter_by(user_id=user_id).all()
        account_list = [account.get_account_details() for account in accounts]

        return jsonify({"accounts": account_list}), HTTP_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
