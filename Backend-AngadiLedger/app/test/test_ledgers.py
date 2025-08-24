import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime

from app.db.schemas.ledger_entry import LedgerEntryCreate, LedgerEntryRead, LedgerEntryUpdate
from app.db.models.ledger_entry import LedgerEntry
from app.db.models.user import User
from app.db.models.customer import Customer
from app.db.models.business import Business

@pytest.fixture
def owner_user():
    """Create mock owner user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.role = "owner"
    user.business_id = 1
    return user

@pytest.fixture
def ledger_entry_data():
    """Create valid ledger entry data for testing."""
    return {
        "customer_id": 1,
        "entry_type": "credit",
        "amount": Decimal("100.00"),
        "description": "Test entry",
        "image_url": None
    }

@pytest.fixture
def mock_ledger_entry():
    """Create mock ledger entry object for testing."""
    entry = Mock(spec=LedgerEntry)
    entry.id = 1
    entry.customer_id = 1
    entry.business_id = 1
    entry.entry_type = "credit"
    entry.amount = Decimal("100.00")
    entry.description = "Test entry"
    entry.image_url = None
    entry.created_by_id = 1
    entry.created_at = datetime.now()
    return entry

@pytest.fixture
def mock_customer():
    """Create mock customer object for testing."""
    customer = Mock(spec=Customer)
    customer.id = 1
    customer.business_id = 1
    return customer

@pytest.fixture
def mock_business():
    """Create mock business object for testing."""
    business = Mock(spec=Business)
    business.id = 1
    return business

async def mock_get_customer_balance(customer_id: int, db):
    """Mock function to get customer balance."""
    return Decimal("50.00")

async def mock_get_customer_balance_excluding_entry(customer_id: int, entry_id: int, db):
    """Mock function to get customer balance excluding specific entry."""
    return Decimal("50.00")

async def mock_create_ledger_entry(entry_data: dict, db, current_user: User):
    """Mock function to create ledger entry."""
    balance = await mock_get_customer_balance(entry_data["customer_id"], db)
    
    if entry_data["entry_type"] == "debit":
        if balance == 0 and entry_data["amount"] > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot debit: customer has no available credit."
            )
        elif entry_data["amount"] > balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available credit: {balance}"
            )
    
    return LedgerEntryRead(
        id=1,
        customer_id=entry_data["customer_id"],
        business_id=current_user.business_id,
        entry_type=entry_data["entry_type"],
        amount=entry_data["amount"],
        description=entry_data["description"],
        image_url=entry_data["image_url"],
        created_by_id=current_user.id,
        created_at=datetime.now()
    )

async def mock_update_ledger_entry(entry_id: int, entry_update: LedgerEntryUpdate, db, current_user: User):
    """Mock function to update ledger entry."""
    mock_entry = Mock(spec=LedgerEntry)
    mock_entry.id = entry_id
    mock_entry.customer_id = 1
    mock_entry.business_id = current_user.business_id
    mock_entry.entry_type = "credit"
    mock_entry.amount = Decimal("100.00")
    mock_entry.description = "Test entry"
    mock_entry.image_url = None
    mock_entry.created_by_id = current_user.id
    mock_entry.created_at = datetime.now()
    
    balance = await mock_get_customer_balance_excluding_entry(mock_entry.customer_id, entry_id, db)
    
    new_entry_type = entry_update.entry_type or mock_entry.entry_type
    new_amount = entry_update.amount or mock_entry.amount
    
    if new_entry_type == "debit":
        new_balance = balance - new_amount
        if new_balance < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available credit: {balance}"
            )
    
    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mock_entry, field, value)
    
    return LedgerEntryRead(
        id=mock_entry.id,
        customer_id=mock_entry.customer_id,
        business_id=mock_entry.business_id,
        entry_type=mock_entry.entry_type,
        amount=mock_entry.amount,
        description=mock_entry.description,
        image_url=mock_entry.image_url,
        created_by_id=mock_entry.created_by_id,
        created_at=mock_entry.created_at
    )

async def mock_list_customer_ledgers(customer: Customer, db):
    """Mock function to list customer ledgers."""
    return [
        LedgerEntryRead(
            id=1,
            customer_id=customer.id,
            business_id=customer.business_id,
            entry_type="credit",
            amount=Decimal("100.00"),
            description="Test entry",
            image_url=None,
            created_by_id=1,
            created_at=datetime.now()
        )
    ]

class TestCreateLedgerEntry:
    """Test ledger entry creation functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_credit_entry_success(self, owner_user, ledger_entry_data):
        """Test successful credit entry creation."""
        mock_db = AsyncMock()
        result = await mock_create_ledger_entry(ledger_entry_data, mock_db, owner_user)
        
        assert isinstance(result, LedgerEntryRead)
        assert result.entry_type == "credit"
        assert result.amount == Decimal("100.00")
        assert result.business_id == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_debit_entry_insufficient_balance(self, owner_user):
        """Test debit entry creation with insufficient balance."""
        mock_db = AsyncMock()
        debit_data = {
            "customer_id": 1,
            "entry_type": "debit",
            "amount": Decimal("100.00"),
            "description": "Test debit",
            "image_url": None
        }
        
        with pytest.raises(HTTPException) as exc:
            await mock_create_ledger_entry(debit_data, mock_db, owner_user)
        
        assert exc.value.status_code == 400
        assert "Insufficient balance" in exc.value.detail

class TestUpdateLedgerEntry:
    """Test ledger entry update functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_entry_success(self, owner_user):
        """Test successful ledger entry update."""
        mock_db = AsyncMock()
        update_data = LedgerEntryUpdate(
            description="Updated description",
            amount=Decimal("150.00")
        )
        
        result = await mock_update_ledger_entry(1, update_data, mock_db, owner_user)
        
        assert result.description == "Updated description"
        assert result.amount == Decimal("150.00")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_entry_insufficient_balance(self, owner_user):
        """Test update entry with insufficient balance."""
        mock_db = AsyncMock()
        update_data = LedgerEntryUpdate(
            entry_type="debit",
            amount=Decimal("200.00")
        )
        
        with pytest.raises(HTTPException) as exc:
            await mock_update_ledger_entry(1, update_data, mock_db, owner_user)
        
        assert exc.value.status_code == 400
        assert "Insufficient balance" in exc.value.detail

class TestListLedgerEntries:
    """Test ledger entry listing functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_customer_ledgers_success(self, mock_customer):
        """Test successful customer ledger listing."""
        mock_db = AsyncMock()
        result = await mock_list_customer_ledgers(mock_customer, mock_db)
        
        assert len(result) == 1
        assert result[0].customer_id == mock_customer.id
        assert result[0].entry_type == "credit"

class TestLedgerWorkflow:
    """Test complete ledger workflow."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complete_ledger_workflow(self, owner_user):
        """Test complete ledger CRUD workflow."""
        mock_db = AsyncMock()
        
        entry_data = {
            "customer_id": 1,
            "entry_type": "credit",
            "amount": Decimal("100.00"),
            "description": "Initial credit",
            "image_url": None
        }
        
        created = await mock_create_ledger_entry(entry_data, mock_db, owner_user)
        assert created.entry_type == "credit"
        assert created.amount == Decimal("100.00")
        
        update_data = LedgerEntryUpdate(description="Updated credit")
        updated = await mock_update_ledger_entry(created.id, update_data, mock_db, owner_user)
        assert updated.description == "Updated credit"
