"""Authentication module - JWT authentication and RBAC."""
from functools import wraps
from flask import current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)

from .extensions import db
from .models import User


class AuthError(Exception):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed", code: str = "AUTH_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


def authenticate_user(username: str, password: str) -> User:
    """Authenticate user with username and password.
    
    Args:
        username: User's username
        password: Plain text password
        
    Returns:
        User object if authenticated
        
    Raises:
        AuthError: If authentication fails
    """
    user = User.query.filter_by(username=username).first()
    
    if not user:
        raise AuthError("Invalid username or password", "INVALID_CREDENTIALS")
    
    if not user.is_active:
        raise AuthError("Account is disabled", "ACCOUNT_DISABLED")
    
    if not user.check_password(password):
        raise AuthError("Invalid username or password", "INVALID_CREDENTIALS")
    
    return user


def create_tokens(user: User) -> dict:
    """Create access and refresh tokens for user.
    
    Args:
        user: Authenticated user
        
    Returns:
        Dict with access_token, refresh_token, and user info
    """
    # Include user role in JWT claims
    additional_claims = {
        'role': user.role,
        'username': user.username
    }
    
    access_token = create_access_token(
        identity=str(user.id),  # Must be string
        additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),  # Must be string
        additional_claims=additional_claims
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }


def get_current_user() -> User:
    """Get current authenticated user from JWT.
    
    Returns:
        User object
        
    Raises:
        AuthError: If user not found
    """
    user_id = get_jwt_identity()  # Returns string
    user = db.session.get(User, int(user_id))  # Convert to int for DB lookup
    
    if not user:
        raise AuthError("User not found", "USER_NOT_FOUND")
    
    if not user.is_active:
        raise AuthError("Account is disabled", "ACCOUNT_DISABLED")
    
    return user


def require_roles(*allowed_roles):
    """Decorator to require specific roles for endpoint access.
    
    Usage:
        @bp.route('/admin-only')
        @jwt_required()
        @require_roles('ADMIN')
        def admin_endpoint():
            ...
    
    Args:
        allowed_roles: Tuple of allowed role strings
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return {
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': f'Access denied. Required roles: {", ".join(allowed_roles)}',
                        'details': {'user_role': user_role, 'required_roles': list(allowed_roles)}
                    }
                }, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Legacy decorator for backward compatibility during transition
def require_token(f):
    """Legacy token decorator - now wraps jwt_required.
    
    This maintains backward compatibility during migration.
    Will be removed in future version.
    """
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated
