from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.services.analytics_service import get_business_payables_service,get_business_receivables_service,get_customers_with_multiple_entries
from app.services.auth import supervisor_or_owner_required

router = APIRouter()

@router.get("/analytics/customer/payables/")
async def get_customer_payables(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(supervisor_or_owner_required)
):
    return await get_business_payables_service(current_user.business_id,db)


@router.get("/analytics/customer/receivables/")
async def get_customer_payables(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(supervisor_or_owner_required)
):
    return await get_business_receivables_service(current_user.business_id,db)


@router.get("/analytics/customer/multipl_entries/")
async def get_customer_payables(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(supervisor_or_owner_required)
):
    return await get_customers_with_multiple_entries(current_user.business_id,db)



