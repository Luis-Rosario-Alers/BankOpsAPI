import datetime
import hashlib
import os
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_dir.extensions import db


class User(db.Model):
    __tablename__ = "user"
    # User identity columns
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # User authentication details
    password_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    password_salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # User activity information
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_password_change: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True
    )
    # TODO: add functionality to track last password change and attempts
    # User account history information
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, default=datetime.datetime.now, nullable=True
    )
    # TODO: add functionality to track last login
    accounts = relationship("Account", back_populates="user")

    @property
    def full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Securely hash and store the password."""
        salt = os.urandom(32)
        self.password_salt = salt
        self.password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100000
        )

    def check_password(self, password: str) -> None:
        """Check if the provided password matches the stored hash."""
        hash_to_check = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.password_salt, 100000
        )
        return hash_to_check == self.password_hash
