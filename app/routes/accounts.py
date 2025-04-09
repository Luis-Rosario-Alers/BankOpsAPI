from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_OK,
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
)
from app.extensions import db
from app.services.account_service import AccountService
from app.services.auth_service import AuthService

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/<account_number>/pin", methods=["PATCH"])
@jwt_required()
def update_pin(account_number):
    """
    Update the PIN of the account.

    :param account_number: The account number to update
    :type account_number: str

    :**json** request body:
        * **current_pin** (*str*): The current PIN for the account
        * **new_pin** (*str*): The new PIN to set for the account

    :status 200: PIN updated successfully
    :status 400: Missing data or invalid PIN
    :status 401: Account doesn't belong to user
    :status 500: Database or server error
    :return: JSON response with message
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    current_pin = data.get("current_pin")
    new_pin = data.get("new_pin")

    if not current_pin or not new_pin:
        return (
            jsonify({"error": "Current PIN and new PIN are required"}),
            HTTP_BAD_REQUEST,
        )

    # Get the user identity from the JWT
    user = get_jwt_identity()

    try:
        # Verify the account belongs to the authenticated user
        result = AccountService.change_account_pin(
            user_id=user.user_id,
            account_number=account_number,
            current_pin=current_pin,
            new_pin=new_pin,
        )

        if not result:
            return (
                jsonify({"error": "PIN change failed. Verify your current PIN."}),
                HTTP_BAD_REQUEST,
            )

        return jsonify({"message": "PIN updated successfully"}), HTTP_OK

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST
    except IntegrityError:
        return jsonify({"error": "Database integrity error"}), HTTP_SERVER_ERROR
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR


@accounts_bp.route("/register", methods=["POST"])
@jwt_required()
def register_account():
    """
    Register a new account for the user.

    :**json** request body:
        * **account_name** (*str*): Name for the new account
        * **account_type** (*str*): Type of account (must be one of the valid types)
        * **account_pin** (*str*): PIN code to secure the account

    :status 201: Account registered successfully
    :status 400: Missing required fields or invalid account type
    :status 500: Database or server error
    :return: JSON response with message
    """
    user = get_jwt_identity()

    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    account_name = data.get("account_name")
    account_type = data.get("account_type")
    account_pin = data.get("account_pin")

    if not account_name or not account_type or not account_pin:
        return (
            jsonify({"error": "Account name, type, and PIN are required"}),
            HTTP_BAD_REQUEST,
        )
    if account_type not in AccountService.ACCOUNT_TYPES:
        return jsonify({"error": "Invalid account type"}), HTTP_BAD_REQUEST

    from app.models.account_model import Account

    new_account = Account(
        name=account_name,
        account_holder=user.username,
        account_type=account_type.upper(),
        user_id=user.user_id,
        pin=account_pin,
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "Account registered successfully"}), HTTP_CREATED


@accounts_bp.route("/authenticate", methods=["POST"])
@jwt_required()
def account_login():
    """
    Authenticate with account number and PIN.

    :**json** request body:
        * **account_number** (*str*): The account number to authenticate
        * **pin** (*str*): The PIN code for the account

    :status 200: Login successful with account details
    :status 400: Missing required fields
    :status 401: Invalid credentials or locked account
    :status 500: Server error during authentication
    :return: JSON response with account details including account_number,
             account_name, account_balance, account_type, account_holder,
             account_currency
    """
    identity = get_jwt_identity()

    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    account_number = data.get("account_number")
    pin = data.get("pin")

    if not account_number or not pin:
        return (
            jsonify({"error": "Account number and PIN are required"}),
            HTTP_BAD_REQUEST,
        )

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
                    "account_number": account.account_number,
                    "account_name": account.name,
                    "account_balance": account.balance,
                    "account_type": account.account_type,
                    "account_holder": account.account_holder,
                    "account_currency": account.currency,
                    "message": "Login successful",
                }
            ),
            HTTP_OK,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
