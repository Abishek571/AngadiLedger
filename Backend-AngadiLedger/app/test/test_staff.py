import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user import StaffCreate, UserRead, RoleRead, StaffListItem, StaffUpdate
from app.db.models.user import User

@pytest.fixture
def owner_user():
    user = Mock(spec=User)
    user.id = 1
    user.role = "owner"
    user.business_id = 1
    return user

@pytest.fixture
def non_owner_user():
    user = Mock(spec=User)
    user.id = 2
    user.role = "staff"
    user.business_id = 1
    return user

@pytest.fixture
def staff_data():
    return StaffCreate(
        email="staff@test.com",
        password="password123",
        phone_number="1234567890",
        assigned_role="cashier"        
    )

async def mock_add_staff(staff: StaffCreate, db: AsyncSession, current_user: User):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    if staff.assigned_role not in ["supervisor", "cashier", "salesman"]:
        raise HTTPException(status_code=400, detail="Invalid staff role.")
    if staff.email == "existing@test.com":
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    return UserRead(
        id=2,
        email=staff.email,
        is_verified=True,
        roles=[RoleRead(id=2, name="staff")],
        phone_number=staff.phone_number,
        business_name=None
    )

async def mock_get_owner_staffs(db: AsyncSession, current_user: User):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return [
        StaffListItem(
            id=2,
            email="staff1@test.com",
            phone_number="1234567890",
            role="staff",
            assigned_role="cashier",
            business_name="Test Business"
        ),
        StaffListItem(
            id=3,
            email="staff2@test.com",
            phone_number="0987654321",
            role="staff",
            assigned_role="supervisor",
            business_name="Test Business"
        )
    ]

async def mock_delete_staff(staff_id: int, db: AsyncSession, current_user: User):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    if staff_id == 999:
        raise HTTPException(status_code=404, detail="Staff not found or not part of your business")
    return None

async def mock_update_staff(staff_id: int, update: StaffUpdate, db: AsyncSession, current_user: User):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    if staff_id == 999:
        raise HTTPException(status_code=404, detail="Staff not found or not part of your business")
    return {"detail": "Staff updated successfully"}

async def mock_get_staff_detail(staff_id: int, db: AsyncSession, current_user: User):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not authorized")
    if staff_id == 999:
        raise HTTPException(status_code=404, detail="Staff not found or not part of your business")
    
    return StaffListItem(
        id=staff_id,
        email="staff@test.com",
        phone_number="1234567890",
        role="staff",
        assigned_role="cashier",
        business_name="Test Business"
    )

class TestAddStaff:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_staff_success(self, owner_user, staff_data):
        mock_db = AsyncMock()
        result = await mock_add_staff(staff_data, mock_db, owner_user)
        
        assert result.email == "staff@test.com"
        assert result.roles[0].name == "staff"
        assert result.phone_number == "1234567890"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_staff_unauthorized(self, non_owner_user, staff_data):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_add_staff(staff_data, mock_db, non_owner_user)
        
        assert exc.value.status_code == 403
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_staff_email_exists(self, owner_user):
        mock_db = AsyncMock()
        existing_staff = StaffCreate(
            email="existing@test.com",
            password="password123",
            phone_number="1234567890",
            assigned_role="cashier"
        )
        
        with pytest.raises(HTTPException) as exc:
            await mock_add_staff(existing_staff, mock_db, owner_user)
        
        assert exc.value.status_code == 400

class TestGetOwnerStaffs:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_staffs_success(self, owner_user):
        mock_db = AsyncMock()
        result = await mock_get_owner_staffs(mock_db, owner_user)
        
        assert len(result) == 2
        assert result[0].email == "staff1@test.com"
        assert result[0].assigned_role == "cashier"
        assert result[1].assigned_role == "supervisor"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_staffs_unauthorized(self, non_owner_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_get_owner_staffs(mock_db, non_owner_user)
        
        assert exc.value.status_code == 403

class TestDeleteStaff:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_staff_success(self, owner_user):
        mock_db = AsyncMock()
        result = await mock_delete_staff(2, mock_db, owner_user)
        
        assert result is None  

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_staff_unauthorized(self, non_owner_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_delete_staff(2, mock_db, non_owner_user)
        
        assert exc.value.status_code == 403
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_staff_not_found(self, owner_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_delete_staff(999, mock_db, owner_user)
        
        assert exc.value.status_code == 404

class TestUpdateStaff:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_staff_success(self, owner_user):
        mock_db = AsyncMock()
        update_data = StaffUpdate(
            phone_number="9999999999",
            assigned_role="supervisor"
        )
        
        result = await mock_update_staff(2, update_data, mock_db, owner_user)
        
        assert result == {"detail": "Staff updated successfully"}
    

class TestGetStaffDetail:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_staff_detail_success(self, owner_user):
        mock_db = AsyncMock()
        result = await mock_get_staff_detail(2, mock_db, owner_user)
        
        assert result.id == 2
        assert result.email == "staff@test.com"
        assert result.assigned_role == "cashier"
        assert result.business_name == "Test Business"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_staff_detail_unauthorized(self, non_owner_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_get_staff_detail(2, mock_db, non_owner_user)
        
        assert exc.value.status_code == 403
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_staff_detail_not_found(self, owner_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_get_staff_detail(999, mock_db, owner_user)
        
        assert exc.value.status_code == 404
