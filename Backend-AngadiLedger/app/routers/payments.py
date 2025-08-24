from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.schemas.payment import PaymentCreateRequest, PaymentFromLedgerEntry, PaymentResponse
from app.deps import get_db
from app.services.payment_service import get_outstanding_balances, get_partial_settlements, get_payments_from_ledger_entries, send_email_reminder
from app.db.models.user import User
from app.services.auth import cashier_or_owner_required
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/customers/{customer_id}/payments-from-ledger/", response_model=List[PaymentFromLedgerEntry])
async def get_payments_for_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(cashier_or_owner_required)
):
    payments = await get_payments_from_ledger_entries(db, customer_id)
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found for this customer.")
    return payments

@router.get("/customers/partial-settlements/", response_model=list[dict])
async def partial_settlement_endpoint(
    db: AsyncSession = Depends(get_db),
    user=Depends(cashier_or_owner_required)
):
    return await get_partial_settlements(user,db)

@router.get("/customers/outstanding-balances/", response_model=list[dict])
async def outstanding_balance_endpoint(
    db: AsyncSession = Depends(get_db),
    user=Depends(cashier_or_owner_required)
):
    return await get_outstanding_balances(user,db, threshold=10000.0)

@router.post("/customers/outstanding-balances/send-reminders/")
async def send_outstanding_balance_reminders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(cashier_or_owner_required)
):
    customers = await get_outstanding_balances(current_user,db, threshold=10000.0)
    if not customers:
        return {"message": "No outstanding balances found."}

    sent = []
    failed = []
    for customer in customers:
        email = customer.get("email")
        name = customer.get("customer_name")
        balance = customer.get("outstanding_balance")
        if not email:
            failed.append({"customer": name, "reason": "No email address"})
            continue
        subject = "Outstanding Balance Reminder"
        body = (
            f"Dear {name},\n\n"
            f"Our records show you have an outstanding balance of ${balance:.2f}.\n"
            "Please make a payment at your earliest convenience.\n\n"
            "Thank you."
        )
        try:
            await send_email_reminder(email, subject, body)
            sent.append(email)
        except Exception as e:
            failed.append({"customer": name, "reason": str(e)})

    return {"sent": sent, "failed": failed}


