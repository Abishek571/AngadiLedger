from fastapi import APIRouter
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check():
    health = {"database": "unknown"}
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        health["database"] = "working"
    except Exception as e:
        health["database"] = f"not working: {str(e)}"
    return health
