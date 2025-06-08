from fastapi import Request
from mcp.types import Tool
from typing import List, Optional

from .services.orchestrator import ChatOrchestrator
from .services.llm_client_interface import LLMClientInterface
from .services.mcp_client_interface import MCPClientInterface

def get_orchestrator(request: Request) -> ChatOrchestrator:
    return request.app.state.orchestrator

def get_llm_client(request: Request) -> LLMClientInterface:
    return request.app.state.llm_client

def get_mcp_client(request: Request) -> Optional[MCPClientInterface]:
    return getattr(request.app.state, 'mcp_client', None)

async def get_mcp_client_tools(request: Request) -> List[Tool]:
    mcp_client = getattr(request.app.state, 'mcp_client', None)
    if mcp_client and hasattr(mcp_client, 'list_tools'):
        try:
            return await mcp_client.list_tools()
        except Exception:
            return []
    return []
