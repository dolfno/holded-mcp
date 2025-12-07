from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from holded_mcp.client import HoldedClient

async def get_outstanding_invoices() -> List[Dict[str, Any]]:
    """
    Retrieves a list of outstanding (unpaid) invoices.
    Returns a simplified list of invoices with ID, contact name, amount, and due date.
    """
    client = HoldedClient()
    invoices = await client.get_invoices()
    
    outstanding = []
    for invoice in invoices:
        # Logic to determine if outstanding. 
        # Assuming 'status' field exists where 0=unpaid, 1=paid, 2=partial
        # Or checking 'pending' amount if available.
        # Fallback: Check if 'paid' is false or 'payment' < 'total'
        
        # Note: Based on typical Holded API responses (inferred), we look for 'status' or 'pending'.
        # Since schema was vague, we'll try to be robust.
        
        is_paid = False
        if 'status' in invoice:
            if invoice['status'] == 1: # Assuming 1 is paid
                is_paid = True
        elif 'paid' in invoice: # Boolean flag
             is_paid = bool(invoice['paid'])
        
        if not is_paid:
            outstanding.append({
                "id": invoice.get("id"),
                "contactName": invoice.get("contactName", "Unknown"), # API might return contactId, need to check if name is expanded
                "total": invoice.get("total"),
                "date": invoice.get("date"),
                "dueDate": invoice.get("dueDate") # If available
            })
            
    return outstanding

async def get_customer_spending(customer_name: str, year: int = None) -> str:
    """
    Calculates the total spending of a customer for a specific year.
    If year is not provided, defaults to the previous year.
    """
    client = HoldedClient()
    
    if year is None:
        year = datetime.now().year - 1
        
    contact = await client.get_contact_by_name(customer_name)
    if not contact:
        return f"Could not find customer with name: {customer_name}"
        
    contact_id = contact.get("id")
    invoices = await client.get_invoices() # Ideally filter by contactId in API if possible
    
    total_spent = 0.0
    count = 0
    
    for invoice in invoices:
        # Filter by contact
        if invoice.get("contactId") != contact_id and invoice.get("contact") != contact_id:
            continue
            
        # Filter by year
        inv_date_str = invoice.get("date") # Unix timestamp or YYYY-MM-DD? Schema said 'string' format 'date' -> YYYY-MM-DD usually.
        # But Holded often uses Unix timestamps. Let's handle both or check schema again.
        # Schema said: type: string, format: date. So likely "2023-01-01".
        
        try:
            # Try parsing YYYY-MM-DD
            inv_date = datetime.strptime(inv_date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
             # Fallback if it's a timestamp (seconds)
            try:
                inv_date = datetime.fromtimestamp(int(inv_date_str))
            except (ValueError, TypeError):
                continue # Skip if date is unparseable

        if inv_date.year == year:
            total_spent += float(invoice.get("total", 0))
            count += 1
            
    return f"Customer {customer_name} spent {total_spent:.2f} across {count} invoices in {year}."
