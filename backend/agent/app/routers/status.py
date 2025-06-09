from fastapi import APIRouter, Depends, Request
from datetime import datetime, timezone
from mcp.types import Tool
from typing import List, Optional

from app.schemas.status import StatusResponse
from app.dependencies import get_mcp_client, get_mcp_client_tools
from app.services.mcp_client_interface import MCPClientInterface

router = APIRouter()

@router.get("/", response_model=StatusResponse, summary="Check API status")
async def get_status(
    request: Request,
    mcp_client: Optional[MCPClientInterface] = Depends(get_mcp_client),
    tools: List[Tool] = Depends(get_mcp_client_tools)
):
    """
    Check the status of the API and its components.
    """
    if mcp_client:
        mcp_status = "connected" if mcp_client.is_connected else "disconnected"
    else:
        mcp_status = "not_configured"
    
    tools_formatted = []
    for tool in tools:
        tools_formatted.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        })
    
    return StatusResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        tools=tools_formatted,
        count_tools=len(tools_formatted),
        mcp_server_status=mcp_status
    )