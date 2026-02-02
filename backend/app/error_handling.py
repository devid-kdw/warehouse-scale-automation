"""Centralized error handling with standard error format."""
from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError

from .auth import AuthError


# Error codes mapping
ERROR_CODES = {
    'INVALID_TOKEN': 401,
    'VALIDATION_ERROR': 400,
    'DRAFT_NOT_FOUND': 404,
    'DRAFT_NOT_DRAFT': 409,
    'DUPLICATE_EVENT_ID': 409,
    'INVALID_BATCH_FORMAT': 400,
    'INSUFFICIENT_STOCK': 409,
    'ARTICLE_NOT_FOUND': 404,
    'BATCH_NOT_FOUND': 404,
    'LOCATION_NOT_FOUND': 404,
    'USER_NOT_FOUND': 404,
    'INTERNAL_ERROR': 500,
}


def error_response(code: str, message: str, details: dict = None, status_code: int = None):
    """Create a standard error response.
    
    Args:
        code: Error code (e.g., 'VALIDATION_ERROR')
        message: Human-readable error message
        details: Optional additional details
        status_code: HTTP status code (defaults to ERROR_CODES mapping)
    
    Returns:
        Tuple of (response, status_code)
    """
    if status_code is None:
        status_code = ERROR_CODES.get(code, 500)
    
    response = {
        'error': {
            'code': code,
            'message': message,
            'details': details or {}
        }
    }
    
    return jsonify(response), status_code


class AppError(Exception):
    """Base application error."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


def register_error_handlers(app):
    """Register error handlers on Flask app."""
    
    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        return error_response('INVALID_TOKEN', error.message)
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return error_response(error.code, error.message, error.details)
    
    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(error):
        return error_response(
            'VALIDATION_ERROR',
            'Request validation failed',
            {'fields': error.messages}
        )
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        # Check for unique constraint violations
        error_str = str(error.orig).lower()
        
        if 'client_event_id' in error_str:
            return error_response(
                'DUPLICATE_EVENT_ID',
                'A draft with this client_event_id already exists'
            )
        
        return error_response(
            'VALIDATION_ERROR',
            'Database constraint violation',
            {'detail': str(error.orig)}
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response(
            'VALIDATION_ERROR',
            'Resource not found',
            status_code=404
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return error_response(
            'INTERNAL_ERROR',
            'An internal error occurred'
        )
