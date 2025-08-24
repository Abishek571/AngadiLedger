from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional

from sqlalchemy import Enum
from .enums import RoleEnum, StaffRoleEnum

class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str  
    business_name: str
    phone_number: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    roles: List[RoleRead]
    phone_number: Optional[str] = None
    business_name: Optional[str] = None

    class Config:
        from_attributes = True

class UserVerifyOTP(BaseModel):
    email: EmailStr
    otp_code: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class StaffCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    assigned_role: StaffRoleEnum


class UserProfileRead(BaseModel):
    id: int
    email: str
    phone_number: Optional[str]
    is_verified: bool
    role: str
    business_name: Optional[str] = None
    assigned_role: Optional[StaffRoleEnum] = None
    roles: Optional[List[str]] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    phone_number: Optional[str] = None

class OwnerUserRead(BaseModel):
    id: int
    email: str
    phone_number: Optional[str]
    is_verified: bool
    business_name: Optional[str] = None

    class Config:
        from_attributes = True

class PersonalDetail(BaseModel):
    email: str
    phone_number: Optional[str]

class BusinessDetail(BaseModel):
    email: str
    business_name: Optional[str] = None
    assigned_role: Optional[StaffRoleEnum] = None

class UserProfileView(BaseModel):
    personal: PersonalDetail
    business: BusinessDetail

class StaffListItem(BaseModel):
    id:int
    email: str
    phone_number: Optional[str]
    role: str
    assigned_role: Optional[str]
    business_name: Optional[str]

class StaffUpdate(BaseModel):
    phone_number: Optional[str]
    assigned_role: Optional[str]