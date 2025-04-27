from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)
from sqlalchemy.exc import IntegrityError

from app_dir.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_NO_CONTENT,
    HTTP_OK,
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
)
from app_dir.extensions import db
from app_dir.models.jwttoken import JWTToken
from app_dir.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/sessions/users", methods=["POST"])
def create_session():
    """
    Create a new authentication session (login).

    Request JSON:
        * username (str): The username to authenticate
        * password (str): The password for authentication

    :status 201: Session created successfully
    :status 400: Missing required fields
    :status 401: Invalid username or password
    :status 500: Server error

    :return: JSON with access token and user information
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

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

        # create an access token for the user
        access_token = create_access_token(identity=user.username)

        refresh_token = create_refresh_token(identity=user.username)

        JWTToken.create_token_log(
            jti=decode_token(refresh_token)["jti"],
            user_id=user.user_id,
            expires_at=datetime.fromtimestamp(
                decode_token(refresh_token)["exp"], tz=timezone.utc
            ),
        )

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "access_token_expires_in": decode_token(access_token)["exp"],
                    "refresh_token": refresh_token,
                    "refresh_token_expires_in": decode_token(refresh_token)["exp"],
                    "user": user.username,
                    "roles": user.roles,
                    "message": "Login successful",
                }
            ),
            HTTP_CREATED,
        )

    except IntegrityError:
        return jsonify({"error": "Database integrity error"}), HTTP_SERVER_ERROR
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@auth_bp.route("/sessions/users/current", methods=["GET"])
@jwt_required()
def get_current_session():
    """
    Get information about the current authentication session.

    Requires JWT authentication.

    :reqheader Authorization: JWT token required

    :status 200: Session retrieved successfully
    :status 401: Not authenticated
    :status 500: Server error

    :return: JSON with current user information
    """
    try:
        current_user = get_current_user()
        return (
            jsonify({"user": current_user.username, "roles": current_user.roles}),
            HTTP_OK,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@auth_bp.route("/sessions/users/current", methods=["DELETE"])
@jwt_required()
def delete_session():
    """
    End the current authentication session (logout).

    Requires JWT authentication.

    Request JSON:
        * revoke_all (bool, optional): If true, will revoke all tokens associated
          with the current user. Useful for "log out on all devices" functionality.

    :reqheader Authorization: JWT token required

    :status 204: Session ended successfully
    :status 401: Not authenticated
    :status 500: Server error

    :return: Empty response
    """
    try:
        response = jsonify({})
        unset_jwt_cookies(response)
        JWTToken.revoke_token(jti=get_jwt()["jti"], user_id=get_current_user().user_id)
        return response, HTTP_NO_CONTENT
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@auth_bp.route("/sessions/accounts/<account_number>", methods=["POST"])
@jwt_required()
def authenticate_account(account_number):
    """
    Authenticate with an account using its PIN (creates an account session).

    Requires JWT authentication.

    :param account_number: The account number to authenticate
    :type account_number: int

    :reqheader Authorization: JWT token required

    Request JSON:
        * pin (int): The PIN code for the account

    :status 200: Authentication successful
    :status 400: Missing required fields
    :status 401: Invalid PIN or locked account
    :status 404: Account not found
    :status 500: Server error

    :return: JSON containing account details and success message
    """
    identity = get_jwt_identity()

    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    pin = data.get("pin")

    if not pin:
        return jsonify({"error": "PIN is required"}), HTTP_BAD_REQUEST

    try:
        # Get an authenticated account with details
        account = AuthService.authenticate_account(identity, account_number, pin)
        if not account:
            return (
                jsonify({"error": "Invalid account number or PIN"}),
                HTTP_UNAUTHORIZED,
            )

        if account.is_locked:
            return jsonify({"error": "Account is locked"}), HTTP_UNAUTHORIZED

        return (
            jsonify(
                {
                    "account": {
                        "account_number": account.account_number,
                        "account_name": account.account_name,
                        "balance": account.balance,
                        "account_type": account.account_type,
                        "holder": account.account_holder,
                        "currency": account.currency,
                    },
                    "message": "Authentication successful",
                }
            ),
            HTTP_OK,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@auth_bp.route("/sessions/renew", methods=["POST"])
@jwt_required(refresh=True, verify_type=True)
def renew_session():
    """Attempts to renew the current session."""
    try:
        refresh_token = get_jwt()["jti"]
        user = get_current_user()

        refresh_token_object = JWTToken.query.filter_by(
            id=refresh_token, user_id=user.user_id, is_blacklisted=False
        ).first()

        if refresh_token_object is None:
            return jsonify({"error": "Invalid refresh token"}), HTTP_UNAUTHORIZED

        db.session.delete(refresh_token_object)

        new_refresh_token = create_refresh_token(identity=user.username)
        new_access_token = create_access_token(identity=user.username)

        JWTToken.create_token_log(
            jti=decode_token(new_refresh_token)["jti"],
            user_id=user.user_id,
            expires_at=datetime.fromtimestamp(
                decode_token(new_refresh_token)["exp"], tz=timezone.utc
            ),
        )

        db.session.commit()

        return (
            jsonify(
                {
                    "access_token": new_access_token,
                    "access_token_expires_in": decode_token(new_access_token)["exp"],
                    "refresh_token": new_refresh_token,
                    "refresh_token_expires_in": decode_token(new_refresh_token)["exp"],
                }
            ),
            HTTP_OK,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
