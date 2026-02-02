"""Articles API endpoints."""
from datetime import datetime, timezone
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

from ..extensions import db
from ..auth import require_token
from ..models import Article, Batch, Stock, Surplus, Transaction, WeighInDraft, User
from ..schemas.articles import ArticleSchema, ArticleCreateSchema, ArticleListSchema
from ..schemas.common import ErrorResponseSchema, SuccessMessageSchema

blp = Blueprint(
    'articles',
    __name__,
    url_prefix='/api/articles',
    description='Articles management'
)


@blp.route('')
class ArticleList(MethodView):
    """Article collection resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, ArticleListSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @require_token
    def get(self):
        """List articles.
        
        Query params:
        - active=true (default): only active articles
        - active=false: only archived articles
        - active=all: all articles
        """
        active = request.args.get('active', 'true')
        
        if active == 'all':
            articles = Article.query.all()
        elif active == 'false':
            articles = Article.query.filter_by(is_active=False).all()
        else:
            articles = Article.query.filter_by(is_active=True).all()
        
        return {
            'items': [a.to_dict() for a in articles],
            'total': len(articles)
        }
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ArticleCreateSchema)
    @blp.response(201, ArticleSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Article already exists')
    @require_token
    def post(self, article_data):
        """Create a new article.
        
        Creates an article with the provided data.
        """
        # Check if article_no already exists
        existing = Article.query.filter_by(article_no=article_data['article_no']).first()
        if existing:
            return {
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f"Article {article_data['article_no']} already exists",
                    'details': {'article_no': article_data['article_no']}
                }
            }, 409
        
        article = Article(**article_data)
        db.session.add(article)
        db.session.commit()
        
        return article.to_dict(), 201


@blp.route('/<string:article_no>')
class ArticleDetail(MethodView):
    """Single article resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, ArticleSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @require_token
    def get(self, article_no):
        """Get article by article_no."""
        article = Article.query.filter_by(article_no=article_no).first()
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f'Article {article_no} not found',
                    'details': {}
                }
            }, 404
        return article.to_dict()


@blp.route('/<int:article_id>/archive')
class ArticleArchive(MethodView):
    """Archive an article."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, SuccessMessageSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @require_token
    def post(self, article_id):
        """Archive an article (soft delete).
        
        Sets is_active=false. Article remains in database for audit purposes.
        """
        article = Article.query.get(article_id)
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f'Article ID {article_id} not found',
                    'details': {}
                }
            }, 404
        
        article.is_active = False
        article.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return {
            'message': f'Article {article.article_no} archived successfully',
            'data': article.to_dict()
        }


@blp.route('/<int:article_id>/restore')
class ArticleRestore(MethodView):
    """Restore an archived article."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, SuccessMessageSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @require_token
    def post(self, article_id):
        """Restore an archived article.
        
        Sets is_active=true.
        """
        article = Article.query.get(article_id)
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f'Article ID {article_id} not found',
                    'details': {}
                }
            }, 404
        
        article.is_active = True
        article.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return {
            'message': f'Article {article.article_no} restored successfully',
            'data': article.to_dict()
        }


@blp.route('/<int:article_id>')
class ArticleDelete(MethodView):
    """Delete article resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, SuccessMessageSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Article in use')
    @require_token
    def delete(self, article_id):
        """Hard delete an article.
        
        Only allowed if article has no references:
        - 0 batches
        - 0 stock rows
        - 0 surplus rows
        - 0 transactions
        - 0 weigh-in drafts
        """
        article = Article.query.get(article_id)
        if not article:
            return {
                'error': {
                    'code': 'ARTICLE_NOT_FOUND',
                    'message': f'Article ID {article_id} not found',
                    'details': {}
                }
            }, 404
        
        # Check for references
        references = {}
        
        batch_count = Batch.query.filter_by(article_id=article_id).count()
        if batch_count > 0:
            references['batches'] = batch_count
        
        stock_count = Stock.query.filter_by(article_id=article_id).count()
        if stock_count > 0:
            references['stock_rows'] = stock_count
        
        surplus_count = Surplus.query.filter_by(article_id=article_id).count()
        if surplus_count > 0:
            references['surplus_rows'] = surplus_count
        
        transaction_count = Transaction.query.filter_by(article_id=article_id).count()
        if transaction_count > 0:
            references['transactions'] = transaction_count
        
        draft_count = WeighInDraft.query.filter_by(article_id=article_id).count()
        if draft_count > 0:
            references['drafts'] = draft_count
        
        if references:
            return {
                'error': {
                    'code': 'ARTICLE_IN_USE',
                    'message': f'Cannot delete article {article.article_no}: has references',
                    'details': {'references': references}
                }
            }, 409
        
        article_no = article.article_no
        db.session.delete(article)
        db.session.commit()
        
        return {
            'message': f'Article {article_no} deleted permanently'
        }
