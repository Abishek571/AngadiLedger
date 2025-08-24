import random
from datetime import datetime, timedelta,timezone
from sqlalchemy.orm import Session
from app.db.models.user import User

def generate_otp():
    return str(random.randint(100000, 999999))

def set_user_otp(db: Session, user: User):
    otp_code = generate_otp()
    user.otp_code = otp_code
    user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()
    db.refresh(user)
    return otp_code

def verify_user_otp(db: Session, user: User, otp_code: str):
    if user.otp_code != otp_code:
        return False
    if user.otp_expiry < datetime.utcnow():
        return False
    user.is_verified = True
    user.otp_code = None
    user.otp_expiry = None
    db.commit()
    return True
