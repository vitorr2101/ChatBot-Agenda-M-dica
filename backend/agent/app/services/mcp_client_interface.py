from abc import ABC, abstractmethod
from mcp import ClientSession
from mcp.types import Tool
from typing import List


class MCPClientInterface(ABC):
    """
    Interface for MCP clients.
    """

    @abstractmethod
    async def connect(self) -> ClientSession:
        """
        Connect to the MCP server and initialize the session.
        
        Returns:
            ClientSession: The initialized client session.
            
        Raises:
            Exception: If connection fails.
        """
        pass

    @abstractmethod
    async def disconnect(self):
        """
        Disconnect from the MCP server.
        """
        pass

    @abstractmethod
    async def list_tools(self) -> List[Tool]:
        """
        List available tools from the MCP server.
        
        Returns:
            List[Tool]: List of available tools.
            
        Raises:
            RuntimeError: If not connected to server.
            Exception: If listing tools fails.
        """
        pass
