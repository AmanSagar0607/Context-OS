"""
Auth Middleware — API key and JWT authentication.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API requests."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check
        if request.url.path == "/api/v1/health":
            return await call_next(request)

        # TODO: Implement proper auth validation
        # For now, extract user from header or set anonymous
        user_id = request.headers.get("x-user-id", "anonymous")
        request.state.user_id = user_id

        response = await call_next(request)
        return response