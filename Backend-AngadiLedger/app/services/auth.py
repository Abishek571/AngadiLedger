import logging
import os
import sys
from sqlalchemy.orm import selectinload
from fastapi import Depends, HTTPException, logger,status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError
import jwt
from passlib.context import CryptContext
from datetime import datetime,timezone,timedelta
from sqlalchemy import select
from app.deps import get_db
from pytest import Session
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from dotenv import load_dotenv
from app.db.models.user import StaffAssignment, User
from sqlalchemy.ext.asyncio import AsyncSession


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        user_role = payload.get("role")
        if user_email is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        result = await db.execute(select(User).options(selectinload(User.roles)).where(User.email == user_email))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def admin_required(current_user: User = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def owner_required(current_user: User = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner privileges required")
    return current_user

async def cashier_or_owner_required(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if getattr(current_user, "role", None) == "owner":
        return current_user
    
    if getattr(current_user, "role", None) == "staff":
        result = await db.execute(
            select(StaffAssignment).where(
                StaffAssignment.staff_id == current_user.id,
                StaffAssignment.assigned_role == "cashier"
            )
        )
        staff_assignment = result.scalars().first()
        if staff_assignment:
            return current_user
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only owners or cashiers can perform this action."
    )

async def supervisor_or_owner_required(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if getattr(current_user, "role", None) == "owner":
        return current_user
    
    if getattr(current_user, "role", None) == "staff":
        result = await db.execute(
            select(StaffAssignment).where(
                StaffAssignment.staff_id == current_user.id,
                StaffAssignment.assigned_role == "supervisor"
            )
        )
        staff_assignment = result.scalars().first()
        if staff_assignment:
            return current_user
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only owners or cashiers can perform this action."
    )