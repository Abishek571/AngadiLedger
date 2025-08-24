from datetime import datetime,timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.db.models.payment import Payment


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    entry_type = Column(String(10), nullable=False) 
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer = relationship("Customer", back_populates="ledgers")
    created_by = relationship("User")
    payment_ledger_entries = relationship("PaymentLedgerEntry", back_populates="ledger_entry")


class PaymentLedgerEntry(Base):
    __tablename__ = "payment_ledger_entry"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    ledger_entry_id = Column(Integer, ForeignKey("ledger_entries.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    payment = relationship("Payment", back_populates="payment_ledger_entries")
    ledger_entry = relationship("LedgerEntry", back_populates="payment_ledger_entries")