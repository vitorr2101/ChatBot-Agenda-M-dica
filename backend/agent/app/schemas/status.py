from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    input_schema: dict = Field(
        default_factory=dict,
        description="Input schema for the tool, if applicable"
    )

class StatusResponse(BaseModel):
    """
    Represents the status response of the application.
    """
    status: str = Field(..., description="Current status of the application")
    timestamp: str = Field(..., description="Timestamp of the status check in ISO 8601 format")
    tools: list[ToolResponse] = Field(
        default_factory=list,
        description="List of available tools in the application"
    )
    count_tools: int = Field(
        default=0,
        description="Count of available tools"
    )
    mcp_server_status: str = Field(
        default="disconnected",
        description="Status of the MCP server connection"
    )
