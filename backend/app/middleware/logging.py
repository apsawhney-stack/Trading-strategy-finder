"""
Request/response logging middleware.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("strategy_finder")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get request info
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        
        # Log request
        logger.info(f"→ {method} {path} {query}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(f"← {method} {path} | {response.status_code} | {duration_ms:.1f}ms")
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"✗ {method} {path} | ERROR | {duration_ms:.1f}ms | {str(e)}")
            raise
