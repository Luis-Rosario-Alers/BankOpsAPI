import datetime
import hashlib
import logging
import os

from sqlalchemy import DECIMAL, Boolean, DateTime, Enum, Integer, LargeBinary, String

from app.extensions import db

logger = logging.getLogger(
    "core"
)  # TODO: change this logger to a more sophisticated logging system.


class Account(db.Model):
    __tablename__ = "account"

    # Identity columns
    account_number: int = db.mapped_column(Integer, primary_key=True)
    user_id: int = db.mapped_column(Integer, nullable=False, foreign_key="user.id")

    # Account information
    account_holder: str = db.mapped_column(String(45), nullable=False)
    account_type: str = db.mapped_column(
        Enum("CHECKING", "SAVINGS", "CERTIFICATE OF DEPOSIT"), nullable=False
    )
    creation_date: datetime.datetime = db.mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    # Financial details
    balance: float = db.mapped_column(DECIMAL(13, 2), nullable=False, default=0.0)
    interest_rate: float = db.mapped_column(DECIMAL(6, 3), nullable=False, default=0.0)

    # Security information
    pin_hash: bytes = db.mapped_column(LargeBinary, nullable=False)
    pin_salt: bytes = db.mapped_column(LargeBinary, nullable=False)
    is_locked: bool = db.mapped_column(Boolean, default=False)

    # Relationships
    user = db.relationship("User", back_populates="accounts")

    bank_accounts = 0  # Class variable for tracking count

    def __init__(self, name: str, balance: float, user_id: int, pin: str) -> None:
        self.name = name
        self.balance = balance
        self.interest_rate = 0.0
        self.is_locked = False
        self.user_id = user_id
        self.pin_hash = None
        self.pin_salt = None
        self.set_pin(pin)
        Account.bank_accounts += 1

    @classmethod
    def get_all_bank_accounts(cls) -> int:
        return cls.bank_accounts

    def set_pin(self, account, pin: str) -> None:
        """Securely hash and store the PIN."""
        # Generate a new salt and hash the PIN
        salt = os.urandom(32)
        self.pin_salt = salt
        self.pin_hash = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 100000)
        db.session.commit()

    def verify_pin(self, pin: str) -> bool:
        """Verify if the provided PIN matches this account's PIN."""
        if not self.pin_salt or not self.pin_hash:
            return False

        hash_to_check = hashlib.pbkdf2_hmac(
            "sha256", pin.encode("utf-8"), self.pin_salt, 100000
        )
        return hash_to_check == self.pin_hash
