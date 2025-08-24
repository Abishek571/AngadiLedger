from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.ledger_entry import LedgerEntry
from app.db.models.user import User
from app.db.models.customer import Customer
from app.deps import get_db
from app.services.auth import cashier_or_owner_required
from app.db.models.business import Business

async def business_ledger_access_required(
    ledger_entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):
    result = await db.execute(select(LedgerEntry).where(LedgerEntry.id == ledger_entry_id))
    ledger_entry = result.scalars().first()
    if not ledger_entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found.")

    if ledger_entry.business_id != current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ledger entry."
        )
    return ledger_entry


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

async def business_access_required(
    business_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found.")
    if business.id != current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this business."
        )
    return business

async def get_customer_balance(customer_id: int, db: AsyncSession):
    result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.customer_id == customer_id)
    )
    ledger_entries = result.scalars().all()
    balance = sum(
        le.amount if le.entry_type == "credit" else -le.amount
        for le in ledger_entries
    )
    return balance

async def get_customer_balance_excluding_entry(customer_id: int, exclude_entry_id: int, db: AsyncSession):
    result = await db.execute(
        select(LedgerEntry)
        .where(
            LedgerEntry.customer_id == customer_id,
            LedgerEntry.id != exclude_entry_id
        )
    )
    ledger_entries = result.scalars().all()
    balance = sum(
        le.amount if le.entry_type == "credit" else -le.amount
        for le in ledger_entries
    )
    return balance