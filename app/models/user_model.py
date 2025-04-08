import datetime
import hashlib
import os

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

from app.extensions import db

Base = declarative_base()


class User(db.Model):
    __tablename__ = "user"
    # User identity columns
    user_id: int = db.mapped_column(Integer, primary_key=True)
    username: str = db.mapped_column(String(50), unique=True, nullable=False)
    email: str = db.mapped_column(String(100), unique=True, nullable=False)

    # User authentication details
    password_hash: bytes = db.mapped_column(LargeBinary, nullable=False)
    password_salt: bytes = db.mapped_column(LargeBinary, nullable=False)

    # User activity information
    is_active: bool = db.mapped_column(Boolean, default=True)
    is_admin: bool = db.mapped_column(Boolean, default=False)
    failed_login_attempts: int = db.mapped_column(Integer, default=0)
    last_password_change: datetime = db.mapped_column(DateTime, nullable=True)

    # User account history information
    created_at: datetime = db.mapped_column(
        DateTime, default=datetime.datetime.now, nullable=False
    )
    updated_at: datetime = db.mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    last_login: datetime = db.mapped_column(DateTime)

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
