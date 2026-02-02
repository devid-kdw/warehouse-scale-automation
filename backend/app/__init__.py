"""Flask application factory."""
from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, api as smorest_api
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
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    smorest_api.init_app(app)
    
    # Enable CORS
    CORS(app)
    
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
