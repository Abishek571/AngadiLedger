from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.customer_services import business_customer_access_required
from app.db.models.customer import Customer
from app.db.models.user import User
from app.db.models.business import Business
from app.deps import get_db
from app.db.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.auth import cashier_or_owner_required

router = APIRouter()

@router.post("/customers/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):
    result = await db.execute(
        select(Business).where(Business.id == current_user.business_id)
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found.")

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
        business_id=current_user.business_id,
        relationship_type=customer.relationship_type,
        notes=customer.notes,
        created_by_id=current_user.id
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)

    return CustomerRead(
        id=new_customer.id,
        name=new_customer.name,
        email=new_customer.email,
        phone_number=new_customer.phone_number,
        business_id=new_customer.business_id,
        relationship_type=new_customer.relationship_type,
        notes=new_customer.notes,
        created_by_id=new_customer.created_by_id
    )


@router.get("/customers/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer: Customer = Depends(business_customer_access_required)
):
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_update: CustomerUpdate,
    customer: Customer = Depends(business_customer_access_required),
    db: AsyncSession = Depends(get_db)
):
    for field, value in customer_update.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    await db.commit()
    await db.refresh(customer)
    return customer

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer: Customer = Depends(business_customer_access_required),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(customer)
    await db.commit()
    return

@router.get("/customers/", response_model=List[CustomerRead])
async def list_customers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):
    business_id = current_user.business_id

    if not business_id:
        raise HTTPException(status_code=400, detail="User is not associated with any business.")

    result = await db.execute(
        select(Customer).where(Customer.business_id == business_id)
    )
    customers = result.scalars().all()
    return customers