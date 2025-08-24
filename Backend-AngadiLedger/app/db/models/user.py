from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from .enums import RoleEnum, StaffRoleEnum


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True)
    business = relationship("Business", back_populates="users")
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    invited_by = relationship("User", remote_side=[id])
    roles = relationship("UserRole", back_populates="user")
    assigned_as_staff = relationship("StaffAssignment", foreign_keys="[StaffAssignment.staff_id]", back_populates="staff")
    assigned_staff = relationship("StaffAssignment", foreign_keys="[StaffAssignment.owner_id]", back_populates="owner")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)

    users = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)

class StaffAssignment(Base):
    __tablename__ = "staff_assignments"
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_role = Column(Enum(StaffRoleEnum), nullable=False)

    staff = relationship("User", foreign_keys=[staff_id], back_populates="assigned_as_staff")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="assigned_staff")
