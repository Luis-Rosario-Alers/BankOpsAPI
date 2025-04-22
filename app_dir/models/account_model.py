import hashlib
import logging
import os
from datetime import datetime, timezone

from app_dir.extensions import db

logger = logging.getLogger(
    "core"
)  # TODO: change this logger to a more sophisticated logging system.


class Account(db.Model):
    __tablename__ = "account"

    valid_account_types = {
        "CHECKING": "Checking",
        "SAVINGS": "Savings",
        "CERTIFICATE OF DEPOSIT": "Certificate of Deposit",
    }

    # Identity columns
    account_number: db.Mapped[int] = db.mapped_column(
        db.Integer, primary_key=True, autoincrement=True, unique=True
    )  # TODO: make account number unique and not simply autoincrement.
    user_id: db.Mapped[int] = db.mapped_column(
        db.Integer, db.ForeignKey("user.user_id"), nullable=False
    )

    # Account information
    account_holder: db.Mapped[str] = db.mapped_column(db.String(45), nullable=False)
    account_type: db.Mapped[str] = db.mapped_column(
        db.Enum("CHECKING", "SAVINGS", "CERTIFICATE OF DEPOSIT"), nullable=False
    )
    account_name: db.Mapped[str] = db.mapped_column(db.String(45), nullable=False)
    creation_date: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    # Financial details
    balance: db.Mapped[float] = db.mapped_column(
        db.DECIMAL(13, 2), nullable=False, default=0.0
    )
    interest_rate: db.Mapped[float] = db.mapped_column(
        db.DECIMAL(6, 3), nullable=False, default=0.0
    )
    latest_balance_change: db.Mapped[float] = db.mapped_column(
        db.DECIMAL(13, 2), nullable=False, default=0.0
    )
    last_transaction_date: db.Mapped[datetime] = db.mapped_column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )

    # Security information
    pin_hash: db.Mapped[bytes] = db.mapped_column(db.LargeBinary, nullable=False)
    pin_salt: db.Mapped[bytes] = db.mapped_column(db.LargeBinary, nullable=False)
    is_locked: db.Mapped[bool] = db.mapped_column(db.Boolean, default=False)

    # Relationships
    user = db.relationship("User", back_populates="accounts")

    def set_pin(self, pin: str) -> None:
        """Securely hash and store the PIN."""
        # Generate a new salt and hash the PIN
        if not isinstance(pin, str):
            raise ValueError("PIN must be a string")
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
