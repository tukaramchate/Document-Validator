from datetime import datetime, timezone
from models import db


class TokenBlacklist(db.Model):
    """Stores revoked JWT tokens so they can no longer be used.

    Tokens are blacklisted on:
      - Explicit logout
      - Password change (invalidates all previous tokens)
    """
    __tablename__ = 'token_blacklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(512), unique=True, nullable=False, index=True)  # The raw JWT string
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    revoked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)  # So we can prune old entries

    @staticmethod
    def is_token_revoked(token_string):
        """Check whether a token has been revoked."""
        return db.session.query(
            TokenBlacklist.query.filter_by(jti=token_string).exists()
        ).scalar()

    @staticmethod
    def prune_expired():
        """Delete blacklist entries whose tokens have already expired."""
        now = datetime.now(timezone.utc)
        deleted = TokenBlacklist.query.filter(TokenBlacklist.expires_at < now).delete()
        db.session.commit()
        return deleted

    def __repr__(self):
        return f'<TokenBlacklist user_id={self.user_id}>'
