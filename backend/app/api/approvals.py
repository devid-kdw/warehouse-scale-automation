"""Approvals API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint

from ..extensions import db
from ..auth import require_token
from ..models import WeighInDraft, ApprovalAction, User
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
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Draft not in DRAFT status')
    @require_token
    def post(self, approval_data, draft_id):
        """Approve a draft.
        
        Only drafts in DRAFT status can be approved.
        This is a stub - full implementation will update stock/surplus.
        """
        # Lock draft for update
        draft = db.session.query(WeighInDraft).filter_by(id=draft_id).with_for_update().first()
        if not draft:
            return {
                'error': {
                    'code': 'DRAFT_NOT_FOUND',
                    'message': f'Draft {draft_id} not found',
                    'details': {}
                }
            }, 404
        
        if draft.status != 'DRAFT':
            return {
                'error': {
                    'code': 'DRAFT_NOT_DRAFT',
                    'message': f'Cannot approve draft with status {draft.status}',
                    'details': {'current_status': draft.status}
                }
            }, 409
        
        # Validate actor user exists
        user = User.query.get(approval_data['actor_user_id'])
        if not user:
            return {
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': f"User ID {approval_data['actor_user_id']} not found",
                    'details': {}
                }
            }, 404
        
        # Create approval action
        action = ApprovalAction(
            draft_id=draft_id,
            action='APPROVE',
            actor_user_id=approval_data['actor_user_id'],
            old_value={'status': draft.status},
            new_value={'status': 'APPROVED'},
            note=approval_data.get('note')
        )
        
        # Update draft status
        draft.status = 'APPROVED'
        
        db.session.add(action)
        db.session.commit()
        
        return {
            'message': 'Draft approved successfully',
            'draft_id': draft_id,
            'new_status': 'APPROVED',
            'action': action.to_dict()
        }


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
        
        Only drafts in DRAFT status can be rejected.
        """
        # Lock draft for update
        draft = db.session.query(WeighInDraft).filter_by(id=draft_id).with_for_update().first()
        if not draft:
            return {
                'error': {
                    'code': 'DRAFT_NOT_FOUND',
                    'message': f'Draft {draft_id} not found',
                    'details': {}
                }
            }, 404
        
        if draft.status != 'DRAFT':
            return {
                'error': {
                    'code': 'DRAFT_NOT_DRAFT',
                    'message': f'Cannot reject draft with status {draft.status}',
                    'details': {'current_status': draft.status}
                }
            }, 409
        
        # Validate actor user exists
        user = User.query.get(approval_data['actor_user_id'])
        if not user:
            return {
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': f"User ID {approval_data['actor_user_id']} not found",
                    'details': {}
                }
            }, 404
        
        # Create approval action
        action = ApprovalAction(
            draft_id=draft_id,
            action='REJECT',
            actor_user_id=approval_data['actor_user_id'],
            old_value={'status': draft.status},
            new_value={'status': 'REJECTED'},
            note=approval_data.get('note')
        )
        
        # Update draft status
        draft.status = 'REJECTED'
        
        db.session.add(action)
        db.session.commit()
        
        return {
            'message': 'Draft rejected successfully',
            'draft_id': draft_id,
            'new_status': 'REJECTED',
            'action': action.to_dict()
        }
