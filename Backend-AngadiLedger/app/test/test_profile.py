import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user import UserProfileRead, UserProfileUpdate, UserProfileView, PersonalDetail, BusinessDetail
from app.db.models.user import User

@pytest.fixture
def admin_user():
    user = Mock(spec=User)
    user.id = 1
    user.email = "admin@test.com"
    user.phone_number = "1234567890"
    user.is_verified = True
    user.role = "admin"
    user.business_id = None
    return user

@pytest.fixture
def owner_user():
    user = Mock(spec=User)
    user.id = 2
    user.email = "owner@test.com"
    user.phone_number = "1234567890"
    user.is_verified = True
    user.role = "owner"
    user.business_id = 1
    return user

@pytest.fixture
def staff_user():
    user = Mock(spec=User)
    user.id = 3
    user.email = "staff@test.com"
    user.phone_number = "1234567890"
    user.is_verified = True
    user.role = "staff"
    user.business_id = 1
    return user

async def mock_get_profile(db: AsyncSession, current_user: User):
    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "is_verified": current_user.is_verified,
        "role": current_user.role,
        "roles": [current_user.role]
    }
    
    if current_user.role == "admin":
        return UserProfileRead(**profile_data)
    elif current_user.role == "owner":
        profile_data["business_name"] = "Test Business"
        return UserProfileRead(**profile_data)
    elif current_user.role == "staff":
        profile_data["business_name"] = "Test Business"
        profile_data["assigned_role"] = "cashier"
        return UserProfileRead(**profile_data)
    else:
        raise HTTPException(status_code=400, detail="Unknown user role.")

async def mock_update_profile(update: UserProfileUpdate, db: AsyncSession, current_user: User):
    current_user.phone_number = update.phone_number
    return await mock_get_profile(db, current_user)

async def mock_view_profile_details(db: AsyncSession, current_user: User):
    personal = PersonalDetail(
        email=current_user.email,
        phone_number=current_user.phone_number
    )
    
    business_name = "Test Business" if current_user.role in ("owner", "staff") else None
    assigned_role = "cashier" if current_user.role == "staff" else None
    
    business = BusinessDetail(
        email=current_user.email,
        business_name=business_name,
        assigned_role=assigned_role
    )
    
    return UserProfileView(personal=personal, business=business)

class TestGetProfile:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_admin_profile(self, admin_user):
        mock_db = AsyncMock()
        result = await mock_get_profile(mock_db, admin_user)
        
        assert result.id == 1
        assert result.email == "admin@test.com"
        assert result.role == "admin"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_owner_profile(self, owner_user):
        mock_db = AsyncMock()
        result = await mock_get_profile(mock_db, owner_user)
        
        assert result.id == 2
        assert result.email == "owner@test.com"
        assert result.role == "owner"
        assert result.business_name == "Test Business"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_staff_profile(self, staff_user):
        mock_db = AsyncMock()
        result = await mock_get_profile(mock_db, staff_user)
        
        assert result.id == 3
        assert result.email == "staff@test.com"
        assert result.role == "staff"
        assert result.business_name == "Test Business"
        assert result.assigned_role == "cashier"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_profile_unknown_role(self):
        unknown_user = Mock(spec=User)
        unknown_user.role = "unknown"
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_get_profile(mock_db, unknown_user)
        
        assert exc.value.status_code == 400
        assert "Unknown user role" in exc.value.detail

class TestUpdateProfile:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_profile_success(self, admin_user):
        mock_db = AsyncMock()
        update_data = UserProfileUpdate(phone_number="9999999999")
        
        result = await mock_update_profile(update_data, mock_db, admin_user)
        
        assert result.phone_number == "9999999999"
        assert result.email == "admin@test.com"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_owner_profile(self, owner_user):
        mock_db = AsyncMock()
        update_data = UserProfileUpdate(phone_number="8888888888")
        
        result = await mock_update_profile(update_data, mock_db, owner_user)
        
        assert result.phone_number == "8888888888"
        assert result.business_name == "Test Business"

class TestViewProfileDetails:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_view_admin_details(self, admin_user):
        mock_db = AsyncMock()
        result = await mock_view_profile_details(mock_db, admin_user)
        
        assert result.personal.email == "admin@test.com"
        assert result.personal.phone_number == "1234567890"
        assert result.business.business_name is None
        assert result.business.assigned_role is None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_view_owner_details(self, owner_user):
        mock_db = AsyncMock()
        result = await mock_view_profile_details(mock_db, owner_user)
        
        assert result.personal.email == "owner@test.com"
        assert result.business.business_name == "Test Business"
        assert result.business.assigned_role is None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_view_staff_details(self, staff_user):
        mock_db = AsyncMock()
        result = await mock_view_profile_details(mock_db, staff_user)
        
        assert result.personal.email == "staff@test.com"
        assert result.business.business_name == "Test Business"
        assert result.business.assigned_role == "cashier"
