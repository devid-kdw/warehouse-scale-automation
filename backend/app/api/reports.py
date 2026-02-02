"""Reports API endpoints (stubs)."""
from datetime import datetime, timezone
from flask.views import MethodView
from flask_smorest import Blueprint

from ..auth import require_token
from ..schemas.reports import (
    InventoryReportSchema, TransactionReportSchema, ReportQuerySchema
)
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'reports',
    __name__,
    url_prefix='/api/reports',
    description='Inventory and transaction reports'
)


@blp.route('/inventory')
class InventoryReport(MethodView):
    """Inventory report resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, InventoryReportSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @require_token
    def get(self, query_args):
        """Get inventory report.
        
        Returns current stock and surplus levels.
        
        **Note: This is a stub - full implementation pending.**
        """
        # Stub response
        return {
            'error': {
                'code': 'NOT_IMPLEMENTED',
                'message': 'Inventory report not yet implemented',
                'details': {'endpoint': '/api/reports/inventory'}
            }
        }, 501


@blp.route('/transactions')
class TransactionReport(MethodView):
    """Transaction report resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, TransactionReportSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @require_token
    def get(self, query_args):
        """Get transaction report.
        
        Returns transaction history for audit purposes.
        
        **Note: This is a stub - full implementation pending.**
        """
        # Stub response
        return {
            'error': {
                'code': 'NOT_IMPLEMENTED',
                'message': 'Transaction report not yet implemented',
                'details': {'endpoint': '/api/reports/transactions'}
            }
        }, 501
