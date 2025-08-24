from datetime import datetime
import decimal
from typing import Optional
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.customer import Customer
from app.db.models.payment import Payment
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.ledger_entry import LedgerEntry,PaymentLedgerEntry
from app.db.schemas.payment import PaymentCreateRequest, PaymentAllocation
import aiosmtplib
from email.message import EmailMessage

async def get_payments_from_ledger_entries(db: AsyncSession, customer_id: int):
    stmt = select(LedgerEntry).where(
        LedgerEntry.customer_id == customer_id,
        LedgerEntry.entry_type == "debit"
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    payments = []
    for entry in entries:
        payments.append({
            "ledger_entry_id": entry.id,
            "customer_id": entry.customer_id,
            "business_id": entry.business_id,
            "amount": entry.amount,
            "status": "paid",  
            "description": entry.description,
            "image_url": entry.image_url,
            "created_at": entry.created_at,
            "paid_at": None
        })
    return payments

async def get_partial_settlements(current_user, db: AsyncSession):
    stmt = (
        select(
            Customer.id,
            Customer.name,
            func.coalesce(
                func.sum(
                    case(
                        (LedgerEntry.entry_type == "credit", LedgerEntry.amount),
                        else_=-LedgerEntry.amount
                    )
                ), 0
            ).label("balance")
        )
        .join(LedgerEntry, LedgerEntry.customer_id == Customer.id)
        .where(Customer.business_id == current_user.business_id)
        .group_by(Customer.id)
    )

    result = await db.execute(stmt)
    rows = result.all()

    settlements = []
    for row in rows:
        status = "paid" if row.balance == 0 else "pending"
        if status == "pending":
            settlements.append({
                "customer_id": row.id,
                "customer_name": row.name,
                "balance": float(row.balance),
                "status": status
            })
    return settlements

async def get_outstanding_balances(current_user, db: AsyncSession, threshold: float = 10000.0):
    stmt = (
        select(
            Customer.id,
            Customer.name,
            Customer.email,
            Customer.phone_number,
            func.coalesce(
                func.sum(
                    case(
                        (LedgerEntry.entry_type == "credit", LedgerEntry.amount),
                        else_=-LedgerEntry.amount
                    )
                ), 0
            ).label("balance")
        )
        .join(LedgerEntry, LedgerEntry.customer_id == Customer.id)
        .where(Customer.business_id == current_user.business_id)
        .group_by(Customer.id)
        .having(
            func.coalesce(
                func.sum(
                    case(
                        (LedgerEntry.entry_type == "credit", LedgerEntry.amount),
                        else_=-LedgerEntry.amount
                    )
                ), 0
            ) > threshold
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "customer_id": row.id,
            "customer_name": row.name,
            "email": row.email,
            "contact": row.phone_number,
            "outstanding_balance": float(row.balance)
        }
        for row in rows
    ]

async def send_email_reminder(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = "abishekuvs@gmail.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        username="abishekuvs@gmail.com",
        password="aqlyeeipytbbhune",
        start_tls=True,
    )
