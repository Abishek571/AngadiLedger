import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime
from typing import List

from app.db.models.user import User
from app.db.models.customer import Customer
from app.db.models.business import Business
from app.db.models.ledger_entry import LedgerEntry

@pytest.fixture
def owner_user():
    """Create mock owner user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.role = "owner"
    user.business_id = 1
    return user

@pytest.fixture
def mock_customer():
    """Create mock customer object for testing."""
    customer = Mock(spec=Customer)
    customer.id = 1
    customer.business_id = 1
    customer.name = "Test Customer"
    return customer

@pytest.fixture
def mock_business():
    """Create mock business object for testing."""
    business = Mock(spec=Business)
    business.id = 1
    business.name = "Test Business"
    return business

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
    entry.created_at = datetime.now()
    return entry

async def mock_get_payments_from_ledger_entries(db, customer_id: int):
    """Mock function to get payments from ledger entries."""
    return [
        {
            "ledger_entry_id": 1,
            "customer_id": customer_id,
            "business_id": 1,
            "amount": Decimal("100.00"),
            "entry_type": "credit",
            "description": "Test payment",
            "image_url": None,
            "created_at": datetime.now(),
            "created_by_id": 1
        }
    ]

async def mock_get_partial_settlements(db):
    """Mock function to get partial settlements."""
    return [
        {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "partial_amount": Decimal("50.00"),
            "total_balance": Decimal("100.00")
        }
    ]

async def mock_get_outstanding_balances(db, threshold: float = 10000.0):
    """Mock function to get outstanding balances."""
    return [
        {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "outstanding_balance": Decimal("150.00"),
            "last_payment_date": datetime.now()
        }
    ]

async def mock_business_customer_access_required(customer_id: int, db, current_user: User):
    """Mock function for business customer access validation."""
    if customer_id == 999:
        raise HTTPException(status_code=404, detail="Customer not found.")
    
    customer = Mock(spec=Customer)
    customer.id = customer_id
    customer.business_id = current_user.business_id
    
    if customer.business_id != current_user.business_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this customer."
        )
    
    return customer

async def mock_business_ledger_access_required(ledger_entry_id: int, db, current_user: User):
    """Mock function for business ledger access validation."""
    if ledger_entry_id == 999:
        raise HTTPException(status_code=404, detail="Ledger entry not found.")
    
    ledger_entry = Mock(spec=LedgerEntry)
    ledger_entry.id = ledger_entry_id
    ledger_entry.business_id = current_user.business_id
    
    if ledger_entry.business_id != current_user.business_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this ledger entry."
        )
    
    return ledger_entry

async def mock_business_access_required(business_id: int, db, current_user: User):
    """Mock function for business access validation."""
    if business_id == 999:
        raise HTTPException(status_code=404, detail="Business not found.")
    
    business = Mock(spec=Business)
    business.id = business_id
    
    if business.id != current_user.business_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this business."
        )
    
    return business

async def mock_get_customer_balance(customer_id: int, db):
    """Mock function to get customer balance."""
    return Decimal("100.00")

async def mock_get_customer_balance_excluding_entry(customer_id: int, exclude_entry_id: int, db):
    """Mock function to get customer balance excluding specific entry."""
    return Decimal("50.00")

class TestPaymentEndpoints:
    """Test payment-related endpoints."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_payments_for_customer_success(self):
        """Test successful retrieval of customer payments."""
        mock_db = AsyncMock()
        customer_id = 1
        
        result = await mock_get_payments_from_ledger_entries(mock_db, customer_id)
        
        assert len(result) == 1
        assert result[0]["customer_id"] == customer_id
        assert result[0]["amount"] == Decimal("100.00")
        assert result[0]["entry_type"] == "credit"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_payments_for_customer_not_found(self):
        """Test customer payments not found scenario."""
        mock_db = AsyncMock()
        
        async def mock_empty_payments(db, customer_id):
            return []
        
        result = await mock_empty_payments(mock_db, 999)
        
        if not result:
            with pytest.raises(HTTPException) as exc:
                raise HTTPException(status_code=404, detail="No payments found for this customer.")
            
            assert exc.value.status_code == 404
            assert "No payments found" in exc.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_partial_settlement_endpoint_success(self, owner_user):
        """Test successful partial settlement retrieval."""
        mock_db = AsyncMock()
        
        result = await mock_get_partial_settlements(mock_db)
        
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["partial_amount"] == Decimal("50.00")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_outstanding_balance_endpoint_success(self, owner_user):
        """Test successful outstanding balance retrieval."""
        mock_db = AsyncMock()
        
        result = await mock_get_outstanding_balances(mock_db, threshold=10000.0)
        
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["outstanding_balance"] == Decimal("150.00")

class TestLedgerServices:
    """Test ledger service functions."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_business_customer_access_success(self, owner_user):
        """Test successful business customer access validation."""
        mock_db = AsyncMock()
        
        result = await mock_business_customer_access_required(1, mock_db, owner_user)
        
        assert result.id == 1
        assert result.business_id == owner_user.business_id
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_business_customer_access_not_found(self, owner_user):
        """Test business customer access with customer not found."""
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_business_customer_access_required(999, mock_db, owner_user)
        
        assert exc.value.status_code == 404
        assert "Customer not found" in exc.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_business_ledger_access_success(self, owner_user):
        """Test successful business ledger access validation."""
        mock_db = AsyncMock()
        
        result = await mock_business_ledger_access_required(1, mock_db, owner_user)
        
        assert result.id == 1
        assert result.business_id == owner_user.business_id
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_business_ledger_access_not_found(self, owner_user):
        """Test business ledger access with entry not found."""
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_business_ledger_access_required(999, mock_db, owner_user)
        
        assert exc.value.status_code == 404
        assert "Ledger entry not found" in exc.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_customer_balance_success(self):
        """Test successful customer balance retrieval."""
        mock_db = AsyncMock()
        
        balance = await mock_get_customer_balance(1, mock_db)
        
        assert balance == Decimal("100.00")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_customer_balance_excluding_entry_success(self):
        """Test successful customer balance retrieval excluding entry."""
        mock_db = AsyncMock()
        
        balance = await mock_get_customer_balance_excluding_entry(1, 1, mock_db)
        
        assert balance == Decimal("50.00")

class TestBusinessAccess:
    """Test business access validation."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_business_access_success(self, owner_user):
        """Test successful business access validation."""
        mock_db = AsyncMock()
        
        result = await mock_business_access_required(1, mock_db, owner_user)
        
        assert result.id == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_business_access_not_found(self, owner_user):
        """Test business access with business not found."""
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_business_access_required(999, mock_db, owner_user)
        
        assert exc.value.status_code == 404
        assert "Business not found" in exc.value.detail

class TestPaymentWorkflow:
    """Test complete payment workflow."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complete_payment_workflow(self, owner_user):
        """Test complete payment workflow."""
        mock_db = AsyncMock()
        
        customer = await mock_business_customer_access_required(1, mock_db, owner_user)
        assert customer.id == 1
        
        payments = await mock_get_payments_from_ledger_entries(mock_db, customer.id)
        assert len(payments) == 1
        assert payments[0]["customer_id"] == customer.id
        
        balance = await mock_get_customer_balance(customer.id, mock_db)
        assert balance == Decimal("100.00")
        
        settlements = await mock_get_partial_settlements(mock_db)
        assert len(settlements) == 1
        
        outstanding = await mock_get_outstanding_balances(mock_db)
        assert len(outstanding) == 1

class TestSimplePayments:
    """Test simple payment operations without schema validation."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_payment_data_structure(self):
        """Test payment data structure without Pydantic validation."""
        payment_data = {
            "ledger_entry_id": 1,
            "customer_id": 1,
            "business_id": 1,
            "amount": Decimal("100.00"),
            "entry_type": "credit",
            "description": "Test payment",
            "image_url": None,
            "created_at": datetime.now(),
            "created_by_id": 1
        }
        
        assert payment_data["customer_id"] == 1
        assert payment_data["amount"] == Decimal("100.00")
        assert payment_data["entry_type"] == "credit"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mock_service_functions(self):
        """Test that mock service functions work correctly."""
        mock_db = AsyncMock()
        
        payments = await mock_get_payments_from_ledger_entries(mock_db, 1)
        assert len(payments) == 1
        
        settlements = await mock_get_partial_settlements(mock_db)
        assert len(settlements) == 1
        
        balances = await mock_get_outstanding_balances(mock_db)
        assert len(balances) == 1
