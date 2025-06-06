from fastapi import Request

from .services.orchestrator import ChatOrchestrator

def get_orchestrator(request: Request) -> ChatOrchestrator:
    return request.app.state.orchestrator
