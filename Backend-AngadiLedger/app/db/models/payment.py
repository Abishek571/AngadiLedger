from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), nullable=False)  # "pending", "paid", "overdue", "disputed"
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer = relationship("Customer")
    created_by = relationship("User")
    payment_ledger_entries = relationship("PaymentLedgerEntry", back_populates="payment")


