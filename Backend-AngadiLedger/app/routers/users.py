import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from app.db.schemas.user import RoleRead, UserCreate, UserLogin, UserRead, UserVerifyOTP
from app.db.models.user import Role, User, UserRole
from app.deps import get_db
from app.services.auth import create_access_token, get_password_hash
from app.services.auth import verify_password
from app.services.otp import generate_otp
from app.db.models.business import Business
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

LOG_DIR = "logs"
LOG_FILE = "user_auth.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

logger = logging.getLogger("user_auth_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_path)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
file_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(file_handler)

@router.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == user_in.email))
        db_user = result.scalars().first()
        if db_user:
            logger.warning("Registration attempt with already registered email (redacted)")
            raise HTTPException(status_code=400, detail="Email already registered")

        business = None
        business_id = None

        if user_in.role == "owner":
            result = await db.execute(select(Business).where(Business.name == user_in.business_name))
            business = result.scalars().first()
            if not business:
                business = Business(name=user_in.business_name)
                db.add(business)
                await db.commit()
                await db.refresh(business)
                logger.info("Business created during registration (name redacted)")
            business_id = business.id

        otp_code = generate_otp()

        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            business_id=business_id,
            phone_number=user_in.phone_number,
            otp_code=otp_code,
            is_verified=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User registered: user_id={user.id}")

        result = await db.execute(select(Role).where(Role.name == user_in.role))
        role = result.scalars().first()
        if not role:
            role = Role(name=user_in.role)
            db.add(role)
            await db.commit()
            await db.refresh(role)
            logger.info(f"Role created: role_id={role.id}")
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        await db.commit()

        return UserRead(
            id=user.id,
            email=user.email,
            is_verified=user.is_verified,
            roles=[RoleRead(id=role.id, name=role.name)],
            phone_number=user.phone_number,
            business_name=business.name if business else None
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException in register_user: {http_exc.detail}")
        raise
    except Exception as exc:
        logger.exception("Unexpected error in register_user")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/verify-otp", response_model=UserRead)
async def verify_otp(otp_data: UserVerifyOTP, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == otp_data.email))
        user = result.scalars().first()
        if not user:
            logger.warning("OTP verification attempt for non-existent user (email redacted)")
            raise HTTPException(status_code=404, detail="User not found")

        if user.otp_code != otp_data.otp_code:
            logger.warning(f"Invalid OTP attempt for user_id={user.id}")
            raise HTTPException(status_code=400, detail="Invalid OTP")

        user.is_verified = True
        user.otp_code = None
        await db.commit()
        await db.refresh(user)
        logger.info(f"User verified via OTP: user_id={user.id}")

        result = await db.execute(
            select(Role).join(UserRole).where(UserRole.user_id == user.id)
        )
        roles = result.scalars().all()

        return UserRead(
            id=user.id,
            email=user.email,
            is_verified=user.is_verified,
            roles=[RoleRead(id=role.id, name=role.name) for role in roles]
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException in verify_otp: {http_exc.detail}")
        raise
    except Exception as exc:
        logger.exception("Unexpected error in verify_otp")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(request: Request,user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug("Starting login DB query")
        result = await db.execute(select(User).where(User.email == user_in.email))
        logger.debug("Fetching user from DB result")
        user = result.scalars().first()
        if not user:
            logger.warning("Login attempt with invalid credentials (email redacted)")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(user_in.password, user.hashed_password):
            logger.warning(f"Login attempt with invalid password for user_id={user.id}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_verified:
            logger.warning(f"Unverified user login attempt: user_id={user.id}")
            raise HTTPException(status_code=403, detail="User not verified")

        role = user.role
        token_data = {"sub": user.email, "role": role}
        logger.debug("Creating access token")
        access_token = create_access_token(token_data)
        logger.info(f"User logged in: user_id={user.id}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": role,
                "business_id": user.business_id,
                "phone_number": user.phone_number
            }
        }
    except Exception as e:
        print(f"Login error: {e}")  # Replace with proper logging in production
        raise HTTPException(status_code=500, detail=str(e))
