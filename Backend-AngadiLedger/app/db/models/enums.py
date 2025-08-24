import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    owner = "owner"
    staff = "staff"

class StaffRoleEnum(str, enum.Enum):
    supervisor = "supervisor"
    cashier = "cashier"
    salesman = "salesman"
