"""Drafts API endpoints."""
from decimal import Decimal, ROUND_HALF_UP
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..auth import require_roles
from ..models import WeighInDraft, Location, Article, Batch
from ..schemas.drafts import (
    DraftSchema, DraftCreateSchema, DraftUpdateSchema,
    DraftQuerySchema, DraftListSchema
)
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'drafts',
    __name__,
    url_prefix='/api/drafts',
    description='Weigh-in drafts management'
)


@blp.route('')
class DraftList(MethodView):
    """Draft collection resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(DraftQuerySchema, location='query')
    @blp.response(200, DraftListSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @jwt_required()
    def get(self, query_args):
        """List drafts.
        
        Filter by status, location_id, or article_id.
        Accessible by ADMIN and OPERATOR.
        """
        query = WeighInDraft.query
        
        if query_args.get('status'):
            query = query.filter_by(status=query_args['status'])
        if query_args.get('location_id'):
            query = query.filter_by(location_id=query_args['location_id'])
        if query_args.get('article_id'):
            query = query.filter_by(article_id=query_args['article_id'])
        
        drafts = query.order_by(WeighInDraft.created_at.desc()).all()
        
        return {
            'items': drafts,
            'total': len(drafts)
        }
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(DraftCreateSchema)
    @blp.response(201, DraftSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Location/Article/Batch not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Duplicate client_event_id')
    @jwt_required()
    def post(self, draft_data):
        """Create a new draft.
        
        Accessible by ADMIN and OPERATOR.
        Uses JWT identity as created_by_user_id.
        Requires client_event_id for idempotency.
        Quantity must be between 0.01 and 9999.99 kg.
        
        Backward compatibility: Auto-creates a DraftGroup for this single draft.
        """
        from ..services import draft_group_service
        
        # Get user from JWT
        current_user_id = int(get_jwt_identity())
        
        # Validate existence (basic check before service call)
        location = db.session.get(Location, draft_data['location_id'])
        if not location:
            return {'error': {'code': 'LOCATION_NOT_FOUND', 'message': f"Location ID {draft_data['location_id']} not found", 'details': {}}}, 404
            
        # Article/Batch check (optional, but good for error reporting before service)
        article = db.session.get(Article, draft_data['article_id'])
        if not article:
            return {'error': {'code': 'ARTICLE_NOT_FOUND', 'message': f"Article ID {draft_data['article_id']} not found", 'details': {}}}, 404
        
        batch = db.session.get(Batch, draft_data['batch_id'])
        if not batch:
            return {'error': {'code': 'BATCH_NOT_FOUND', 'message': f"Batch ID {draft_data['batch_id']} not found", 'details': {}}}, 404

        # Check for duplicate client_event_id (idempotency)
        existing = WeighInDraft.query.filter_by(
            client_event_id=draft_data['client_event_id']
        ).first()
        if existing:
            return {
                'error': {
                    'code': 'DUPLICATE_EVENT_ID',
                    'message': 'A draft with this client_event_id already exists',
                    'details': {'client_event_id': draft_data['client_event_id']}
                }
            }, 409

        # Use group service to create a 1-line group
        line = {
            'article_id': draft_data['article_id'],
            'batch_id': draft_data['batch_id'],
            'quantity_kg': draft_data['quantity_kg'],
            'draft_type': draft_data.get('draft_type', WeighInDraft.DRAFT_TYPE_WEIGH_IN),
            'client_event_id': draft_data['client_event_id'],
            'note': draft_data.get('note')
        }
        
        group = draft_group_service.create_group(
            location_id=draft_data['location_id'],
            user_id=current_user_id,
            lines=[line],
            source='ui_operator'
        )
        
        # Return the created draft (first and only one in group)
        return group.drafts[0], 201


@blp.route('/<int:draft_id>')
class DraftDetail(MethodView):
    """Single draft resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DraftSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft not found')
    @jwt_required()
    def get(self, draft_id):
        """Get draft by ID."""
        draft = db.session.get(WeighInDraft, draft_id)
        if not draft:
            return {
                'error': {
                    'code': 'DRAFT_NOT_FOUND',
                    'message': f'Draft {draft_id} not found',
                    'details': {}
                }
            }, 404
        return draft
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(DraftUpdateSchema)
    @blp.response(200, DraftSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Draft not in DRAFT status')
    @jwt_required()
    def patch(self, update_data, draft_id):
        """Update a draft.
        
        Only drafts in DRAFT status can be updated.
        """
        draft = db.session.get(WeighInDraft, draft_id)
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
                    'message': f'Cannot update draft with status {draft.status}',
                    'details': {'current_status': draft.status}
                }
            }, 409
        
        # Update fields
        if 'quantity_kg' in update_data:
            quantity = Decimal(str(update_data['quantity_kg'])).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
            draft.quantity_kg = quantity
        
        if 'note' in update_data:
            draft.note = update_data['note']
        
        db.session.commit()
        
        return draft
