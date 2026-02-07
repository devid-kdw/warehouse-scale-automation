"""Flask application factory."""
from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, api as smorest_api, jwt, limiter
from .error_handling import register_error_handlers
from .api import register_blueprints
from .cli import register_cli


def create_app(config_class=Config):
    """Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Validate production config
    if hasattr(config_class, 'validate_production_config'):
        config_class.validate_production_config()
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    smorest_api.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS with proper origins
    cors_origins = config_class.get_cors_origins() if hasattr(config_class, 'get_cors_origins') else '*'
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': {
                'code': 'TOKEN_EXPIRED',
                'message': 'Access token has expired',
                'details': {}
            }
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid token',
                'details': {'reason': str(error)}
            }
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': {
                'code': 'MISSING_TOKEN',
                'message': 'Missing Authorization header',
                'details': {}
            }
        }), 401
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register API blueprints
    register_blueprints(smorest_api)
    
    # Register CLI commands
    register_cli(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from . import models  # noqa: F401
    
    return app
