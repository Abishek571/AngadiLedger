from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import health, users, staff,admin,customer,ledger_entry,profile,payments,statement_download,analytics
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.include_router(health.router)
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(profile.router,prefix="",tags=["profile"])
app.include_router(admin.router,prefix="/admin", tags=["admin"])
app.include_router(staff.router, prefix="/staff", tags=["staff"])
app.include_router(customer.router,prefix="",tags=["customer"])
app.include_router(ledger_entry.router,prefix="",tags=["ledger"])
app.include_router(payments.router,prefix="/payments",tags=["payment"])
app.include_router(statement_download.router,prefix="/download",tags=["statements"])
app.include_router(analytics.router,prefix="",tags=["analytics"])

origins = [
    "http://localhost:4200", 

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,          
    allow_methods=["*"],  
    allow_headers=["*"],            

)