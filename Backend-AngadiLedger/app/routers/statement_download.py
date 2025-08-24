from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.services.payment_service import get_outstanding_balances, get_partial_settlements, get_payments_from_ledger_entries
from app.services.statement_services import list_of_dicts_to_csv
from app.services.auth import cashier_or_owner_required

router = APIRouter()

@router.get("/customers/{customer_id}/payments-from-ledger/download-csv/")
async def download_payments_csv(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(cashier_or_owner_required)

):
    payments = await get_payments_from_ledger_entries(db, customer_id)
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found for this customer.")
    csv_file = list_of_dicts_to_csv(payments)
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=payments_customer_{customer_id}.csv"}
    )

@router.get("/customers/partial-settlements/download-csv/")
async def download_partial_settlements_csv(
    db: AsyncSession = Depends(get_db),
    user=Depends(cashier_or_owner_required)
):
    settlements = await get_partial_settlements(user,db)
    if not settlements:
        raise HTTPException(status_code=404, detail="No partial settlements found.")
    csv_file = list_of_dicts_to_csv(settlements)
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=partial_settlements.csv"}
    )


@router.get("/customers/outstanding-balances/download-csv/")
async def download_outstanding_balances_csv(
    db: AsyncSession = Depends(get_db),
    user=Depends(cashier_or_owner_required)
):
    balances = await get_outstanding_balances(user,db, threshold=10000.0)
    if not balances:
        raise HTTPException(status_code=404, detail="No outstanding balances found.")
    csv_file = list_of_dicts_to_csv(balances)
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=outstanding_balances.csv"}
    )