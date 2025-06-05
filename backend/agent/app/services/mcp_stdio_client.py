from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from mcp.types import Tool
from typing import Optional, List
import logging

from .mcp_client_interface import MCPClientInterface


class MCPStdioClient(MCPClientInterface):
    """
    MCP stdio client.
    """
    
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self.session: Optional[ClientSession] = None
        self.stdio_stream = None
        self.read_stream = None
        self.write_stream = None
        self.close_func = None
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> ClientSession:
        """
        Connect to the MCP server and initialize the session.
        """

        if self.is_connected:
            self.logger.warning("Already connected to MCP server")
            return self.session
        
        try:
            self.stdio_stream = stdio_client(
                self.server_params
            )
            self.read_stream, self.write_stream = await self.stdio_stream.__aenter__()
            
            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()
            await self.session.initialize()
            
            self.is_connected = True
            self.logger.info("Successfully connected to MCP server")
            return self.session
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            await self.disconnect()
            raise
    
    async def disconnect(self):
        """
        Disconnect from the MCP server.
        """

        if not self.is_connected:
            return
        
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
        except Exception as e:
            self.logger.error(f"Error closing session: {e}")
        
        try:
            if self.stdio_stream:
                await self.stdio_stream.__aexit__(None, None, None)
        except Exception as e:
            self.logger.error(f"Error closing streams: {e}")
        
        self.session = None
        self.stdio_stream = None
        self.read_stream = None
        self.write_stream = None
        self.close_func = None
        self.is_connected = False
        self.logger.info("Disconnected from MCP server")
    
    async def list_tools(self) -> List[Tool]:
        """
        List available tools.
        """

        if not self.is_connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.list_tools()
            return result.tools if hasattr(result, 'tools') else []
        except Exception as e:
            self.logger.error(f"Error listing tools: {e}")
            raise