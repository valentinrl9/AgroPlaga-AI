from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"
    __table_args__ = (UniqueConstraint("user_id", "plague", name="uq_user_plague_pref"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plague = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
