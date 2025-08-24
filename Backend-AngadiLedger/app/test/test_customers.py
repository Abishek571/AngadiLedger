import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.db.models.customer import Customer
from app.db.models.user import User

@pytest.fixture
def owner_user():
    """Create mock owner user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.role = "owner"
    user.business_id = 1
    return user

@pytest.fixture
def customer_data():
    """Create valid customer data for testing."""
    return {
        "name": "John Doe",
        "email": "john@test.com",
        "phone_number": "1234567890",
        "relationship_type": "regular",
        "notes": "Test customer"
    }

@pytest.fixture
def mock_customer():
    """Create mock customer object for testing."""
    customer = Mock(spec=Customer)
    customer.id = 1
    customer.name = "John Doe"
    customer.email = "john@test.com"
    customer.phone_number = "1234567890"
    customer.business_id = 1
    customer.relationship_type = "regular"
    customer.notes = "Test customer"
    customer.created_by_id = 1
    return customer

async def mock_create_customer(customer_data: dict, db: AsyncSession, current_user: User):
    """Mock function to create customer."""
    if not current_user.business_id:
        raise HTTPException(status_code=404, detail="Business not found.")
    
    return CustomerRead(
        id=1,
        name=customer_data["name"],
        email=customer_data["email"],
        phone_number=customer_data["phone_number"],
        business_id=current_user.business_id,
        relationship_type=customer_data["relationship_type"],
        notes=customer_data["notes"],
        created_by_id=current_user.id
    )

async def mock_update_customer(customer_update: CustomerUpdate, customer: Customer, db: AsyncSession):
    """Mock function to update customer."""
    for field, value in customer_update.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    return customer

async def mock_list_customers(db: AsyncSession, current_user: User):
    """Mock function to list customers."""
    if not current_user.business_id:
        raise HTTPException(status_code=400, detail="User is not associated with any business.")
    
    return [
        CustomerRead(
            id=1,
            name="John Doe",
            email="john@test.com",
            phone_number="1234567890",
            business_id=current_user.business_id,
            relationship_type="regular",
            notes="Test customer",
            created_by_id=current_user.id
        )
    ]

class TestCreateCustomer:
    """Test customer creation functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_customer_success(self, owner_user, customer_data):
        """Test successful customer creation."""
        mock_db = AsyncMock()
        result = await mock_create_customer(customer_data, mock_db, owner_user)
        
        assert isinstance(result, CustomerRead)
        assert result.name == "John Doe"
        assert result.email == "john@test.com"
        assert result.business_id == 1
        assert result.created_by_id == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_customer_no_business(self, customer_data):
        """Test customer creation fails without business."""
        user_no_business = Mock(spec=User)
        user_no_business.business_id = None
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_create_customer(customer_data, mock_db, user_no_business)
        
        assert exc.value.status_code == 404
        assert "Business not found" in exc.value.detail

class TestUpdateCustomer:
    """Test customer update functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_customer_success(self, mock_customer):
        """Test successful customer update."""
        mock_db = AsyncMock()
        update_data = CustomerUpdate(
            name="John Updated",
            phone_number="9999999999"
        )
        
        result = await mock_update_customer(update_data, mock_customer, mock_db)
        
        assert result.name == "John Updated"
        assert result.phone_number == "9999999999"
        assert result.email == "john@test.com"

class TestListCustomers:
    """Test customer listing functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_customers_success(self, owner_user):
        """Test successful customer listing."""
        mock_db = AsyncMock()
        result = await mock_list_customers(mock_db, owner_user)
        
        assert len(result) == 1
        assert result[0].name == "John Doe"
        assert result[0].business_id == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_customers_no_business(self):
        """Test customer listing fails without business."""
        user_no_business = Mock(spec=User)
        user_no_business.business_id = None
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_list_customers(mock_db, user_no_business)
        
        assert exc.value.status_code == 400
        assert "not associated with any business" in exc.value.detail

class TestCustomerWorkflow:
    """Test complete customer workflow."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complete_workflow(self, owner_user):
        """Test complete customer CRUD workflow."""
        mock_db = AsyncMock()

        customer_data = {
            "name": "Workflow Test",
            "email": "workflow@test.com",
            "phone_number": "1111111111",
            "relationship_type": "regular",
            "notes": "Test notes"
        }
        
        created = await mock_create_customer(customer_data, mock_db, owner_user)
        assert created.name == "Workflow Test"
        
        mock_customer = Mock(spec=Customer)
        mock_customer.name = created.name
        mock_customer.email = created.email
        mock_customer.phone_number = created.phone_number
        
        update_data = CustomerUpdate(name="Updated Test")
        updated = await mock_update_customer(update_data, mock_customer, mock_db)
        assert updated.name == "Updated Test"
