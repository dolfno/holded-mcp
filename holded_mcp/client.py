import httpx
import os
from typing import List, Dict, Any, Optional

class HoldedClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("HOLDED_API_KEY")
        if not self.api_key:
            raise ValueError("HOLDED_API_KEY environment variable is not set")
        self.base_url = "https://api.holded.com/api"
        self.headers = {
            "key": self.api_key,
            "Accept": "application/json"
        }

    async def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_invoices(self, page: int = 1) -> List[Dict[str, Any]]:
        """
        Fetches invoices.
        Note: The API endpoint for invoices is /invoicing/v1/documents/invoice
        """
        return await self._get("/invoicing/v1/documents/invoice", params={"page": page})

    async def get_contacts(self, page: int = 1) -> List[Dict[str, Any]]:
        """
        Fetches contacts.
        """
        return await self._get("/invoicing/v1/contacts", params={"page": page})

    async def get_contact_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Helper to find a contact by name.
        This is inefficient as it iterates through pages, but necessary if no search endpoint exists.
        For MVP, we'll check the first few pages.
        """
        # TODO: Implement more robust search or use a search endpoint if available.
        # For now, we'll just check the first page as a simple implementation.
        contacts = await self.get_contacts(page=1)
        for contact in contacts:
            if name.lower() in contact.get("name", "").lower():
                return contact
        return None
