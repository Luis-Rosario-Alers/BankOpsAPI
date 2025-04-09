from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required

from app_dir.constants.http_status import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
)
from app_dir.services.account_service import AccountService

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():
    """Transfer money between accounts"""
    data = request.get_json()
    from_account_number = data.get("from_account")
    to_account_number = data.get("to_account")
    amount = data.get("amount")
    description = data.get("description")
    if not from_account_number or not to_account_number or not amount:
        return (
            jsonify({"error": "Account numbers and amount are required"}),
            HTTP_BAD_REQUEST,
        )
    try:
        user = get_current_user()
        AccountService.transfer(
            from_account_number, to_account_number, amount, description, user
        )
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST

    return jsonify({"message": "transfer successful."}), HTTP_CREATED


@transactions_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    """Withdraw money from an account"""
    data = request.get_json()
    account_number = data.get("account_number")
    amount = data.get("amount")
    description = data.get("description")
    if not account_number or not amount:
        return (
            jsonify({"error": "Account number and amount are required"}),
            HTTP_BAD_REQUEST,
        )
    try:
        user = get_current_user()
        AccountService.withdrawal(account_number, amount, description, user)
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST

    return jsonify({"message": "withdrawal successful."}), HTTP_CREATED


@transactions_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit():
    """Deposit money into an account"""
    data = request.get_json()
    account_number = data.get("account_number")
    amount = data.get("amount")
    description = data.get("description")
    if not account_number or not amount:
        return (
            jsonify({"error": "Account number and amount are required"}),
            HTTP_BAD_REQUEST,
        )
    try:
        user = get_current_user()
        AccountService.deposit(account_number, amount, description, user)
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_BAD_REQUEST

    return jsonify({"message": "deposit successful."}), HTTP_CREATED
