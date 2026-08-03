from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TechNotification(Base):
    __tablename__ = "tech_notifications"

    id = Column(Integer, primary_key=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    notification_type = Column(String(40), nullable=False, default="scan_pending")
    title = Column(String(120), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    recipient = relationship("User", foreign_keys=[recipient_id])
    scan = relationship("Scan", foreign_keys=[scan_id])
