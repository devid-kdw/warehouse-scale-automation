"""Approvals API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint

from ..extensions import db
from ..auth import require_token
from ..services.approval_service import approve_draft, reject_draft
from ..error_handling import AppError, InsufficientStockError
from ..schemas.approvals import ApprovalRequestSchema, ApprovalResponseSchema
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
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft or user not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Draft not in DRAFT status or insufficient stock')
    @require_token
    def post(self, approval_data, draft_id):
        """Approve a draft with atomic inventory update.
        
        Applies surplus-first consumption logic:
        1. Uses available surplus first
        2. Then consumes from stock
        3. Fails if combined inventory is insufficient
        
        Creates transaction records for audit trail.
        """
        try:
            result = approve_draft(
                draft_id=draft_id,
                actor_user_id=approval_data['actor_user_id'],
                note=approval_data.get('note')
            )
            db.session.commit()
            
            return {
                'message': 'Draft approved successfully',
                'draft_id': result['draft_id'],
                'new_status': result['new_status'],
                'consumed_surplus_kg': result['consumed_surplus_kg'],
                'consumed_stock_kg': result['consumed_stock_kg'],
                'action': result['approval_action']
            }
            
        except InsufficientStockError as e:
            db.session.rollback()
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, 409
            
        except AppError as e:
            db.session.rollback()
            status_code = 404 if 'NOT_FOUND' in e.code else 409
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, status_code


@blp.route('/<int:draft_id>/reject')
class RejectDraft(MethodView):
    """Reject a draft."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ApprovalRequestSchema)
    @blp.response(200, ApprovalResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft or user not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Draft not in DRAFT status')
    @require_token
    def post(self, approval_data, draft_id):
        """Reject a draft.
        
        No inventory changes occur on rejection.
        """
        try:
            result = reject_draft(
                draft_id=draft_id,
                actor_user_id=approval_data['actor_user_id'],
                note=approval_data.get('note')
            )
            db.session.commit()
            
            return {
                'message': 'Draft rejected successfully',
                'draft_id': result['draft_id'],
                'new_status': result['new_status'],
                'action': result['approval_action']
            }
            
        except AppError as e:
            db.session.rollback()
            status_code = 404 if 'NOT_FOUND' in e.code else 409
            return {
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }, status_code
