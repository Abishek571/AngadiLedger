from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal
from app.services.ledger_services import business_access_required, business_customer_access_required, business_ledger_access_required, get_customer_balance, get_customer_balance_excluding_entry
from app.db.models.customer import Customer
from app.db.models.user import User
from app.db.models.ledger_entry import LedgerEntry
from app.deps import get_db
from app.db.schemas.ledger_entry import LedgerEntryCreate, LedgerEntryRead
from app.services.auth import cashier_or_owner_required
from app.db.schemas.ledger_entry import LedgerEntryUpdate, LedgerEntryRead
from app.db.models.business import Business
router = APIRouter()

@router.post("/ledger/", response_model=LedgerEntryRead)
async def create_ledger_entry(
    entry: LedgerEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):
    
    balance = await get_customer_balance(entry.customer_id, db)

    if entry.entry_type == "debit":
        if balance == 0:
            if entry.amount > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot debit: customer has no available credit."
                )
        elif entry.amount > balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available credit: {balance}"
            )

    new_entry = LedgerEntry(
        customer_id=entry.customer_id,
        business_id=current_user.business_id,
        entry_type=entry.entry_type,
        amount=entry.amount,
        description=entry.description,
        image_url=entry.image_url,
        created_by_id=current_user.id
    )
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return LedgerEntryRead(
        id=new_entry.id,
        customer_id=new_entry.customer_id,
        business_id=new_entry.business_id,
        entry_type=new_entry.entry_type,
        amount=new_entry.amount,
        description=new_entry.description,
        image_url=new_entry.image_url,
        created_by_id=new_entry.created_by_id,
        created_at=new_entry.created_at
    )

@router.delete("/ledger/{ledger_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ledger_entry(
    ledger_entry: LedgerEntry = Depends(business_ledger_access_required),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(ledger_entry)
    await db.commit()
    return


@router.put("/ledger/{ledger_entry_id}", response_model=LedgerEntryRead)
async def update_ledger_entry(
    ledger_entry_id: int,
    entry_update: LedgerEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(cashier_or_owner_required)
):
    result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.id == ledger_entry_id)
    )
    ledger_entry = result.scalars().first()
    if not ledger_entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found.")

    balance = await get_customer_balance_excluding_entry(
        ledger_entry.customer_id, ledger_entry.id, db
    )

    new_entry_type = entry_update.entry_type or ledger_entry.entry_type
    new_amount = entry_update.amount or ledger_entry.amount

    if new_entry_type == "credit":
        new_balance = balance + new_amount
    else:
        new_balance = balance - new_amount

    if new_entry_type == "debit" and new_balance < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available credit: {balance}"
        )

    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ledger_entry, field, value)
    await db.commit()
    await db.refresh(ledger_entry)
    return LedgerEntryRead(
        id=ledger_entry.id,
        customer_id=ledger_entry.customer_id,
        business_id=ledger_entry.business_id,
        entry_type=ledger_entry.entry_type,
        amount=ledger_entry.amount,
        description=ledger_entry.description,
        image_url=ledger_entry.image_url,
        created_by_id=ledger_entry.created_by_id,
        created_at=ledger_entry.created_at
    )

@router.get("/ledger/{ledger_entry_id}", response_model=LedgerEntryRead)
async def get_ledger_entry(
    ledger_entry: LedgerEntry = Depends(business_ledger_access_required)
):
    return LedgerEntryRead(
        id=ledger_entry.id,
        customer_id=ledger_entry.customer_id,
        business_id=ledger_entry.business_id,
        entry_type=ledger_entry.entry_type,
        amount=ledger_entry.amount,
        description=ledger_entry.description,
        image_url=ledger_entry.image_url,
        created_by_id=ledger_entry.created_by_id,
        created_at=ledger_entry.created_at
    )

@router.get("/customers/{customer_id}/ledgers/", response_model=list[LedgerEntryRead])
async def list_customer_ledgers(
    customer: Customer = Depends(business_customer_access_required),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.customer_id == customer.id)
    )
    ledgers = result.scalars().all()
    return [
        LedgerEntryRead(
            id=le.id,
            customer_id=le.customer_id,
            business_id=le.business_id,
            entry_type=le.entry_type,
            amount=le.amount,
            description=le.description,
            image_url=le.image_url,
            created_by_id=le.created_by_id,
            created_at=le.created_at
        )
        for le in ledgers
    ]

@router.get("/businesses/{business_id}/ledgers/", response_model=list[LedgerEntryRead])
async def list_business_ledgers(
    business: Business = Depends(business_access_required),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.business_id == business.id)
    )
    ledgers = result.scalars().all()
    return [
        LedgerEntryRead(
            id=le.id,
            customer_id=le.customer_id,
            business_id=le.business_id,
            entry_type=le.entry_type,
            amount=le.amount,
            description=le.description,
            image_url=le.image_url,
            created_by_id=le.created_by_id,
            created_at=le.created_at
        )
        for le in ledgers
    ]