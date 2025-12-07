from fastmcp import FastMCP
from holded_mcp.tools import get_outstanding_invoices, get_customer_spending

# Initialize FastMCP server
mcp = FastMCP("Holded MCP")

# Register tools
mcp.tool()(get_outstanding_invoices)
mcp.tool()(get_customer_spending)

if __name__ == "__main__":
    mcp.run()
