import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.db.models.user import User, Role, UserRole
from app.db.models.business import Business
from app.db.schemas.user import OwnerUserRead, RoleRead, UserCreate, UserRead
from app.services.auth import admin_required, get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db

router = APIRouter()

LOG_DIR = "logs"
LOG_FILE = "admin_owner.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

logger = logging.getLogger("admin_owner_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_path)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
file_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(file_handler)

@router.post("/admin/owners", response_model=UserRead)
async def add_owner(
    owner_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    try:
        result = await db.execute(select(User).where(User.email == owner_in.email))
        db_user = result.scalars().first()
        if db_user:
            logger.warning("Attempt to register already existing email (redacted)")
            raise HTTPException(status_code=400, detail="Email already registered")

        result = await db.execute(select(Business).where(Business.name == owner_in.business_name))
        business = result.scalars().first()
        if not business:
            business = Business(name=owner_in.business_name)
            db.add(business)
            await db.commit()
            await db.refresh(business)
            logger.info("Business created: business_id={}".format(business.id))

        user = User(
            email=owner_in.email,
            hashed_password=get_password_hash(owner_in.password),
            role="owner",
            business_id=business.id,
            phone_number=owner_in.phone_number,
            is_verified=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Owner created: user_id={user.id} for business_id={business.id}")

        result = await db.execute(select(Role).where(Role.name == "owner"))
        role = result.scalars().first()
        if not role:
            role = Role(name="owner")
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
            business_name=business.name
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException in add_owner: {http_exc.detail}")
        raise
    except Exception as exc:
        logger.exception("Unexpected error in add_owner")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/admin/owners/{owner_id}")
async def delete_owner(
    owner_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    try:
        result = await db.execute(select(User).where(User.id == owner_id, User.role == "owner"))
        owner = result.scalars().first()
        if not owner:
            logger.warning(f"Attempt to delete non-existent owner with ID: {owner_id}")
            raise HTTPException(status_code=404, detail="Owner not found")
        await db.delete(owner)
        await db.commit()
        logger.info(f"Owner deleted: user_id={owner_id}")
        return {"detail": "Owner deleted successfully"}
    except HTTPException as http_exc:
        logger.error(f"HTTPException in delete_owner: {http_exc.detail}")
        raise
    except Exception as exc:
        logger.exception("Unexpected error in delete_owner")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/owners", response_model=list[OwnerUserRead])
async def get_all_owners(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(User).where(User.role == "owner")
    )
    owners = result.scalars().all()

    owner_list = []
    for owner in owners:
        business_name = None
        if owner.business_id:
            business_result = await db.execute(
                select(Business).where(Business.id == owner.business_id)
            )
            business = business_result.scalars().first()
            if business:
                business_name = business.name
        owner_list.append(
            OwnerUserRead(
                id=owner.id,
                email=owner.email,
                phone_number=owner.phone_number,
                is_verified=owner.is_verified,
                business_name=business_name
            )
        )
    return owner_list
