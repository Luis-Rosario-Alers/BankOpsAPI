from datetime import datetime, timezone

from app_dir.extensions import db


class JWTToken(db.Model):
    __tablename__ = "jwt_token"
    id: db.Mapped[str] = db.mapped_column(db.String(36), primary_key=True)
    user_id: db.Mapped[int] = db.mapped_column(
        db.Integer, db.ForeignKey("user.user_id"), nullable=False
    )
    is_blacklisted: db.Mapped[bool] = db.mapped_column(db.Boolean, default=False)
    created_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime, default=datetime.now(timezone.utc)
    )
    expires_at: db.Mapped[datetime] = db.mapped_column(db.DateTime, nullable=False)

    user = db.relationship("User", back_populates="jwt_tokens")

    @staticmethod
    def create_token_log(jti, user_id, expires_at):
        """
        Create a new JWT token for a user.

        :param user_id: ID of the user
        :param jti: Unique identifier for the token
        :param expires_at: Expiration time for the token
        :return: New JWT token object
        """
        new_token = JWTToken(id=jti, user_id=user_id, expires_at=expires_at)
        db.session.add(new_token)
        db.session.commit()
        return new_token

    @staticmethod
    def revoke_token(jti, user_id, revoke_all: bool = False):
        if revoke_all:
            db.session.query(JWTToken).filter_by(user_id=user_id).delete()
        else:
            db.session.query(JWTToken).filter_by(id=jti, user_id=user_id).update(
                {"is_blacklisted": True}
            )
        db.session.commit()
