"""Authentication module - Bearer token validation."""
from functools import wraps
from flask import request, current_app


class AuthError(Exception):
    """Authentication error."""
    
    def __init__(self, message: str = "Invalid or missing token"):
        self.message = message
        super().__init__(self.message)


def require_token(f):
    """Decorator to require Bearer token authentication.
    
    Usage:
        @bp.route('/protected')
        @require_token
        def protected_endpoint():
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            raise AuthError("Missing Authorization header")
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthError("Invalid Authorization header format. Use: Bearer <token>")
        
        token = parts[1]
        expected_token = current_app.config.get('API_TOKEN', '')
        
        if not expected_token:
            raise AuthError("API_TOKEN not configured on server")
        
        if token != expected_token:
            raise AuthError("Invalid token")
        
        return f(*args, **kwargs)
    
    return decorated
