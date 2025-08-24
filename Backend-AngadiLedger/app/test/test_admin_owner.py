import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user import UserCreate, UserRead, OwnerUserRead, RoleRead
from app.db.models.user import User

@pytest.fixture
def admin_user():
    user = Mock(spec=User)
    user.role = "admin"
    return user

@pytest.fixture
def non_admin_user():
    user = Mock(spec=User)
    user.role = "employee"
    return user

@pytest.fixture
def owner_data():
    return UserCreate(
        email="owner@test.com",
        password="password123",
        phone_number="1234567890",
        business_name="Test Business",
        role="owner"
    )

async def mock_add_owner(owner_in: UserCreate, db: AsyncSession, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if owner_in.email == "existing@test.com":
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return UserRead(
        id=1,
        email=owner_in.email,
        is_verified=True,
        roles=[RoleRead(id=1, name="owner")],
        phone_number=owner_in.phone_number,
        business_name=owner_in.business_name
    )

async def mock_delete_owner(owner_id: int, db: AsyncSession, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if owner_id == 999:
        raise HTTPException(status_code=404, detail="Owner not found")
    return {"detail": "Owner deleted successfully"}

async def mock_get_all_owners(db: AsyncSession, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return [
        OwnerUserRead(
            id=1,
            email="owner1@test.com",
            phone_number="1234567890",
            is_verified=True,
            business_name="Business One"
        )
    ]

class TestAddOwner:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_owner_success(self, admin_user, owner_data):
        mock_db = AsyncMock()
        result = await mock_add_owner(owner_data, mock_db, admin_user)
        
        assert result.email == "owner@test.com"
        assert result.business_name == "Test Business"
        assert result.roles[0].name == "owner"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_owner_unauthorized(self, non_admin_user, owner_data):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_add_owner(owner_data, mock_db, non_admin_user)
        
        assert exc.value.status_code == 403
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_owner_email_exists(self, admin_user):
        mock_db = AsyncMock()
        existing_data = UserCreate(
            email="existing@test.com",
            password="password123",
            phone_number="1234567890",
            business_name="Test Business",
            role="owner"
        )
        
        with pytest.raises(HTTPException) as exc:
            await mock_add_owner(existing_data, mock_db, admin_user)
        
        assert exc.value.status_code == 400

class TestDeleteOwner:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_owner_success(self, admin_user):
        mock_db = AsyncMock()
        result = await mock_delete_owner(1, mock_db, admin_user)
        
        assert result == {"detail": "Owner deleted successfully"}
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_owner_unauthorized(self, non_admin_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_delete_owner(1, mock_db, non_admin_user)
        
        assert exc.value.status_code == 403
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_owner_not_found(self, admin_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_delete_owner(999, mock_db, admin_user)
        
        assert exc.value.status_code == 404

class TestGetAllOwners:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_owners_success(self, admin_user):
        mock_db = AsyncMock()
        result = await mock_get_all_owners(mock_db, admin_user)
        
        assert len(result) == 1
        assert result[0].email == "owner1@test.com"
        assert result[0].business_name == "Business One"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_owners_unauthorized(self, non_admin_user):
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_get_all_owners(mock_db, non_admin_user)
        
        assert exc.value.status_code == 403
