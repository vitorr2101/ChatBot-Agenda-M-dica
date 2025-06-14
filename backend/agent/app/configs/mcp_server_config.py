from .settings import MCP_SERVER_DIR

MCP_SERVERS = {
    "Medical Appointment System": {
        "command": "python3",
        "args": [MCP_SERVER_DIR],
        "env": {},
        "description": "Medical appointment scheduling server"
    }
}