"""MCP Server for Solution Memory."""

import os
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .storage.sqlite_store import SQLiteStore
from .storage.chroma_store import ChromaStore
from .search.hybrid_search import HybridSearchEngine
from .tools import save_solution, search_solutions, get_solution, list_tags


def get_data_dir() -> Path:
    """Get the data directory for solution memory."""
    data_dir = os.environ.get("SOLUTION_MEMORY_PATH", "~/.solution-memory")
    return Path(data_dir).expanduser()


# Initialize storage (ChromaStore uses lazy loading for embedding model)
data_dir = get_data_dir()
sqlite_store = SQLiteStore(data_dir / "solutions.db")
chroma_store = ChromaStore(data_dir / "chroma")  # Embedding model loads on first use
search_engine = HybridSearchEngine(sqlite_store, chroma_store)

# Create MCP server
server = Server("solution-memory")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name=save_solution.TOOL_DEFINITION["name"],
            description=save_solution.TOOL_DEFINITION["description"],
            inputSchema=save_solution.TOOL_DEFINITION["inputSchema"]
        ),
        Tool(
            name=search_solutions.TOOL_DEFINITION["name"],
            description=search_solutions.TOOL_DEFINITION["description"],
            inputSchema=search_solutions.TOOL_DEFINITION["inputSchema"]
        ),
        Tool(
            name=get_solution.TOOL_DEFINITION["name"],
            description=get_solution.TOOL_DEFINITION["description"],
            inputSchema=get_solution.TOOL_DEFINITION["inputSchema"]
        ),
        Tool(
            name=list_tags.TOOL_DEFINITION["name"],
            description=list_tags.TOOL_DEFINITION["description"],
            inputSchema=list_tags.TOOL_DEFINITION["inputSchema"]
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    import json
    
    if name == "save_solution":
        result = await save_solution.save_solution(
            sqlite_store=sqlite_store,
            chroma_store=chroma_store,
            **arguments
        )
    elif name == "search_solutions":
        result = await search_solutions.search_solutions(
            search_engine=search_engine,
            **arguments
        )
    elif name == "get_solution":
        result = await get_solution.get_solution(
            sqlite_store=sqlite_store,
            **arguments
        )
    elif name == "list_tags":
        result = await list_tags.list_tags(
            sqlite_store=sqlite_store,
            **arguments
        )
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
