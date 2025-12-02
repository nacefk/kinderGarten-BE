"""
Custom middleware to exempt API endpoints from CSRF protection.
API endpoints use JWT authentication, not session cookies, so CSRF protection is not needed.
This is essential for React Native and other non-browser clients.
"""

from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import decorator_from_middleware_with_args


class DisableCSRFForAPIMiddleware(CsrfViewMiddleware):
    """
    Custom CSRF middleware that disables CSRF protection for /api/ endpoints.
    These endpoints use JWT token authentication instead of session cookies,
    making CSRF attacks not applicable.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Disable CSRF for all /api/ endpoints
        if request.path.startswith("/api/"):
            return None  # Skip CSRF check

        # Apply normal CSRF check for other endpoints (admin, etc.)
        return super().process_view(request, view_func, view_args, view_kwargs)
