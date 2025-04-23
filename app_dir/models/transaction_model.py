from datetime import datetime, timezone
from typing import Optional

from app_dir.extensions import db


class Transaction(db.Model):
    __tablename__ = "transaction"
    # Primary key
    transaction_id: db.Mapped[int] = db.mapped_column(
        db.Integer, primary_key=True, autoincrement=True
    )

    # Transaction details
    transaction_type: db.Mapped[str] = db.mapped_column(
        db.Enum("DEPOSIT", "WITHDRAWAL", "TRANSFER"), nullable=False
    )

    amount: db.Mapped[float] = db.mapped_column(db.DECIMAL(13, 2), nullable=False)

    description: db.Mapped[Optional[str]] = db.mapped_column(
        db.String(255), nullable=True
    )
    reference_code: db.Mapped[str] = db.mapped_column(
        db.String(50), unique=True, nullable=False
    )

    # Account information
    account_from: db.Mapped[int] = db.mapped_column(
        db.Integer, db.ForeignKey("account.account_number"), nullable=False
    )
    account_to: db.Mapped[int] = db.mapped_column(
        db.Integer, db.ForeignKey("account.account_number"), nullable=False
    )

    # Status and tracking
    status: db.Mapped[str] = db.mapped_column(
        db.Enum("PENDING", "COMPLETED", "FAILED", "REVERSED"), default="PENDING"
    )
    timestamp: db.Mapped[datetime] = db.mapped_column(
        db.DateTime, default=datetime.now(timezone.utc)
    )
    balance_after: db.Mapped[float] = db.mapped_column(
        db.DECIMAL(13, 2), nullable=False
    )

    # Relationships
    account_from_relationship = db.relationship("Account", foreign_keys=[account_from])
    account_to_relationship = db.relationship("Account", foreign_keys=[account_to])

    def get_transaction_details(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "account_from": self.account_from,
            "account_to": self.account_to,
            "amount": self.amount,
            "description": self.description,
            "reference_code": self.reference_code,
            "status": self.status,
            "timestamp": self.timestamp,
            "balance_after": self.balance_after,
        }

    def __repr__(self) -> str:
        return (
            f"<Transaction {self.transaction_id},"
            f"Type: {self.transaction_type},"
            f"Amount: {self.amount}>"
        )
