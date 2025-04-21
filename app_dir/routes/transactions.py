from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required

from app_dir.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_OK,
    HTTP_SERVER_ERROR,
)
from app_dir.services.account_service import AccountService
from app_dir.services.auth_service import AuthService

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("", methods=["POST"])
@jwt_required()
def create_transaction(account_number):  # TODO: refactor this function to use services
    """
    Create a new transaction (deposit, withdrawal, or transfer).

    Requires JWT authentication.

    :reqheader Authorization: JWT token required

    Request JSON:
        * type (str): Transaction type ('deposit', 'withdrawal', 'transfer')
        * from_account (int): Source account number
          (required for transfer and withdrawal)
        * to_account (int): Destination account number
          (required for transfer)
        * account_number (int): Account number
          (can be used instead of from_account for deposit/withdrawal)
        * amount (float): Amount to transfer/deposit/withdraw
        * description (str, optional): Description of the transaction

    :status 201: Transaction created successfully
    :status 400: Missing required fields or validation error
    :status 500: Server error

    :return: JSON with success message or error
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request data"}), HTTP_BAD_REQUEST

    transaction_type = data.get("type")
    amount = data.get("amount")
    description = data.get("description", "")

    if not transaction_type or not amount:
        return (
            jsonify({"error": "Transaction type and amount are required"}),
            HTTP_BAD_REQUEST,
        )

    user = get_current_user()

    try:
        if transaction_type.lower() == "transfer":
            from_account = data.get("from_account")
            to_account = data.get("to_account")

            if not from_account or not to_account:
                return (
                    jsonify(
                        {
                            "error": "Source and destination accounts "
                            "are required for transfers"
                        }
                    ),
                    HTTP_BAD_REQUEST,
                )

            AccountService.transfer(from_account, to_account, amount, description, user)
            return (
                jsonify(
                    {
                        "message": "Transfer successful",
                        "transaction": {
                            "type": "transfer",
                            "from_account": from_account,
                            "to_account": to_account,
                            "amount": amount,
                            "description": description,
                        },
                    }
                ),
                HTTP_CREATED,
            )

        elif transaction_type.lower() == "withdrawal":
            account_number = data.get("account_number") or data.get("from_account")

            if not account_number:
                return (
                    jsonify({"error": "Account number is required for withdrawals"}),
                    HTTP_BAD_REQUEST,
                )

            AccountService.withdrawal(account_number, amount, description, user)
            return (
                jsonify(
                    {
                        "message": "Withdrawal successful",
                        "transaction": {
                            "type": "withdrawal",
                            "account": account_number,
                            "amount": amount,
                            "description": description,
                        },
                    }
                ),
                HTTP_CREATED,
            )

        elif transaction_type.lower() == "deposit":
            account_number = data.get("account_number") or data.get("to_account")

            if not account_number:
                return (
                    jsonify({"error": "Account number is required for deposits"}),
                    HTTP_BAD_REQUEST,
                )

            AccountService.deposit(account_number, amount, description, user)
            return (
                jsonify(
                    {
                        "message": "Deposit successful",
                        "transaction": {
                            "type": "deposit",
                            "account": account_number,
                            "amount": amount,
                            "description": description,
                        },
                    }
                ),
                HTTP_CREATED,
            )

        else:
            return (
                jsonify({"error": f"Unknown transaction type: {transaction_type}"}),
                HTTP_BAD_REQUEST,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST


@transactions_bp.route("", methods=["GET"])
@jwt_required()
def get_transactions():
    """
    Get transactions for the authenticated user.

    Requires JWT authentication.

    :reqheader Authorization: JWT token required

    Request JSON:
        * account_number (int, optional): Filter transactions by account number
        * type (str, optional): Filter transactions by type
        * limit (int, optional): Maximum number of transactions to return (default: 30)
        * offset (int, optional): Offset for pagination (default: 0)

    :status 200: Successfully retrieved transactions
    :status 400: Invalid query parameters
    :status 500: Server error

    :return: JSON containing a list of transactions
    """
    try:
        user = get_current_user()

        # Get query parameters
        account_number = request.args.get("account_number")
        transaction_type = request.args.get("type")
        limit = request.args.get("limit", 30)
        offset = request.args.get("offset", 0)

        if account_number:
            AuthService.verify_account_ownership(user, int(account_number))

        from app_dir.services.transaction_service import TransactionService

        transactions = TransactionService.get_transactions(
            user=user,
            account_number=account_number,
            transaction_type=transaction_type,
            limit=limit,
            offset=offset,
        )

        return jsonify({"transactions": transactions}), HTTP_OK

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_SERVER_ERROR
