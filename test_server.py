import asyncio
from unittest.mock import MagicMock, patch
from holded_mcp.tools import get_outstanding_invoices, get_customer_spending

# Mock data
MOCK_INVOICES = [
    {"id": "inv1", "contactName": "Client A", "total": 100.0, "date": "2023-01-15", "status": 1}, # Paid
    {"id": "inv2", "contactName": "Client A", "total": 200.0, "date": "2023-02-20", "status": 0}, # Unpaid
    {"id": "inv3", "contactName": "Client B", "total": 300.0, "date": "2023-03-10", "paid": False}, # Unpaid (alt field)
    {"id": "inv4", "contactName": "Client A", "total": 150.0, "date": "2022-12-01", "status": 1}, # Paid, prev year
    {"id": "inv5", "contactName": "Client A", "total": 50.0, "date": "2023-04-05", "contactId": "contact_a_id", "status": 1}, # Paid, with ID
]

MOCK_CONTACTS = [
    {"id": "contact_a_id", "name": "Client A"},
    {"id": "contact_b_id", "name": "Client B"},
]

async def test_outstanding_invoices():
    print("Testing get_outstanding_invoices...")
    with patch('holded_mcp.tools.HoldedClient') as MockClient:
        instance = MockClient.return_value
        # Mock async methods
        f = asyncio.Future()
        f.set_result(MOCK_INVOICES)
        instance.get_invoices.return_value = f
        
        results = await get_outstanding_invoices()
        
        # Expect inv2 and inv3
        assert len(results) == 2
        assert results[0]['id'] == 'inv2'
        assert results[1]['id'] == 'inv3'
        print("PASS: Correctly identified outstanding invoices.")

async def test_customer_spending():
    print("\nTesting get_customer_spending...")
    with patch('holded_mcp.tools.HoldedClient') as MockClient:
        instance = MockClient.return_value
        
        # Mock get_contact_by_name
        async def mock_get_contact(name):
            return next((c for c in MOCK_CONTACTS if c['name'] == name), None)
        instance.get_contact_by_name.side_effect = mock_get_contact
        
        # Mock get_invoices
        spending_invoices = [
            {"id": "1", "contactId": "contact_a_id", "total": 100, "date": "2023-01-01"},
            {"id": "2", "contactId": "contact_a_id", "total": 200, "date": "2023-06-01"},
            {"id": "3", "contactId": "contact_b_id", "total": 500, "date": "2023-01-01"},
            {"id": "4", "contactId": "contact_a_id", "total": 50, "date": "2022-12-31"}, # Prev year
        ]
        f = asyncio.Future()
        f.set_result(spending_invoices)
        instance.get_invoices.return_value = f
        
        # Test 2023 spending for Client A
        result = await get_customer_spending("Client A", year=2023)
        print(f"Result: {result}")
        
        # Expected: 100 + 200 = 300
        assert "300.00" in result
        assert "2 invoices" in result
        print("PASS: Correctly calculated spending.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_outstanding_invoices())
    loop.run_until_complete(test_customer_spending())
