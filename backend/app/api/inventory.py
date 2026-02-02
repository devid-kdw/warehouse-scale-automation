"""Inventory API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields, validate

from ..extensions import db
from ..auth import require_token
from ..services.inventory_service import adjust_inventory
from ..error_handling import AppError
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'inventory',
    __name__,
    url_prefix='/api/inventory',
    description='Inventory management'
)


class InventoryAdjustSchema(Schema):
    """Schema for inventory adjustment request."""
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
    actor_user_id = fields.Integer(required=True)
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
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Entity not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Negative inventory not allowed')
    @require_token
    def post(self, data):
        """Adjust inventory (stock or surplus).
        
        Admin-only endpoint for manual inventory corrections.
        
        Modes:
        - set: Set absolute value (must be >= 0)
        - delta: Add/subtract from current value (result must be >= 0)
        
        Creates an INVENTORY_ADJUSTMENT transaction for audit trail.
        """
        try:
            result = adjust_inventory(
                location_id=data['location_id'],
                article_id=data['article_id'],
                batch_id=data['batch_id'],
                target=data['target'],
                mode=data['mode'],
                quantity_kg=data['quantity_kg'],
                actor_user_id=data['actor_user_id'],
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
