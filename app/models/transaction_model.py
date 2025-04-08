from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    DateTime,
    Enum,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

from app.extensions import db

Base = declarative_base()


class Transaction(db.Model):
    __tablename__ = "transaction"
    # Primary key
    transaction_id: int = db.mapped_column(Integer, primary_key=True)

    # Transaction details
    transaction_type: str = db.mapped_column(
        Enum("DEPOSIT", "WITHDRAWAL", "TRANSFER"), nullable=False
    )
    amount: float = db.mapped_column(DECIMAL(13, 2), nullable=False)
    description: str = db.mapped_column(String(255), nullable=True)
    reference_code: str = db.mapped_column(String(50), unique=True, nullable=False)

    # Accounts information
    account_from: int = db.mapped_column(Integer, nullable=False)
    account_to: int = db.mapped_column(Integer, nullable=False)

    # Status and tracking
    status: str = db.mapped_column(
        Enum("PENDING", "COMPLETED", "FAILED", "REVERSED"), default="PENDING"
    )
    timestamp: datetime = db.mapped_column(DateTime, default=datetime.today())
    balance_after: float = db.mapped_column(DECIMAL(13, 2), nullable=False)

    # Relationships
    account_from_relationship = relationship("Account", foreign_keys=[account_from])
    account_to_relationship = relationship("Account", foreign_keys=[account_to])

    def get_transaction_details(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
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
