import datetime
from typing import Optional

from pydantic import BaseModel


class ActivityLogBase(BaseModel):
    action: str
    details: Optional[str] = None

class ActivityLogCreate(ActivityLogBase):
    user_id: Optional[int] = None
    business_id: Optional[int] = None

class ActivityLogRead(ActivityLogBase):
    id: int
    user_id: Optional[int]
    business_id: Optional[int]
    timestamp: datetime
    class Config:
        from_attributes = True
