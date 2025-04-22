from datetime import datetime, timezone
from decimal import Decimal

from app_dir.extensions import db
from app_dir.models.account_model import Account
from app_dir.models.transaction_model import Transaction
from app_dir.services.auth_service import AuthService


class AccountService:
    def __init__(self):
        pass

    @staticmethod
    def transfer(
        from_account_number, to_account_number, amount, description=None, user=None
    ):
        """Process a transfer between two accounts"""
        try:
            amount = Decimal(amount)
            from_account = Account.query.get(from_account_number)
            to_account = Account.query.get(to_account_number)
            # We always assume that the user is the one who owns the from_account
            # and to_account is the one that is being transferred to.
            # This is a security measure to ensure that the user is not transferring
            # money to an account they do not own.
            if not AuthService.verify_account_ownership(user, from_account_number):
                raise ValueError("sender account does not belong to the user")
            if not AuthService.verify_account_ownership(user, to_account_number):
                raise ValueError("receiver account does not belong to the user")

            # Check if accounts exist
            if not from_account or not to_account:
                raise ValueError("One or both accounts not found")
            # Check if accounts are locked
            if from_account.is_locked or to_account.is_locked:
                raise ValueError("One or both accounts are locked")
            # Check if the transfer amount is valid
            if amount < 0:
                raise ValueError("Transfer amount cannot be negative")
            # Check if the transfer amount is greater than the balance
            # of the form account
            if amount > from_account.balance:
                raise ValueError("Not enough funds in account")

            # Show transfer between accounts properly
            from_account.latest_transaction_change = -amount
            to_account.latest_transaction_change = +amount

            from_account.balance -= amount
            to_account.balance += amount

            transaction = Transaction(
                account_from=from_account_number,
                account_to=to_account_number,
                amount=amount,
                transaction_type="TRANSFER",
                description=description or f"Transfer of ${amount:.2f}",
                balance_after=from_account.balance,
            )
            db.session.add(transaction)
            db.session.commit()
            return from_account.balance

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def deposit(account_number, amount, description=None, user=None):
        """Process a deposit to an account"""
        try:
            # this is necessary because the amount must be the same
            # type as the balance for arithmetic operations i.e., Decimal
            amount = Decimal(amount)
            account = Account.query.get(account_number)
            if not account:
                raise ValueError(f"Account {account_number} not found")
            if account.is_locked:
                raise ValueError(f"Account {account_number} is locked")
            if amount < 0:
                raise ValueError("Deposit amount cannot be negative")
            account.latest_transaction_change = +amount

            account.balance += amount
            # Create a transaction record
            transaction = Transaction(
                account_from=account_number,
                account_to=account_number,
                amount=amount,
                balance_after=account.balance,
                transaction_type="DEPOSIT",
                description=description or f"Deposit of ${amount:.2f}",
            )

            db.session.add(transaction)

            db.session.commit()
            # logger.info(f"Deposit of {amount} to account {account_id} successful")
            return transaction

        except Exception:
            db.session.rollback()
            # logger.error(f"Deposit failed: {str(e)}")
            raise

    @staticmethod
    def withdrawal(account_number, amount, description=None, user=None):
        """Process a withdrawal from an account"""
        try:
            amount = Decimal(amount)
            account = Account.query.get(account_number)
            if not AuthService.verify_account_ownership(user, account_number):
                raise ValueError("Account does not belong to the user")
            if not account:
                raise ValueError(f"Account {account_number} not found")
            if account.is_locked:
                raise ValueError(f"Account {account_number} is locked")
            if amount < 0:
                raise ValueError("Withdraw amount cannot be negative")
            if amount <= account.balance:

                account.latest_transaction_change = -amount

                account.balance -= amount

                transaction = Transaction(
                    account_from=account_number,
                    account_to=account_number,
                    balance_after=account.balance,
                    amount=amount,
                    status="COMPLETED",
                    timestamp=datetime.now(timezone.utc),
                    transaction_type="WITHDRAWAL",
                    description=description or f"Withdrawal of ${amount:.2f}",
                )
                db.session.add(transaction)

                db.session.commit()
                return account.balance
            else:
                raise ValueError("Not enough funds in account.")
        except Exception:
            db.session.rollback()
            # TODO: Add better logging.
            raise

    @staticmethod
    def change_account_pin(user_id, account_number, current_pin, new_pin):
        """Change an account PIN with verification"""
        # Find the account and verify it belongs to the user
        account = Account.query.filter_by(id=account_number, user_id=user_id).first()

        if not account:
            raise ValueError("Account not found or doesn't belong to you")

        if not account.verify_pin(current_pin):
            return False

        if not new_pin.isdigit() or len(new_pin) != 4:
            raise ValueError("PIN must be 4 digits")

        # Change the PIN
        account.set_pin(new_pin)
        db.session.commit()

        return True
