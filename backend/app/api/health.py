"""Health check endpoint - public, no auth required."""
import os
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import text

from ..extensions import db

blp = Blueprint(
    'health',
    __name__,
    url_prefix='/health',
    description='Health check endpoint'
)


@blp.route('')
class HealthCheck(MethodView):
    """Health check resource."""
    
    @blp.response(200)
    def get(self):
        """Check API and database health.
        
        Returns:
            Health status including database connectivity, version, and environment
        """
        # Check database connectivity
        db_status = 'connected'
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return {
            'status': 'ok',
            'database': db_status,
            'version': current_app.config.get('API_VERSION', '0.1.0'),
            'environment': current_app.config.get('ENV', os.getenv('ENV', 'development'))
        }
