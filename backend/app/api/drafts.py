"""Drafts API endpoints."""
from decimal import Decimal, ROUND_HALF_UP
from flask.views import MethodView
from flask_smorest import Blueprint

from ..extensions import db
from ..auth import require_token
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
    @require_token
    def get(self, query_args):
        """List drafts.
        
        Filter by status, location_id, or article_id.
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
    @require_token
    def post(self, draft_data):
        """Create a new draft.
        
        Requires client_event_id for idempotency.
        Quantity must be between 0.01 and 9999.99 kg.
        """
        # Validate location exists
        location = Location.query.get(draft_data['location_id'])
        if not location:
            return {
                'error': {
                    'code': 'LOCATION_NOT_FOUND',
                    'message': f"Location ID {draft_data['location_id']} not found",
                    'details': {}
                }
            }, 404
        
        # Validate article exists
        article = Article.query.get(draft_data['article_id'])
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f"Article ID {draft_data['article_id']} not found",
                    'details': {}
                }
            }, 404
        
        # Validate batch exists
        batch = Batch.query.get(draft_data['batch_id'])
        if not batch:
            return {
                'error': {
                    'code': 'BATCH_NOT_FOUND',
                    'message': f"Batch ID {draft_data['batch_id']} not found",
                    'details': {}
                }
            }, 404
        
        # Check for duplicate client_event_id
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
        
        # Round quantity to 2 decimal places
        quantity = Decimal(str(draft_data['quantity_kg'])).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        draft_data['quantity_kg'] = quantity
        
        draft = WeighInDraft(**draft_data)
        db.session.add(draft)
        db.session.commit()
        
        return draft, 201


@blp.route('/<int:draft_id>')
class DraftDetail(MethodView):
    """Single draft resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, DraftSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Draft not found')
    @require_token
    def get(self, draft_id):
        """Get draft by ID."""
        draft = WeighInDraft.query.get(draft_id)
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
    @require_token
    def patch(self, update_data, draft_id):
        """Update a draft.
        
        Only drafts in DRAFT status can be updated.
        """
        draft = WeighInDraft.query.get(draft_id)
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
