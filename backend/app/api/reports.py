"""Reports API endpoints."""
from datetime import datetime, timezone
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Stock, Surplus, Transaction, Location, Article, Batch
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
    @jwt_required()
    def get(self, query_args):
        """Get inventory report.
        
        Returns current stock and surplus levels grouped by location/article/batch.
        """
        # Build stock query
        stock_query = db.session.query(Stock)
        surplus_query = db.session.query(Surplus)
        
        if query_args.get('location_id'):
            stock_query = stock_query.filter_by(location_id=query_args['location_id'])
            surplus_query = surplus_query.filter_by(location_id=query_args['location_id'])
        
        if query_args.get('article_id'):
            stock_query = stock_query.filter_by(article_id=query_args['article_id'])
            surplus_query = surplus_query.filter_by(article_id=query_args['article_id'])
        
        stocks = stock_query.all()
        surpluses = surplus_query.all()
        
        # Build combined inventory map
        inventory_map = {}
        
        for stock in stocks:
            key = (stock.location_id, stock.article_id, stock.batch_id)
            inventory_map[key] = {
                'location_id': stock.location_id,
                'location_code': stock.location.code if stock.location else None,
                'article_id': stock.article_id,
                'article_no': stock.article.article_no if stock.article else None,
                'batch_id': stock.batch_id,
                'batch_code': stock.batch.batch_code if stock.batch else None,
                'stock_kg': float(stock.quantity_kg),
                'surplus_kg': 0.0
            }
        
        for surplus in surpluses:
            key = (surplus.location_id, surplus.article_id, surplus.batch_id)
            if key in inventory_map:
                inventory_map[key]['surplus_kg'] = float(surplus.quantity_kg)
            else:
                inventory_map[key] = {
                    'location_id': surplus.location_id,
                    'location_code': surplus.location.code if surplus.location else None,
                    'article_id': surplus.article_id,
                    'article_no': surplus.article.article_no if surplus.article else None,
                    'batch_id': surplus.batch_id,
                    'batch_code': surplus.batch.batch_code if surplus.batch else None,
                    'stock_kg': 0.0,
                    'surplus_kg': float(surplus.quantity_kg)
                }
        
        items = list(inventory_map.values())
        
        return {
            'items': items,
            'total': len(items),
            'generated_at': datetime.now(timezone.utc).isoformat()
        }


@blp.route('/transactions')
class TransactionReport(MethodView):
    """Transaction report resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ReportQuerySchema, location='query')
    @blp.response(200, TransactionReportSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    def get(self, query_args):
        """Get transaction report.
        
        Returns transaction history for audit purposes.
        """
        query = Transaction.query
        
        if query_args.get('location_id'):
            query = query.filter_by(location_id=query_args['location_id'])
        
        if query_args.get('article_id'):
            query = query.filter_by(article_id=query_args['article_id'])
        
        if query_args.get('from_date'):
            query = query.filter(Transaction.occurred_at >= query_args['from_date'])
        
        if query_args.get('to_date'):
            query = query.filter(Transaction.occurred_at <= query_args['to_date'])
        
        transactions = query.order_by(Transaction.occurred_at.desc()).limit(1000).all()
        
        return {
            'items': [tx.to_dict() for tx in transactions],
            'total': len(transactions),
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
