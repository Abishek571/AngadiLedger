from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.customer import Customer
from app.db.models.user import User
from app.deps import get_db
from app.services.auth import cashier_or_owner_required

async def business_customer_access_required(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):

    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    if customer.business_id != current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this customer."
        )
    return customer
