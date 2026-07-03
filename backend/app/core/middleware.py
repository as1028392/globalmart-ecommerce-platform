"""
Middleware components
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """Global error handler middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"Error: {str(exc)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(exc)}
            )

class LoggingMiddleware:
    """Request/response logging middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        start_time = datetime.utcnow()
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
