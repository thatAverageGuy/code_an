import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate a request ID
        request_id = str(time.time())
        
        # Log the request
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        # Measure request processing time
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log the response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"(processed in {process_time:.4f}s)"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
        
        except Exception as e:
            # Log any exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: {str(e)} "
                f"(processed in {process_time:.4f}s)"
            )
            raise