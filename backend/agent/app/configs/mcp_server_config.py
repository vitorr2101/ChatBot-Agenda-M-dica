from .settings import MCP_SERVER_DIR, MONGODB_NAME, MONGODB_URI

MCP_SERVERS = {}

if MCP_SERVER_DIR:
    MCP_SERVERS["Medical Appointment System"] = {
        "command": ".venv/bin/python",
        "args": [
            "server.py"
        ],
        "cwd": MCP_SERVER_DIR,
        "env": {
            "MONGODB_URI": MONGODB_URI,
            "MONGODB_DB_NAME": MONGODB_NAME
        },
        "description": "Medical appointment scheduling server"
    }
else:
    print("Warning: MCP_SERVER_DIR not set. MCP server will not be available.")