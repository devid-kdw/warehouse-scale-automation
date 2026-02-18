"""Batches API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..auth import require_roles
from ..models import Batch, Article

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
    @jwt_required()
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
    
    @blp.doc(security=[{'bearerAuth': []}],
             description='**DEPRECATED** — Use receiving workflow instead. '
                         'Standalone batch creation will be removed in Phase 4.')
    @blp.arguments(BatchCreateSchema)
    @blp.response(201, BatchSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Batch already exists')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, batch_data):
        """Create a new batch (DEPRECATED).

        **Deprecated**: Use the receiving workflow (`POST /api/inventory/receive`)
        instead. This endpoint will be removed in Phase 4.

        Requires ADMIN role.
        Batch code must be 4-5 digits (Mankiewicz) or 9-12 digits (Akzo).
        """
        # Validate batch code format is handled by Schema
        batch_code = batch_data['batch_code']
        
        # Check article exists
        article = db.session.get(Article, batch_data['article_id'])
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

        from flask import make_response
        resp = make_response(BatchSchema().dump(batch), 201)
        resp.headers['Deprecation'] = 'true'
        resp.headers['Sunset'] = 'Mon, 01 Jun 2026 00:00:00 GMT'
        return resp
