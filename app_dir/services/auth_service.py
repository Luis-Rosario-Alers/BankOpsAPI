import hashlib
from typing import Union

from flask import jsonify

from app_dir.constants.http_status import HTTP_UNAUTHORIZED
from app_dir.extensions import jwt
from app_dir.models.account_model import Account
from app_dir.models.user_model import User
from app_dir.services.user_service import UserService


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Callback to load user from JWT token"""
    identity = jwt_data["username"]
    return UserService.get_user_by_username(identity)


@jwt.additional_claims_loader
def add_additional_claims(identity):
    """Add additional claims to the JWT token"""
    user = UserService.get_user_by_username(identity)
    if user:
        return {
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "owned_accounts": [account.account_number for account in user.accounts],
        }


@jwt.unauthorized_loader
def unauthenticated_response(auth_error_response: str):
    """Response for unauthenticated requests"""
    auth_error_response = "Missing or invalid token"
    return jsonify({"error": auth_error_response}), HTTP_UNAUTHORIZED


class AuthService:
    """AuthService handles authentication-related operations."""

    @staticmethod
    def authenticate_account(user, account_number: int, pin: str):
        """Verify if the provided PIN is correct."""
        account = Account.query.get(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        hash_to_check = hashlib.pbkdf2_hmac(
            "sha256", pin.encode("utf-8"), account.pin_salt, 100000
        )

        if account.is_locked:
            raise ValueError("Account is locked.")

        # Ownership check of the account object
        if account.user != user:
            raise ValueError("User does not own this account.")

        # return pin validity
        if hash_to_check == account.pin_hash:
            return account
        else:
            return None

    @staticmethod
    def authenticate_user(username: str, password: str) -> Union[User, bool]:
        """Authenticate user with username and password.
        Checks if the provided password matches the stored hash.
        Return the user object if authentication is successful."""
        user = User.query.filter_by(
            username=username
        ).first()  # remember that username might not be uni
        if not user:
            raise ValueError("Invalid username or password")

        if user.is_admin:
            return True
        if not user.is_active:
            return False
        # Check password
        hash_to_check = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), user.password_salt, 100000
        )
        if hash_to_check != user.password_hash:
            raise ValueError("Invalid username or password")

        return user

    @staticmethod
    def verify_account_ownership(user: User, account_number: int) -> bool:
        """Verify if the user owns the account."""
        account = Account.query.get(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        return account.user == user
