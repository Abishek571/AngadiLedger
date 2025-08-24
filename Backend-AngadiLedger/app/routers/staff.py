import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User, Role, UserRole, StaffAssignment
from app.db.schemas.user import StaffCreate, RoleRead, StaffListItem, StaffUpdate, UserRead
from app.db.models.business import Business
from app.services.auth import owner_required, get_password_hash
from app.services.otp import generate_otp
from app.deps import get_db

router = APIRouter()

LOG_DIR = "logs"
LOG_FILE = "owner_staff.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

logger = logging.getLogger("owner_staff_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_path)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
file_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(file_handler)

@router.post("/owner/add", response_model=UserRead)
async def add_staff(
    staff: StaffCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(owner_required)
):
    try:
        if staff.assigned_role not in ["supervisor", "cashier", "salesman"]:
            logger.warning("Invalid staff role attempted (role redacted)")
            raise HTTPException(status_code=400, detail="Invalid staff role.")

        result = await db.execute(
            select(User).where(User.email == staff.email)
        )
        existing_user = result.scalars().first()
        if existing_user:
            logger.warning("Attempt to add staff with existing email (redacted)")
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        hashed_password = get_password_hash(staff.password)
        new_user = User(
            email=staff.email,
            hashed_password=hashed_password,
            role="staff",
            is_active=True,
            business_id=current_user.business_id,
            is_verified=True,
            phone_number=staff.phone_number,
            invited_by_id=current_user.id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"Staff user created: user_id={new_user.id} by owner user_id={current_user.id}")

        result = await db.execute(
            select(Role).where(Role.name == "staff")
        )
        staff_role_obj = result.scalars().first()
        if not staff_role_obj:
            logger.error("Role 'staff' not found in database.")
            raise HTTPException(status_code=400, detail="Role 'staff' not found.")

        user_role = UserRole(user_id=new_user.id, role_id=staff_role_obj.id)
        db.add(user_role)
        await db.commit()

        staff_assignment = StaffAssignment(
            staff_id=new_user.id,
            owner_id=current_user.id,
            assigned_role=staff.assigned_role
        )
        db.add(staff_assignment)
        await db.commit()
        logger.info(f"Staff assignment created for user_id={new_user.id} as assigned_role (redacted)")

        return UserRead(
            id=new_user.id,
            email=new_user.email,
            is_verified=new_user.is_verified,
            roles=[RoleRead(id=staff_role_obj.id, name=staff_role_obj.name)],
            phone_number=new_user.phone_number,
            business_name=None
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException in add_staff: {http_exc.detail}")
        raise
    except Exception as exc:
        logger.exception("Unexpected error in add_staff")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/owner/all", response_model=list[StaffListItem])
async def get_owner_staffs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(owner_required)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")

    business_name = None
    if current_user.business_id:
        result = await db.execute(
            select(Business).where(Business.id == current_user.business_id)
        )
        business = result.scalars().first()
        if business:
            business_name = business.name

    result = await db.execute(
        select(User).where(
            User.role == "staff",
            User.business_id == current_user.business_id
        )
    )
    staffs = result.scalars().all()

    staff_list = []
    for staff in staffs:
        assigned_role = None
        assignment_result = await db.execute(
            select(StaffAssignment).where(StaffAssignment.staff_id == staff.id)
        )
        assignment = assignment_result.scalars().first()
        if assignment:
            assigned_role = assignment.assigned_role

        staff_list.append(
            StaffListItem(
                id=staff.id,
                email=staff.email,
                phone_number=staff.phone_number,
                role=staff.role,
                assigned_role=assigned_role,
                business_name=business_name
            )
        )
    return staff_list


@router.delete("/owner/delete/{staff_id}", status_code=204)
async def delete_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(owner_required)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(User).where(
            User.id == staff_id,
            User.role == "staff",
            User.business_id == current_user.business_id
        )
    )
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found or not part of your business")

    assignment_result = await db.execute(
        select(StaffAssignment).where(StaffAssignment.staff_id == staff.id)
    )
    assignment = assignment_result.scalars().first()
    if assignment:
        await db.delete(assignment)

    await db.delete(staff)
    await db.commit()
    return


@router.put("/owner/update/{staff_id}")
async def update_staff(
    staff_id: int,
    update: StaffUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(owner_required)
):

    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(User).where(
            User.id == staff_id,
            User.role == "staff",
            User.business_id == current_user.business_id
        )
    )
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found or not part of your business")

    if update.phone_number is not None:
        staff.phone_number = update.phone_number

    if update.assigned_role is not None:
        assignment_result = await db.execute(
            select(StaffAssignment).where(StaffAssignment.staff_id == staff.id)
        )
        assignment = assignment_result.scalars().first()
        if assignment:
            assignment.assigned_role = update.assigned_role
            db.add(assignment)
        else:
            new_assignment = StaffAssignment(
                staff_id=staff.id,
                assigned_role=update.assigned_role
            )
            db.add(new_assignment)

    db.add(staff)
    await db.commit()
    await db.refresh(staff)

    return {"detail": "Staff updated successfully"}

@router.get("/owner/staffs/{staff_id}", response_model=StaffListItem)
async def get_staff_detail(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(owner_required)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(User).where(
            User.id == staff_id,
            User.role == "staff",
            User.business_id == current_user.business_id
        )
    )
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found or not part of your business")

    assigned_role = None
    assignment_result = await db.execute(
        select(StaffAssignment).where(StaffAssignment.staff_id == staff.id)
    )
    assignment = assignment_result.scalars().first()
    if assignment:
        assigned_role = assignment.assigned_role

    business_name = None
    if staff.business_id:
        business_result = await db.execute(
            select(Business).where(Business.id == staff.business_id)
        )
        business = business_result.scalars().first()
        if business:
            business_name = business.name

    return StaffListItem(
        id=staff.id,
        email=staff.email,
        phone_number=staff.phone_number,
        role=staff.role,
        assigned_role=assigned_role,
        business_name=business_name
    )