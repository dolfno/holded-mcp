# Holded MCP Server

An MCP server for Holded, providing tools to query outstanding invoices and customer spending.

## Tools

- `get_outstanding_invoices`: List unpaid invoices.
- `get_customer_spending`: Calculate customer spending by year.

## Setup

1. Install dependencies: `uv sync`
2. Set `HOLDED_API_KEY` in `.env`.
3. Run: `uv run fastmcp run main.py`
