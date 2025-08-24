from datetime import datetime,timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class PaymentReminder(Base):
    __tablename__ = "payment_reminders"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    sent_at = Column(DateTime, default=datetime.now(timezone.utc))
    method = Column(String(10), nullable=False)  # "sms" or "email"
    status = Column(String(20), nullable=False)  # "sent", "failed"
    payment = relationship("Payment")
