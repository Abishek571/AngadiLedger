from decimal import Decimal
from typing import List, Dict, Any
from app.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.customer import Customer
from fastapi import HTTPException
from app.db.schemas.ledger_entry import CustomerPayableLedger, LedgerEntryRead
from app.db.models.ledger_entry import LedgerEntry

async def get_business_payables_service(business_id: int, db: AsyncSession) -> Dict[str, Any]:
    try:
        customer_result = await db.execute(
            select(Customer).where(Customer.business_id == business_id)
        )
        customers = customer_result.scalars().all()
        if not customers:
            logger.warning(f"No customers found for business {business_id}")
            return {"total_business_payable": Decimal("0.00"), "customers": []}

        payables_summary = []
        total_business_payable = Decimal("0.00")

        for customer in customers:
            ledger_result = await db.execute(
                select(LedgerEntry).where(
                    LedgerEntry.business_id == business_id,
                    LedgerEntry.customer_id == customer.id,
                    LedgerEntry.entry_type == "credit"
                )
            )
            ledgers = ledger_result.scalars().all()
            total_payable = sum([le.amount for le in ledgers]) if ledgers else Decimal("0.00")
            total_business_payable += total_payable

            ledger_reads = [
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

            payables_summary.append(CustomerPayableLedger(
                customer_id=customer.id,
                customer_name=customer.name,
                customer_email=customer.email,
                total_payable=total_payable,
                ledgers=ledger_reads
            ))

            logger.info(f"Processed payables for customer {customer.id} ({customer.name})")

        logger.info(f"Successfully fetched payables for business {business_id}")

        return {
            "total_business_payable": total_business_payable,
            "customers": payables_summary
        }

    except Exception as e:
        logger.error(f"Error in get_business_payables_service for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching payables.")
    


async def get_business_receivables_service(business_id: int, db: AsyncSession) -> Dict[str, Any]:
    try:
        customer_result = await db.execute(
            select(Customer).where(Customer.business_id == business_id)
        )
        customers = customer_result.scalars().all()
        if not customers:
            logger.warning(f"No customers found for business {business_id}")
            return {"total_business_receivable": Decimal("0.00"), "customers": []}

        receivables_summary = []
        total_business_receivable = Decimal("0.00")

        for customer in customers:
            ledger_result = await db.execute(
                select(LedgerEntry).where(
                    LedgerEntry.business_id == business_id,
                    LedgerEntry.customer_id == customer.id,
                    LedgerEntry.entry_type == "debit"
                )
            )
            ledgers = ledger_result.scalars().all()
            total_receivable = sum([le.amount for le in ledgers]) if ledgers else Decimal("0.00")
            total_business_receivable += total_receivable

            ledger_reads = [
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

            receivables_summary.append(CustomerPayableLedger(
                customer_id=customer.id,
                customer_name=customer.name,
                customer_email=customer.email,
                total_payable=total_receivable,
                ledgers=ledger_reads
            ))

            logger.info(f"Processed receivables for customer {customer.id} ({customer.name})")

        logger.info(f"Successfully fetched receivables for business {business_id}")

        return {
            "total_business_receivable": total_business_receivable,
            "customers": receivables_summary
        }

    except Exception as e:
        logger.error(f"Error in get_business_receivables_service for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching receivables.")

async def get_customers_with_multiple_entries(business_id: int, db: AsyncSession) -> Dict[str, Any]:
    try:
        customer_result = await db.execute(
            select(Customer).where(Customer.business_id == business_id)
        )
        customers = customer_result.scalars().all()
        if not customers:
            logger.warning(f"No customers found for business {business_id}")
            return {"customers_with_multiple_entries": []}

        customers_with_multiple_entries = []

        for customer in customers:
            ledger_result = await db.execute(
                select(LedgerEntry).where(
                    LedgerEntry.business_id == business_id,
                    LedgerEntry.customer_id == customer.id
                )
            )
            ledgers = ledger_result.scalars().all()

            if len(ledgers) > 2:
                total_amount = sum([le.amount for le in ledgers]) if ledgers else Decimal("0.00")
                ledger_reads = [
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

                customers_with_multiple_entries.append(CustomerPayableLedger(
                    customer_id=customer.id,
                    customer_name=customer.name,
                    customer_email=customer.email,
                    total_payable=total_amount,
                    ledgers=ledger_reads
                ))

                logger.info(f"Customer {customer.id} ({customer.name}) has {len(ledgers)} entries.")

        logger.info(f"Fetched {len(customers_with_multiple_entries)} customers with more than 2 entries for business {business_id}.")

        return {"customers_with_multiple_entries": customers_with_multiple_entries}

    except Exception as e:
        logger.error(f"Error in get_customers_with_multiple_entries for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching customers with multiple entries.")