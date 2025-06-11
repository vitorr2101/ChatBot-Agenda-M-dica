from .settings import MCP_SERVER_DIR

MCP_SERVERS = {}

MCP_SERVERS["Medical Appointment System"] = {
     "command": "python",
     "args": ["/home/vitor/Programas/pythonArea/projetoFabiano/ChatBot-Agenda-M-dica/backend/agent/app/server.py"],
     "env": {},
     "description": "Local Python MCP server"
 }