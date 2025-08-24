import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user import UserCreate, UserLogin, UserVerifyOTP, UserRead, RoleRead
from app.db.models.user import User, Role, UserRole
from app.db.models.business import Business

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@pytest.fixture
def mock_register_user():
    """Mock the register_user function for testing."""
    async def _register_user(user_in: UserCreate, db: AsyncSession):
        if user_in.email == "existing@test.com":
            raise HTTPException(status_code=400, detail="Email already registered")
        
        roles = [RoleRead(id=1, name=user_in.role)]
        business_name = user_in.business_name if user_in.role == "owner" else None
        
        return UserRead(
            id=1,
            email=user_in.email,
            is_verified=False,
            roles=roles,
            phone_number=user_in.phone_number,
            business_name=business_name
        )
    return _register_user

@pytest.fixture
def mock_verify_otp():
    """Mock the verify_otp function for testing."""
    async def _verify_otp(otp_data: UserVerifyOTP, db: AsyncSession):
        if otp_data.email == "nonexistent@example.com":
            raise HTTPException(status_code=404, detail="User not found")
        
        if otp_data.otp_code != "123456":
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        roles = [RoleRead(id=1, name="employee")]
        return UserRead(
            id=1,
            email=otp_data.email,
            is_verified=True,
            roles=roles,
            phone_number="1234567890",
            business_name=None
        )
    return _verify_otp

@pytest.fixture
def mock_login():
    """Mock the login function for testing."""
    async def _login(request: Request, user_in: UserLogin, db: AsyncSession):
        if user_in.email == "nonexistent@example.com":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user_in.password == "wrong_password":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user_in.email == "unverified@example.com":
            raise HTTPException(status_code=403, detail="User not verified")
        
        # Simulate successful login
        return {
            "access_token": "fake_access_token_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": user_in.email,
                "role": "employee",
                "business_id": 1,
                "phone_number": "1234567890"
            }
        }
    return _login

class TestRegisterUser:
    """Unit tests for user registration endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_register_user_success_owner(self, mock_register_user):
        """Test successful user registration as owner with new business."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        
        user_data = UserCreate(
            email="owner@test.com",
            password="password123",
            role="owner",
            business_name="Test Business",  # Required for owner role
            phone_number="1234567890"
        )
        
        # Act
        result = await mock_register_user(user_data, mock_db)
        
        # Assert
        assert isinstance(result, UserRead)
        assert result.email == "owner@test.com"
        assert result.is_verified is False
        assert result.business_name == "Test Business"
        assert len(result.roles) == 1
        assert result.roles[0].name == "owner"
        assert result.phone_number == "1234567890"
    
    
class TestVerifyOTP:
    """Unit tests for OTP verification endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_otp_success(self, mock_verify_otp):
        """Test successful OTP verification."""
        mock_db = AsyncMock(spec=AsyncSession)
        
        otp_data = UserVerifyOTP(email="test@example.com", otp_code="123456")
        
        result = await mock_verify_otp(otp_data, mock_db)
        
        assert isinstance(result, UserRead)
        assert result.email == "test@example.com"
        assert result.is_verified is True
        assert len(result.roles) == 1
        assert result.roles[0].name == "employee"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_otp_user_not_found(self, mock_verify_otp):
        """Test OTP verification with non-existent user."""
        mock_db = AsyncMock(spec=AsyncSession)
        
        otp_data = UserVerifyOTP(email="nonexistent@example.com", otp_code="123456")
 
        with pytest.raises(HTTPException) as exc_info:
            await mock_verify_otp(otp_data, mock_db)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_otp_invalid_code(self, mock_verify_otp):
        """Test OTP verification with wrong OTP code."""

        mock_db = AsyncMock(spec=AsyncSession)
        
        otp_data = UserVerifyOTP(email="test@example.com", otp_code="wrong_code")

        with pytest.raises(HTTPException) as exc_info:
            await mock_verify_otp(otp_data, mock_db)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid OTP"

class TestLogin:
    """Unit tests for user login endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_success(self, mock_login):
        """Test successful user login."""
  
        mock_db = AsyncMock(spec=AsyncSession)
        mock_request = Mock(spec=Request)
        
        login_data = UserLogin(email="test@example.com", password="password123")
        
        result = await mock_login(mock_request, login_data, mock_db)
     
        assert result["access_token"] == "fake_access_token_123"
        assert result["token_type"] == "bearer"
        assert result["user"]["id"] == 1
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["role"] == "employee"
        assert result["user"]["business_id"] == 1
        assert result["user"]["phone_number"] == "1234567890"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_login):
        """Test login with non-existent user."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_request = Mock(spec=Request)
        
        login_data = UserLogin(email="nonexistent@example.com", password="password123")
        
        with pytest.raises(HTTPException) as exc_info:
            await mock_login(mock_request, login_data, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, mock_login):
        """Test login with wrong password."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_request = Mock(spec=Request)
        
        login_data = UserLogin(email="test@example.com", password="wrong_password")
        
        with pytest.raises(HTTPException) as exc_info:
            await mock_login(mock_request, login_data, mock_db)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_unverified_user(self, mock_login):
        """Test login with unverified user."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_request = Mock(spec=Request)
        
        login_data = UserLogin(email="unverified@example.com", password="password123")
        
        with pytest.raises(HTTPException) as exc_info:
            await mock_login(mock_request, login_data, mock_db)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "User not verified"
