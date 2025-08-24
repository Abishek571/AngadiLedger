from typing import Optional
from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    relationship_type: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    business_id: int

class CustomerRead(CustomerBase):
    id: int
    business_id: int
    created_by_id: int
    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    relationship_type: Optional[str] = None
    notes: Optional[str] = None
