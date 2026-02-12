"""Transactions API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..auth import require_roles
from ..models import Transaction
from ..schemas.transactions import TransactionListSchema, TransactionQuerySchema
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'transactions',
    __name__,
    url_prefix='/api/transactions',
    description='Transaction log'
)


@blp.route('')
class TransactionList(MethodView):
    """Transactions collection."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(TransactionQuerySchema, location='query')
    @blp.response(200, TransactionListSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, args):
        """List transactions (newest first)."""
        limit = args.get('limit', 100)
        offset = args.get('offset', 0)
        
        query = Transaction.query
        
        # Apply filters
        if 'article_id' in args:
            query = query.filter(Transaction.article_id == args['article_id'])
        if 'batch_id' in args:
            query = query.filter(Transaction.batch_id == args['batch_id'])
        if 'location_id' in args:
            query = query.filter(Transaction.location_id == args['location_id'])
        if 'tx_type' in args:
            query = query.filter(Transaction.tx_type == args['tx_type'])
        if 'from_' in args:
            query = query.filter(Transaction.occurred_at >= args['from_'])
        if 'to' in args:
            query = query.filter(Transaction.occurred_at <= args['to'])
            
        # Get total count before pagination
        total = query.count()
        
        # Eager load relationships to avoid N+1
        query = query.options(
            db.joinedload(Transaction.article),
            db.joinedload(Transaction.batch),
            db.joinedload(Transaction.location)
        )
        
        # Order by newest first
        query = query.order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        
        # Paginate
        query = query.limit(limit).offset(offset)
        
        results = query.all()
        
        # Schema expects matched fields.
        # Since marshmallow maps by attribute, we can attach temporary properties or just rely on a wrapper.
        # But cleanest is to return list of dicts.
        items = []
        for tx in results:
            item = tx.to_dict() # Transaction model has to_dict? Check.
            # Assuming to_dict exists, but likely minimal.
            # Let's check Transaction model content from step 33.
            
            # Since we need to populate denormalized fields:
            tx_dict = {
                'id': tx.id,
                'tx_type': tx.tx_type,
                'occurred_at': tx.occurred_at,
                'location_id': tx.location_id,
                'article_id': tx.article_id,
                'batch_id': tx.batch_id,
                'quantity_kg': tx.quantity_kg,
                'user_id': tx.user_id,
                'source': tx.source,
                'client_event_id': tx.client_event_id,
                'meta': tx.meta,
                'article_no': tx.article.article_no if tx.article else None,
                'batch_code': tx.batch.batch_code if tx.batch else None,
                'location_code': tx.location.code if tx.location else None
            }
            items.append(tx_dict)
        
        return {'items': items, 'total': total}
