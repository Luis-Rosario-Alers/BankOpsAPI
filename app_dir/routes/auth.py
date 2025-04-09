from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_current_user,
    jwt_required,
)
from sqlalchemy.exc import IntegrityError

from app_dir.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_OK,
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
)
from app_dir.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
@jwt_required(optional=True)
def user_login():
    """Authenticates user with username and password"""
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    current_user = get_current_user()
    if current_user:
        return (
            jsonify({"message": "Already logged in", "user": current_user.username}),
            HTTP_OK,
        )

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return (
            jsonify({"error": "Username and password are required"}),
            HTTP_BAD_REQUEST,
        )

    try:
        user = AuthService.authenticate_user(username, password)
        if not user:
            return jsonify({"error": "Invalid username or password"}), HTTP_UNAUTHORIZED

        # create access token for the user.
        access_token = create_access_token(
            identity=user.username, expires_delta=timedelta(days=1)
        )

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "user": user.username,
                    "roles": user.roles,
                    "message": "Login successful",
                }
            ),
            HTTP_OK,
        )

    except IntegrityError:
        return jsonify({"error": "Database integrity error"}), HTTP_SERVER_ERROR
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
