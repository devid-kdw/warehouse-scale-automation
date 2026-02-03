"""Inventory API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate

from ..extensions import db
from ..auth import require_roles
from ..models import Stock, Surplus, Article, Batch, Location
from ..services.inventory_service import adjust_inventory
from ..services import inventory_count_service
from ..error_handling import AppError
from ..schemas.common import ErrorResponseSchema
from ..schemas.inventory import (
    InventorySummaryResponseSchema,
    InventorySummaryQuerySchema,
    InventoryCountRequestSchema,
    InventoryCountResponseSchema
)

blp = Blueprint(
    'inventory',
    __name__,
    url_prefix='/api/inventory',
    description='Inventory management'
)


class InventoryAdjustSchema(Schema):
    """Schema for inventory adjustment request.
    
    Note: actor_user_id removed - taken from JWT token.
    """
    location_id = fields.Integer(required=True)
    article_id = fields.Integer(required=True)
    batch_id = fields.Integer(required=True)
    target = fields.String(
        required=True,
        validate=validate.OneOf(['stock', 'surplus']),
        metadata={'description': 'Target inventory: stock or surplus'}
    )
    mode = fields.String(
        required=True,
        validate=validate.OneOf(['set', 'delta']),
        metadata={'description': 'set = absolute value, delta = relative change'}
    )
    quantity_kg = fields.Float(
        required=True,
        metadata={'description': 'Amount (must be >=0 for set, can be negative for delta)'}
    )
    note = fields.String(
        allow_none=True,
        metadata={'description': 'Reason for adjustment'}
    )


class InventoryAdjustResponseSchema(Schema):
    """Schema for inventory adjustment response."""
    target = fields.String()
    mode = fields.String()
    previous_value = fields.Float()
    new_value = fields.Float()
    delta = fields.Float()
    location_id = fields.Integer()
    article_id = fields.Integer()
    batch_id = fields.Integer()
    transaction = fields.Dict()


@blp.route('/adjust')
class InventoryAdjust(MethodView):
    """Inventory adjustment resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(InventoryAdjustSchema)
    @blp.response(200, InventoryAdjustResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Entity not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Negative inventory not allowed')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, data):
        """Adjust inventory (stock or surplus).
        
        ADMIN-only endpoint for manual inventory corrections.
        Actor is determined from JWT token.
        
        Modes:
        - set: Set absolute value (must be >= 0)
        - delta: Add/subtract from current value (result must be >= 0)
        
        Creates an INVENTORY_ADJUSTMENT transaction for audit trail.
        """
        try:
            # Get actor from JWT
            actor_user_id = get_jwt_identity()
            
            result = adjust_inventory(
                location_id=data['location_id'],
                article_id=data['article_id'],
                batch_id=data['batch_id'],
                target=data['target'],
                mode=data['mode'],
                quantity_kg=data['quantity_kg'],
                actor_user_id=actor_user_id,
                note=data.get('note')
            )
            db.session.commit()
            return result
            
        except AppError as e:
            db.session.rollback()
            status_code = 404 if 'NOT_FOUND' in e.code else (
                409 if 'NEGATIVE' in e.code else 400
            )
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, status_code



@blp.route('/summary')
class InventorySummary(MethodView):
    """Inventory summary resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(InventorySummaryQuerySchema, location='query')
    @blp.response(200, InventorySummaryResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, args):
        """Get inventory summary (stock + surplus).
        
        Returns aggregated view of stock and surplus per batch.
        """
        location_id = args.get('location_id')
        article_id = args.get('article_id')
        batch_id = args.get('batch_id')
        
        # Build query: Batch is the anchor
        query = db.session.query(
            Batch, Article, Stock, Surplus
        ).join(
            Article, Batch.article_id == Article.id
        )
        
        # Outer join stock/surplus
        # If location_id is provided, filter the join
        stock_filter = (Stock.batch_id == Batch.id)
        surplus_filter = (Surplus.batch_id == Batch.id)
        
        if location_id:
            stock_filter &= (Stock.location_id == location_id)
            surplus_filter &= (Surplus.location_id == location_id)
        
        query = query.outerjoin(
            Stock, stock_filter
        ).outerjoin(
            Surplus, surplus_filter
        )
        
        # Apply filters
        if article_id:
            query = query.filter(Batch.article_id == article_id)
        if batch_id:
            query = query.filter(Batch.id == batch_id)
        
        # Only show active batches or batches with stock?
        # For now show all batches that match filters.
        # But usually we want to see only what we have.
        # Let's filter to where stock or surplus exists OR batch is active
        # query = query.filter(
        #     db.or_(
        #         Batch.is_active == True,
        #         Stock.quantity_kg > 0,
        #         Surplus.quantity_kg > 0
        #     )
        # )
        # Keeping it simple: return query results. 
        # But wait, if we don't filter by location in WHERE, and use outer join,
        # we might get multiple rows if multiple locations exist for a batch?
        # Currently Stock/Surplus has location_id.
        # If location_id NOT specified, we might get cartesian product if multiple stocks exist?
        # Specification says "location_id (always 1 for v1)".
        # And "aggregated by (location_id, article_id, batch_id)".
        # If we query Batch, we ignore location if we don't join specifically.
        # If we want detailed list per location, we should query Stock/Surplus primarily.
        
        # Better approach for summary:
        # Union Stock and Surplus keys (loc, art, batch)
        # But standard use case is single location (1).
        # Let's default location_id=1 if not provided, to simplify.
        
        target_location_id = location_id if location_id else 1
        
        # Re-build query with specific location
        query = db.session.query(
            Batch, Article, Stock, Surplus
        ).join(
            Article, Batch.article_id == Article.id
        ).outerjoin(
            Stock, (Stock.batch_id == Batch.id) & (Stock.location_id == target_location_id)
        ).outerjoin(
            Surplus, (Surplus.batch_id == Batch.id) & (Surplus.location_id == target_location_id)
        )
        
        if article_id:
            query = query.filter(Batch.article_id == article_id)
        if batch_id:
            query = query.filter(Batch.id == batch_id)
            
        results = query.all()
        
        items = []
        for batch, article, stock, surplus in results:
            stock_qty = stock.quantity_kg if stock else 0.0
            surplus_qty = surplus.quantity_kg if surplus else 0.0
            
            # Skip if 0 quantity and batch inactive?
            # User wants to see inventory.
            
            # Get location code - simplified, assume target_location_id
            # In real app we might query Location table.
            # But we know ID.
            
            updated_at = None
            if stock and stock.last_updated:
                updated_at = stock.last_updated
            if surplus and surplus.updated_at:
                if not updated_at or surplus.updated_at > updated_at:
                    updated_at = surplus.updated_at
            
            items.append({
                'location_id': target_location_id,
                'location_code': '13', # Hardcoded for v1 as per spec
                'article_id': article.id,
                'article_no': article.article_no,
                'description': article.description,
                'batch_id': batch.id,
                'batch_code': batch.batch_code,
                'expiry_date': batch.expiry_date,
                'stock_qty': float(stock_qty),
                'surplus_qty': float(surplus_qty),
                'total_qty': float(stock_qty + surplus_qty),
                'updated_at': updated_at
            })
            
        return {'items': items, 'total': len(items)}


@blp.route('/count')
class InventoryCount(MethodView):
    """Inventory count resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(InventoryCountRequestSchema)
    @blp.response(200, InventoryCountResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, data):
        """Perform inventory count.
        
        - Adjusts surplus if count > total
        - Resets surplus and creates shortage draft if count < total
        """
        actor_user_id = get_jwt_identity()
        
        try:
            result = inventory_count_service.perform_inventory_count(
                location_id=data['location_id'],
                article_id=data['article_id'],
                batch_id=data['batch_id'],
                counted_total_qty=data['counted_total_qty'],
                actor_user_id=actor_user_id,
                note=data.get('note'),
                client_event_id=data.get('client_event_id')
            )
            db.session.commit()
            return result
        except AppError as e:
            db.session.rollback()
            return {
                'error': {
                    'code': e.error_code,
                    'message': e.message,
                    'details': e.details
                }
            }, e.status_code
