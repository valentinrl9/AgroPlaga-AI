from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.base import Base


class PilotInvite(Base):
    __tablename__ = "pilot_invites"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False, default="farmer")
    label = Column(String(120), nullable=True)
    max_uses = Column(Integer, nullable=False, default=1)
    uses_count = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    redeemed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
