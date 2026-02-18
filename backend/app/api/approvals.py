from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from marshmallow import Schema

from ..extensions import db
from ..auth import require_roles
from ..services.approval_service import (
    approve_draft, reject_draft, 
    get_daily_approvals_list, get_daily_approvals_detail,
    update_aggregate_quantity, approve_day, reject_day
)
from ..error_handling import AppError, InsufficientStockError
from ..schemas.approvals import (
    ApprovalRequestSchema, ApprovalResponseSchema,
    DailyApprovalSummarySchema, DailyApprovalDetailSchema,
    DailyAggregateEditSchema, DailyActionResponseSchema
)
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'approvals',
    __name__,
    url_prefix='/api/drafts',
    description='Draft approval/rejection'
)


@blp.route('/<int:draft_id>/approve')
class ApproveDraft(MethodView):
    """Approve a draft."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ApprovalRequestSchema)
    @blp.response(200, ApprovalResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft or user not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Draft not in DRAFT status or insufficient stock')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, approval_data, draft_id):
        """Approve a draft with atomic inventory update.
        
        Requires ADMIN role. Actor is determined from JWT token.
        
        Applies surplus-first consumption logic:
        1. Uses available surplus first
        2. Then consumes from stock
        3. Fails if combined inventory is insufficient
        
        Creates transaction records for audit trail.
        """
        # Get actor from JWT instead of request body (JWT identity is string, convert to int)
        actor_user_id = int(get_jwt_identity())
        
        result = approve_draft(
            draft_id=draft_id,
            actor_user_id=actor_user_id,
            note=approval_data.get('note')
        )
        db.session.commit()
        
        return {
            'message': 'Draft approved successfully',
            'draft_id': result['draft_id'],
            'new_status': result['new_status'],
            'consumed_surplus': result['consumed_surplus'],
            'consumed_stock': result['consumed_stock'],
            'action': result['approval_action']
        }


@blp.route('/<int:draft_id>/reject')
class RejectDraft(MethodView):
    """Reject a draft."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ApprovalRequestSchema)
    @blp.response(200, ApprovalResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft or user not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Draft not in DRAFT status')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, approval_data, draft_id):
        """Reject a draft.
        
        Requires ADMIN role. Actor is determined from JWT token.
        No inventory changes occur on rejection.
        """
        # Get actor from JWT instead of request body (JWT identity is string, convert to int)
        actor_user_id = int(get_jwt_identity())
        
        result = reject_draft(
            draft_id=draft_id,
            actor_user_id=actor_user_id,
            note=approval_data.get('note')
        )
        db.session.commit()
        
        return {
            'message': 'Draft rejected successfully',
            'draft_id': result['draft_id'],
            'new_status': result['new_status'],
            'action': result.get('approval_action')  # Already a dict
        }


@blp.route('/daily')
class DailyApprovals(MethodView):
    """Daily approvals list."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DailyApprovalSummarySchema(many=True))
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """List operational days with pending drafts."""
        return get_daily_approvals_list()


@blp.route('/daily/<date>/<int:location_id>')
class DailyApprovalsDetail(MethodView):
    """Daily approvals detail for a location."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DailyApprovalDetailSchema(many=True))
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, date, location_id):
        """Get aggregated Article+Batch lines for a specific day and location."""
        return get_daily_approvals_detail(date, location_id)


@blp.route('/daily/<date>/<int:location_id>/approve')
class DailyApprove(MethodView):
    """Mass approve a day's drafts."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DailyActionResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, date, location_id):
        """Approve all drafts for a specific day and location atomically."""
        actor_user_id = int(get_jwt_identity())
        result = approve_day(date, location_id, actor_user_id)
        db.session.commit()
        return result


@blp.route('/daily/<date>/<int:location_id>/reject')
class DailyReject(MethodView):
    """Mass reject a day's drafts."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DailyActionResponseSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, date, location_id):
        """Reject all drafts for a specific day and location atomically."""
        actor_user_id = int(get_jwt_identity())
        result = reject_day(date, location_id, actor_user_id)
        db.session.commit()
        return result


@blp.route('/daily/<date>/<int:location_id>/lines')
class DailyLinesEdit(MethodView):
    """Edit aggregate quantity for a line in the daily queue."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(DailyAggregateEditSchema)
    @blp.response(200, schema=Schema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @jwt_required()
    @require_roles('ADMIN')
    def patch(self, edit_data, date, location_id):
        """Edit aggregate quantity (Delta Adjustment rule)."""
        actor_user_id = int(get_jwt_identity())
        result = update_aggregate_quantity(
            date_str=date,
            location_id=location_id,
            article_id=edit_data['article_id'],
            batch_id=edit_data['batch_id'],
            new_total_qty=Decimal(str(edit_data['new_total_qty'])),
            actor_user_id=actor_user_id
        )
        db.session.commit()
        return result
