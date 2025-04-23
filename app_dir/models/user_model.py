import hashlib
import os
from datetime import datetime, timezone
from typing import Optional

from app_dir.extensions import db


class User(db.Model):
    __tablename__ = "user"
    # User identity columns
    user_id: db.Mapped[int] = db.mapped_column(
        db.Integer, primary_key=True, autoincrement=True
    )
    username: db.Mapped[str] = db.mapped_column(
        db.String(50), unique=True, nullable=False
    )
    email: db.Mapped[str] = db.mapped_column(
        db.String(100), unique=True, nullable=False
    )

    # User authentication details
    password_hash: db.Mapped[bytes] = db.mapped_column(db.LargeBinary, nullable=False)
    password_salt: db.Mapped[bytes] = db.mapped_column(db.LargeBinary, nullable=False)

    # User activity information
    is_active: db.Mapped[bool] = db.mapped_column(db.Boolean, default=True)
    roles: db.Mapped[bool] = db.mapped_column(
        db.Enum("CUSTOMER", "ADMIN"), default="CUSTOMER"
    )
    failed_login_attempts: db.Mapped[int] = db.mapped_column(db.Integer, default=0)
    last_password_change: db.Mapped[Optional[datetime]] = db.mapped_column(
        db.DateTime, nullable=True
    )
    # TODO: add functionality to track last password change and attempts
    # User account history information
    created_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    updated_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now
    )
    last_login: db.Mapped[Optional[datetime]] = db.mapped_column(
        db.DateTime, default=datetime.now(timezone.utc), nullable=True
    )
    # TODO: add functionality to track last login
    accounts = db.relationship("Account", back_populates="user")
    jwt_tokens = db.relationship("JWTToken", back_populates="user")

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.username}>"

    def get_user_profile(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
        }

    def set_password(self, password: str) -> None:
        """Securely hash and store the password."""
        salt = os.urandom(32)
        self.password_salt = salt
        self.password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100000
        )
        self.last_password_change = datetime.now()
        self.failed_login_attempts = 0

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        hash_to_check = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.password_salt, 100000
        )
        return hash_to_check == self.password_hash
