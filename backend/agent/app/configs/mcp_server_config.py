from .settings import MCP_SERVER_DIR

MCP_SERVERS = {
    "Medical Appointment System": {
        "command": "uv",
        "args": [
            "--directory",
            MCP_SERVER_DIR,
            "run",
            "main.py"
        ],
        "description": "Medical appointment scheduling server"
    }
}