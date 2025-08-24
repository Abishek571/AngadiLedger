from pydantic import BaseModel
from typing import Optional, List

class BusinessBase(BaseModel):
    name: str

class BusinessCreate(BusinessBase):
    pass

class BusinessRead(BusinessBase):
    id: int
    class Config:
        from_attributes = True
