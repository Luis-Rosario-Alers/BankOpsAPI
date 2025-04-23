from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app_dir.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_OK,
    HTTP_RESOURCE_NOT_FOUND,
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
)
from app_dir.extensions import db
from app_dir.models.account_model import Account
from app_dir.services.account_service import AccountService

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/<account_number>/pin", methods=["PUT"])
@jwt_required()
def update_pin(account_number):
    """
    Update the PIN of the account.

    Requires JWT authentication.

    :param account_number: The account number to update
    :type account_number: int

    :reqheader Authorization: JWT token required

    Request JSON:
        * current_pin (str): The current PIN for the account
        * new_pin (str): The new PIN to set for the account

    :status 200: PIN updated successfully
    :status 400: Missing data or invalid PIN
    :status 401: Unauthorized: Account doesn't belong to user
    :status 500: Database or server error

    :return: JSON with success message or error
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


@accounts_bp.route("", methods=["POST"])
@jwt_required()
def create_account():
    """
    Create a new account for the authenticated user.

    Requires JWT authentication.

    :reqheader Authorization: JWT token required

    Request JSON:
        * account_name (str): Name for the new account
        * account_type (str): Type of account (must be one of: {valid_types})
        * account_pin (str): PIN code to secure the account

    :status 201: Account created successfully
    :status 400: Missing required fields or invalid account type
    :status 500: Database or server error

    :return: JSON with success message or error
    """

    user = get_current_user()

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

    # Check if account_type is valid and included in an account_types account model.
    # Also we do .upper() to stay consistent with the model casing.
    if account_type.upper() not in Account.valid_account_types:
        return jsonify({"error": "Invalid account type"}), HTTP_BAD_REQUEST

    new_account = Account(
        account_name=account_name,
        account_holder=user.username,
        account_type=account_type.upper(),
        user_id=user.user_id,
    )
    # Set pin for the new account
    try:
        new_account.set_pin(account_pin)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST
    db.session.add(new_account)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Account created successfully",
                "account": {
                    "account_number": new_account.account_number,
                    "account_name": new_account.account_name,
                    "account_type": new_account.account_type,
                },
            }
        ),
        HTTP_CREATED,
    )


@accounts_bp.route("/<account_number>", methods=["GET"])
@jwt_required()
def get_account(account_number):
    """
    Get details of a specific account.

    Requires JWT authentication.

    :param account_number: The account number to retrieve
    :type account_number: str

    :reqheader Authorization: JWT token required

    :status 200: Successfully retrieved account
    :status 401: Unauthorized: Account doesn't belong to user
    :status 404: Account not found
    :status 500: Server error

    :return: JSON containing account details
    """
    user = get_current_user()

    try:
        account = Account.query.filter_by(account_number=account_number).first()

        if not account:
            return jsonify({"error": "Account not found"}), HTTP_RESOURCE_NOT_FOUND

        if account.user_id != user.user_id:
            # TODO: use auth account ownership function instead.
            return (
                jsonify({"error": "You are not authorized to access this account"}),
                HTTP_UNAUTHORIZED,
            )

        return (
            jsonify(
                {
                    "account": {
                        "account_number": account.account_number,
                        "account_name": account.account_name,
                        "account_type": account.account_type,
                        "balance": account.balance,
                        "holder": account.account_holder,
                    }
                }
            ),
            HTTP_OK,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
