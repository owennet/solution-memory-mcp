"""list_tags MCP tool implementation."""

from typing import Any
from ..storage.sqlite_store import SQLiteStore


async def list_tags(
    sqlite_store: SQLiteStore,
    category: str | None = None,
) -> dict[str, Any]:
    """List all tags with solution counts.
    
    Args:
        sqlite_store: SQLite storage instance
        category: Optional category filter ('tech_stack', 'problem_type', 'error_code')
        
    Returns:
        Dict with tags list
    """
    # Validate category
    valid_categories = ("tech_stack", "problem_type", "error_code")
    if category and category not in valid_categories:
        return {
            "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        }
    
    tags = sqlite_store.list_tags(category)
    
    return {
        "tags": [
            {
                "name": t.name,
                "category": t.category,
                "count": t.count
            }
            for t in tags
        ]
    }


TOOL_DEFINITION = {
    "name": "list_tags",
    "description": "List all tags in the solution memory, optionally filtered by category. Useful for browsing solutions by technology or problem type.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["tech_stack", "problem_type", "error_code"],
                "description": "Optional category filter"
            }
        },
        "required": []
    }
}
