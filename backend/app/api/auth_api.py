"""Auth API endpoints - login, refresh, logout."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from ..extensions import db, limiter
from ..auth import authenticate_user, create_tokens, get_current_user, AuthError
from ..models import User
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'auth',
    __name__,
    url_prefix='/api/auth',
    description='Authentication'
)


class LoginSchema(Schema):
    """Login request schema."""
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


class TokenResponseSchema(Schema):
    """Token response schema."""
    access_token = fields.String()
    refresh_token = fields.String()
    user = fields.Dict()


class AccessTokenResponseSchema(Schema):
    """Access token refresh response."""
    access_token = fields.String()


class UserResponseSchema(Schema):
    """Current user response."""
    id = fields.Integer()
    username = fields.String()
    role = fields.String()
    is_active = fields.Boolean()


@blp.route('/login')
class Login(MethodView):
    """User login endpoint."""
    
    @blp.arguments(LoginSchema)
    @blp.response(200, TokenResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid credentials')
    @limiter.limit("6 per minute")
    def post(self, credentials):
        """Authenticate user and return JWT tokens.
        
        Returns access_token (15 min) and refresh_token (30 days).
        """
        user = authenticate_user(
            username=credentials['username'],
            password=credentials['password']
        )
        tokens = create_tokens(user)
        return tokens


@blp.route('/refresh')
class Refresh(MethodView):
    """Token refresh endpoint."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, AccessTokenResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid refresh token')
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token using refresh token.
        
        Send refresh_token in Authorization header: Bearer <refresh_token>
        Returns new access_token.
        """
        try:
            user = get_current_user()
            
            # Create new access token with updated claims
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(
                identity=str(user.id),  # Must be string
                additional_claims={
                    'role': user.role,
                    'username': user.username
                }
            )
            
            return {'access_token': access_token}
            
        except AuthError as e:
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': {}
                }
            }, 401


@blp.route('/me')
class CurrentUser(MethodView):
    """Get current authenticated user."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, UserResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Not authenticated')
    @jwt_required()
    def get(self):
        """Get current user info from JWT."""
        try:
            user = get_current_user()
            return user.to_dict()
        except AuthError as e:
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': {}
                }
            }, 401
