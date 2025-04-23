from sqlalchemy import desc

from app_dir.models.account_model import Account
from app_dir.models.transaction_model import Transaction
from app_dir.models.user_model import User


class TransactionService:
    def __init__(self):
        pass

    @staticmethod
    def get_transactions(
        user: User, account_number=None, transaction_type=None, limit=30, offset=0
    ):
        # Default values for limit and offset if not provided or invalid
        try:
            limit = int(limit) if limit is not None else 30
            offset = int(offset) if offset is not None else 0
            if limit < 0 or offset < 0:
                raise ValueError("Limit and offset must be non-negative integers")
        except (ValueError, TypeError):
            limit = 30
            offset = 0

        try:
            base_query = (
                Transaction.query.join(
                    Account,
                    (
                        (Transaction.account_from == Account.account_number)
                        | (Transaction.account_to == Account.account_number)
                    ),
                )
                .filter(Account.user_id == user.user_id)
                .distinct()
            )

            # Apply optional filters
            if account_number is not None:
                if isinstance(account_number, str):
                    account_number = int(account_number)

                base_query = base_query.filter(
                    (Transaction.account_from == account_number)
                    | (Transaction.account_to == account_number)
                )

            if transaction_type is not None and transaction_type.upper() in [
                "DEPOSIT",
                "WITHDRAWAL",
                "TRANSFER",
            ]:
                base_query = base_query.filter(
                    Transaction.transaction_type == transaction_type.upper()
                )

            transactions = (
                base_query.order_by(desc(Transaction.timestamp))
                .offset(offset)
                .limit(limit)
                .all()
            )

            result = [t.get_transaction_details() for t in transactions]

            return result

        except Exception as e:
            raise e
