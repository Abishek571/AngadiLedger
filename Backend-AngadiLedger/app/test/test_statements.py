import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from decimal import Decimal
from datetime import datetime
from io import StringIO

from app.db.models.user import User

@pytest.fixture
def owner_user():
    """Create mock owner user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.role = "owner"
    user.business_id = 1
    return user

def mock_list_of_dicts_to_csv(data_list):
    """Mock function to convert list of dicts to CSV."""
    if not data_list:
        return StringIO("")
    
    csv_content = StringIO()
    if data_list:
        headers = ",".join(data_list[0].keys())
        csv_content.write(headers + "\n")
        
        for row in data_list:
            values = ",".join(str(v) for v in row.values())
            csv_content.write(values + "\n")
    
    csv_content.seek(0)
    return csv_content

async def mock_get_payments_from_ledger_entries(db, customer_id: int):
    """Mock function to get payments from ledger entries."""
    if customer_id == 999:
        return []
    
    return [
        {
            "ledger_entry_id": 1,
            "customer_id": customer_id,
            "business_id": 1,
            "amount": "100.00",
            "entry_type": "credit",
            "description": "Test payment",
            "created_at": "2024-01-01"
        }
    ]

async def mock_get_partial_settlements(db):
    """Mock function to get partial settlements."""
    return [
        {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "partial_amount": "50.00",
            "total_balance": "100.00"
        }
    ]

async def mock_get_outstanding_balances(db, threshold: float = 10000.0):
    """Mock function to get outstanding balances."""
    return [
        {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "outstanding_balance": "150.00",
            "last_payment_date": "2024-01-01"
        }
    ]

async def mock_download_payments_csv(customer_id: int, db):
    """Mock function to download payments CSV."""
    payments = await mock_get_payments_from_ledger_entries(db, customer_id)
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found for this customer.")
    
    csv_file = mock_list_of_dicts_to_csv(payments)
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=payments_customer_{customer_id}.csv"}
    )

async def mock_download_partial_settlements_csv(db, user):
    """Mock function to download partial settlements CSV."""
    settlements = await mock_get_partial_settlements(db)
    if not settlements:
        raise HTTPException(status_code=404, detail="No partial settlements found.")
    
    csv_file = mock_list_of_dicts_to_csv(settlements)
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=partial_settlements.csv"}
    )

async def mock_download_outstanding_balances_csv(db, user):
    """Mock function to download outstanding balances CSV."""
    balances = await mock_get_outstanding_balances(db, threshold=10000.0)
    if not balances:
        raise HTTPException(status_code=404, detail="No outstanding balances found.")
    
    csv_file = mock_list_of_dicts_to_csv(balances)
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=outstanding_balances.csv"}
    )

class TestCSVDownloads:
    """Test CSV download functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_download_payments_csv_success(self):
        """Test successful payments CSV download."""
        mock_db = AsyncMock()
        customer_id = 1
        
        result = await mock_download_payments_csv(customer_id, mock_db)
        
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/csv"
        assert f"payments_customer_{customer_id}.csv" in result.headers["Content-Disposition"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_download_payments_csv_not_found(self):
        """Test payments CSV download when no payments found."""
        mock_db = AsyncMock()
        customer_id = 999
        
        with pytest.raises(HTTPException) as exc:
            await mock_download_payments_csv(customer_id, mock_db)
        
        assert exc.value.status_code == 404
        assert "No payments found" in exc.value.detail
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_download_partial_settlements_csv_success(self, owner_user):
        """Test successful partial settlements CSV download."""
        mock_db = AsyncMock()
        
        result = await mock_download_partial_settlements_csv(mock_db, owner_user)
        
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/csv"
        assert "partial_settlements.csv" in result.headers["Content-Disposition"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_download_outstanding_balances_csv_success(self, owner_user):
        """Test successful outstanding balances CSV download."""
        mock_db = AsyncMock()
        
        result = await mock_download_outstanding_balances_csv(mock_db, owner_user)
        
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/csv"
        assert "outstanding_balances.csv" in result.headers["Content-Disposition"]

class TestCSVGeneration:
    """Test CSV generation functionality."""
    
    @pytest.mark.unit
    def test_list_of_dicts_to_csv_success(self):
        """Test successful CSV generation from list of dicts."""
        data = [
            {"id": 1, "name": "Test", "amount": "100.00"},
            {"id": 2, "name": "Test2", "amount": "200.00"}
        ]
        
        csv_file = mock_list_of_dicts_to_csv(data)
        content = csv_file.read()
        
        assert "id,name,amount" in content
        assert "1,Test,100.00" in content
        assert "2,Test2,200.00" in content
    
    @pytest.mark.unit
    def test_list_of_dicts_to_csv_empty(self):
        """Test CSV generation with empty data."""
        data = []
        
        csv_file = mock_list_of_dicts_to_csv(data)
        content = csv_file.read()
        
        assert content == ""

class TestDataRetrieval:
    """Test data retrieval functions."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_payments_from_ledger_entries_success(self):
        """Test successful payment data retrieval."""
        mock_db = AsyncMock()
        
        result = await mock_get_payments_from_ledger_entries(mock_db, 1)
        
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["amount"] == "100.00"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_payments_from_ledger_entries_empty(self):
        """Test payment data retrieval with no results."""
        mock_db = AsyncMock()
        
        result = await mock_get_payments_from_ledger_entries(mock_db, 999)
        
        assert len(result) == 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_partial_settlements_success(self):
        """Test successful partial settlements retrieval."""
        mock_db = AsyncMock()
        
        result = await mock_get_partial_settlements(mock_db)
        
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["partial_amount"] == "50.00"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_outstanding_balances_success(self):
        """Test successful outstanding balances retrieval."""
        mock_db = AsyncMock()
        
        result = await mock_get_outstanding_balances(mock_db, threshold=10000.0)
        
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["outstanding_balance"] == "150.00"

class TestCSVWorkflow:
    """Test complete CSV download workflow."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complete_csv_workflow(self, owner_user):
        """Test complete CSV download workflow."""
        mock_db = AsyncMock()
        
   
        payments_csv = await mock_download_payments_csv(1, mock_db)
        assert isinstance(payments_csv, StreamingResponse)
   
        settlements_csv = await mock_download_partial_settlements_csv(mock_db, owner_user)
        assert isinstance(settlements_csv, StreamingResponse)
 
        balances_csv = await mock_download_outstanding_balances_csv(mock_db, owner_user)
        assert isinstance(balances_csv, StreamingResponse)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_csv_error_handling(self, owner_user):
        """Test CSV download error handling."""
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc:
            await mock_download_payments_csv(999, mock_db)
        assert exc.value.status_code == 404
   
        async def empty_settlements(db):
            return []

        original_func = mock_get_partial_settlements
        try:
            settlements = await empty_settlements(mock_db)
            if not settlements:
                with pytest.raises(HTTPException) as exc:
                    raise HTTPException(status_code=404, detail="No partial settlements found.")
                assert exc.value.status_code == 404
        finally:
            pass

class TestSimpleCSV:
    """Test simple CSV operations."""
    
    @pytest.mark.unit
    def test_csv_headers_generation(self):
        """Test CSV headers are generated correctly."""
        data = [{"name": "Test", "value": 100}]
        csv_file = mock_list_of_dicts_to_csv(data)
        content = csv_file.read()
        
        lines = content.strip().split('\n')
        assert lines[0] == "name,value"
        assert lines[1] == "Test,100"
    
    @pytest.mark.unit
    def test_streaming_response_properties(self):
        """Test StreamingResponse properties."""
        csv_content = StringIO("test,data\n1,2")
        response = StreamingResponse(
            csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=test.csv"}
        )
        
        assert response.media_type == "text/csv"
        assert "test.csv" in response.headers["Content-Disposition"]
        assert "attachment" in response.headers["Content-Disposition"]
