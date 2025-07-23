from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Custom HTTP exception handler that returns a JSON response.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
