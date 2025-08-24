from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.deps import get_db
from app.db.models.user import User, UserRole, Role
from app.db.models.business import Business
from app.db.models.user import StaffAssignment
from app.services.auth import get_current_user
from app.db.schemas.user import BusinessDetail, PersonalDetail, UserProfileRead, UserProfileUpdate, UserProfileView

router = APIRouter()

@router.get("/profile", response_model=UserProfileRead)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(UserRole).where(UserRole.user_id == current_user.id)
    )
    user_roles = result.scalars().all()

    role_names = []
    for ur in user_roles:
        result_role = await db.execute(
            select(Role).where(Role.id == ur.role_id)
        )
        role = result_role.scalars().first()
        if role:
            role_names.append(role.name)

    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "is_verified": current_user.is_verified,
        "role": current_user.role,
        "roles": role_names
    }

    if current_user.role == "admin":
        return UserProfileRead(**profile_data)

    elif current_user.role == "owner":
        business_name = None
        if current_user.business_id:
            result = await db.execute(
                select(Business).where(Business.id == current_user.business_id)
            )
            business = result.scalars().first()
            if business:
                business_name = business.name
        profile_data["business_name"] = business_name
        return UserProfileRead(**profile_data)

    elif current_user.role == "staff":
        business_name = None
        if current_user.business_id:
            result = await db.execute(
                select(Business).where(Business.id == current_user.business_id)
            )
            business = result.scalars().first()
            if business:
                business_name = business.name
        profile_data["business_name"] = business_name

        assigned_role = None
        result = await db.execute(
            select(StaffAssignment).where(StaffAssignment.staff_id == current_user.id)
        )
        assignment = result.scalars().first()
        if assignment:
            assigned_role = assignment.assigned_role
        profile_data["assigned_role"] = assigned_role
        return UserProfileRead(**profile_data)

    else:
        raise HTTPException(status_code=400, detail="Unknown user role.")

@router.put("/profile", response_model=UserProfileRead)
async def update_profile(
    update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.phone_number = update.phone_number

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    result = await db.execute(
        select(UserRole).where(UserRole.user_id == current_user.id)
    )
    user_roles = result.scalars().all()
    role_names = []
    for ur in user_roles:
        result_role = await db.execute(
            select(Role).where(Role.id == ur.role_id)
        )
        role = result_role.scalars().first()
        if role:
            role_names.append(role.name)

    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "is_verified": current_user.is_verified,
        "role": current_user.role,
        "roles": role_names
    }

    if current_user.role == "admin":
        return UserProfileRead(**profile_data)

    elif current_user.role == "owner":
        business_name = None
        if current_user.business_id:
            result = await db.execute(
                select(Business).where(Business.id == current_user.business_id)
            )
            business = result.scalars().first()
            if business:
                business_name = business.name
        profile_data["business_name"] = business_name
        return UserProfileRead(**profile_data)

    elif current_user.role == "staff":
        business_name = None
        if current_user.business_id:
            result = await db.execute(
                select(Business).where(Business.id == current_user.business_id)
            )
            business = result.scalars().first()
            if business:
                business_name = business.name
        profile_data["business_name"] = business_name

        assigned_role = None
        result = await db.execute(
            select(StaffAssignment).where(StaffAssignment.staff_id == current_user.id)
        )
        assignment = result.scalars().first()
        if assignment:
            assigned_role = assignment.assigned_role
        profile_data["assigned_role"] = assigned_role
        return UserProfileRead(**profile_data)

    else:
        raise HTTPException(status_code=400, detail="Unknown user role.")
    
@router.get("/profile/details", response_model=UserProfileView)
async def view_profile_details(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    personal = PersonalDetail(
        email=current_user.email,
        phone_number=current_user.phone_number
    )

    business_email = current_user.email
    business_name = None
    assigned_role = None

    if current_user.role in ("owner", "staff") and current_user.business_id:
        result = await db.execute(
            select(Business).where(Business.id == current_user.business_id)
        )
        business = result.scalars().first()
        if business:
            business_name = business.name

    if current_user.role == "staff":
        result = await db.execute(
            select(StaffAssignment).where(StaffAssignment.staff_id == current_user.id)
        )
        assignment = result.scalars().first()
        if assignment:
            assigned_role = assignment.assigned_role

    business = BusinessDetail(
        email=business_email,
        business_name=business_name,
        assigned_role=assigned_role
    )

    return UserProfileView(personal=personal, business=business)