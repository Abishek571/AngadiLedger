from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

class LedgerEntryBase(BaseModel):
    entry_type: str 
    amount: Decimal
    description: Optional[str] = None
    image_url: Optional[str] = None

class LedgerEntryCreate(LedgerEntryBase):
    customer_id: int
    
class LedgerEntryRead(LedgerEntryBase):
    id: int
    customer_id: int
    business_id: int
    created_by_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class LedgerEntryUpdate(BaseModel):
    entry_type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CustomerPayableLedger(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: str
    total_payable: Decimal
    ledgers: List[LedgerEntryRead]

    class Config:
        from_attributes = True