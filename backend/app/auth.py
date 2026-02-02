"""Authentication module - Bearer token validation."""
from functools import wraps
from flask import request, current_app


class AuthError(Exception):
    """Authentication error."""
    
    def __init__(self, message: str = "Invalid or missing token"):
        self.message = message
        super().__init__(self.message)


def validate_token_config():
    """Validate API token configuration at startup.
    
    In production, API_TOKEN must be set.
    In development, empty token is only allowed if ALLOW_NO_AUTH_IN_DEV is true.
    
    Raises:
        RuntimeError: If token configuration is invalid for the environment.
    """
    env = current_app.config.get('ENV', 'development')
    api_token = current_app.config.get('API_TOKEN', '')
    allow_no_auth = current_app.config.get('ALLOW_NO_AUTH_IN_DEV', False)
    
    if env == 'production' and not api_token:
        raise RuntimeError(
            "SECURITY ERROR: API_TOKEN must be set in production environment. "
            "Set API_TOKEN environment variable or refuse to start."
        )
    
    if env != 'production' and not api_token and not allow_no_auth:
        current_app.logger.warning(
            "WARNING: API_TOKEN is empty. Set ALLOW_NO_AUTH_IN_DEV=true to allow "
            "unauthenticated requests in development, or set API_TOKEN."
        )


def require_token(f):
    """Decorator to require Bearer token authentication.
    
    Behavior:
    - In production: Always requires valid Bearer token
    - In development with ALLOW_NO_AUTH_IN_DEV=true and empty API_TOKEN: Allows requests
    - Otherwise: Requires valid Bearer token
    
    Usage:
        @bp.route('/protected')
        @require_token
        def protected_endpoint():
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        env = current_app.config.get('ENV', 'development')
        expected_token = current_app.config.get('API_TOKEN', '')
        allow_no_auth = current_app.config.get('ALLOW_NO_AUTH_IN_DEV', False)
        
        # Dev convenience: skip auth if no token configured and explicitly allowed
        if env != 'production' and not expected_token and allow_no_auth:
            return f(*args, **kwargs)
        
        # Production with no token configured - reject all requests
        if not expected_token:
            raise AuthError("API_TOKEN not configured on server")
        
        # Standard token validation
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            raise AuthError("Missing Authorization header")
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthError("Invalid Authorization header format. Use: Bearer <token>")
        
        token = parts[1]
        
        if token != expected_token:
            raise AuthError("Invalid token")
        
        return f(*args, **kwargs)
    
    return decorated
