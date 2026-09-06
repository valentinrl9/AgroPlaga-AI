from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserNotificationPreference(Base):
    __tablename__ = "user_notification_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    push_scan_validation = Column(Boolean, default=True, nullable=False)
    push_incidents = Column(Boolean, default=True, nullable=False)
    push_carencia = Column(Boolean, default=True, nullable=False)
    push_alerts_comarcal = Column(Boolean, default=False, nullable=False)
    push_badges = Column(Boolean, default=True, nullable=False)
    push_weekly = Column(Boolean, default=True, nullable=False)
    push_tech_pending = Column(Boolean, default=True, nullable=False)
    quiet_hours_enabled = Column(Boolean, default=True, nullable=False)
    quiet_hours_start = Column(Integer, default=22, nullable=False)
    quiet_hours_end = Column(Integer, default=7, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class NotificationPushLog(Base):
    __tablename__ = "notification_push_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(String(50), nullable=True)
    is_grouped = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
