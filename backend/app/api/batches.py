"""Batches API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint

from ..extensions import db
from ..auth import require_token
from ..models import Batch, Article
from ..services.validation import validate_batch_code
from ..schemas.batches import BatchSchema, BatchCreateSchema, BatchListSchema
from ..schemas.common import ErrorResponseSchema

blp = Blueprint(
    'batches',
    __name__,
    url_prefix='/api',
    description='Batches management'
)


@blp.route('/articles/<string:article_no>/batches')
class ArticleBatchList(MethodView):
    """Batches for a specific article."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, BatchListSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @require_token
    def get(self, article_no):
        """List batches for an article.
        
        Returns all active batches for the given article.
        """
        article = Article.query.filter_by(article_no=article_no).first()
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f'Article {article_no} not found',
                    'details': {}
                }
            }, 404
        
        batches = Batch.query.filter_by(
            article_id=article.id,
            is_active=True
        ).all()
        
        return {
            'items': batches,
            'total': len(batches)
        }


@blp.route('/batches')
class BatchList(MethodView):
    """Batch collection resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(BatchCreateSchema)
    @blp.response(201, BatchSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Batch already exists')
    @require_token
    def post(self, batch_data):
        """Create a new batch.
        
        Creates a batch for the specified article.
        Batch code must be 4 digits (Mankiewicz) or 9-10 digits (Akzo).
        """
        # Validate batch code format using service
        batch_code = batch_data['batch_code']
        if not validate_batch_code(batch_code):
            return {
                'error': {
                    'code': 'INVALID_BATCH_FORMAT',
                    'message': f'Invalid batch code format: {batch_code}. Must be 4 digits (Mankiewicz) or 9-10 digits (Akzo)',
                    'details': {'batch_code': batch_code}
                }
            }, 400
        
        # Check article exists
        article = Article.query.get(batch_data['article_id'])
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f"Article ID {batch_data['article_id']} not found",
                    'details': {}
                }
            }, 404
        
        # Check if batch already exists for this article
        existing = Batch.query.filter_by(
            article_id=batch_data['article_id'],
            batch_code=batch_code
        ).first()
        if existing:
            return {
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f'Batch {batch_code} already exists for this article',
                    'details': {'batch_code': batch_code}
                }
            }, 409
        
        batch = Batch(**batch_data)
        db.session.add(batch)
        db.session.commit()
        
        return batch, 201
