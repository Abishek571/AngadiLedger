import datetime

from pydantic import BaseModel


class PaymentReminderBase(BaseModel):
    method: str  # "sms" or "email"
    status: str  # "sent", "failed"

class PaymentReminderCreate(PaymentReminderBase):
    payment_id: int

class PaymentReminderRead(PaymentReminderBase):
    id: int
    payment_id: int
    sent_at: datetime
    class Config:
        from_attributes = True

