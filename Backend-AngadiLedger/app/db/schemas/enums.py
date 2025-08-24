from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    owner = "owner"
    staff = "staff"

class StaffRoleEnum(str, Enum):
    supervisor = "supervisor"
    cashier = "cashier"
    delivery_man = "delivery_man"
