from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PaymentAllocation(BaseModel):
    ledger_entry_id: int
    amount: float

class PaymentCreateRequest(BaseModel):
    customer_id: int
    business_id: int
    amount: float
    status: str
    paid_at: Optional[datetime] = None
    created_by_id: int
    allocations: List[PaymentAllocation]

class PaymentResponse(BaseModel):
    id: int
    customer_id: int
    business_id: int
    amount: float
    status: str
    paid_at: Optional[datetime]
    created_by_id: int
    allocations: List[PaymentAllocation]

    class Config:
        from_attributes = True


class PaymentFromLedgerEntry(BaseModel):
    ledger_entry_id: int
    customer_id: int
    business_id: int
    amount: Decimal
    status: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None 

    class Config:
        from_attributes = True