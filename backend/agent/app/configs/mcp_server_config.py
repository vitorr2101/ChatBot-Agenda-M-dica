from .settings import MCP_SERVER_DIR


MCP_SERVERS = {}

if MCP_SERVER_DIR:
    MCP_SERVERS["Medical Appointment System"] = {
        "command": "uav",
        "args": [
            "--directory",
            MCP_SERVER_DIR,
            "run",
            "server.py"
        ],
        "env": {},
        "description": "Medical appointment scheduling server"
    }