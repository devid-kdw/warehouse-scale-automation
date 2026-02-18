"""Orders API — CRUD and lifecycle management (ADMIN-only)."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from ..extensions import db
from ..auth import require_roles
from ..services import order_service
from ..schemas.orders import (
    OrderSchema, OrderCreateSchema, OrderUpdateSchema,
    OrderListSchema, OrderLineSchema,
)
from ..schemas.common import ErrorResponseSchema

blp = Blueprint('orders', __name__, url_prefix='/api/orders',
                description='Orders management (ADMIN-only)')


@blp.route('')
class OrderCollection(MethodView):
    """Order list and creation."""

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, OrderListSchema)
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """List orders with optional status filter.

        Query params: ?status=OPEN|CLOSED|all (default: all)
        """
        from flask import request
        status = request.args.get('status', 'all')
        orders = order_service.list_orders(status)
        return {'items': orders, 'total': len(orders)}

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(OrderCreateSchema)
    @blp.response(201, OrderSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Duplicate order number')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, order_data):
        """Create a new order.

        If order_number is omitted or set to "auto", generates ORD-xxxx.
        """
        claims = get_jwt()
        user_id = int(claims.get('sub', 0))
        try:
            order = order_service.create_order(order_data, user_id)
            db.session.commit()
            return order, 201
        except Exception as e:
            db.session.rollback()
            if hasattr(e, 'code') and e.code == 'CONFLICT':
                return {
                    'error': {
                        'code': 'CONFLICT',
                        'message': str(e),
                        'details': getattr(e, 'details', {})
                    }
                }, 409
            raise


@blp.route('/<int:order_id>')
class OrderDetail(MethodView):
    """Single order operations."""

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, OrderSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Order not found')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, order_id):
        """Get order detail with lines."""
        order = order_service.get_order(order_id)
        return order

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(OrderUpdateSchema)
    @blp.response(200, OrderSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Order not found')
    @jwt_required()
    @require_roles('ADMIN')
    def put(self, update_data, order_id):
        """Update order header and optionally replace lines."""
        order = order_service.update_order(order_id, update_data)
        db.session.commit()
        return order


@blp.route('/<int:order_id>/lines/<int:line_id>')
class OrderLineRemove(MethodView):
    """Remove a specific order line."""

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, OrderLineSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Line not found')
    @jwt_required()
    @require_roles('ADMIN')
    def delete(self, order_id, line_id):
        """Soft-remove an order line and recalculate order status."""
        line = order_service.remove_line(order_id, line_id)
        db.session.commit()
        return line
