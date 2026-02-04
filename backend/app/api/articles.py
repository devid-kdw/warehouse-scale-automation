"""Articles API endpoints."""
from datetime import datetime, timezone
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..auth import require_roles
from ..models import Article, Batch, Stock, Surplus, Transaction, WeighInDraft, User
from ..error_handling import AppError
from ..schemas.articles import ArticleSchema, ArticleCreateSchema, ArticleListSchema
from ..schemas.aliases import ArticleAliasSchema, AliasCreateSchema, AliasListSchema
from ..schemas.common import ErrorResponseSchema, SuccessMessageSchema
from ..services import article_alias_service

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
    @jwt_required()
    def get(self):
        """List articles.
        
        Query params:
        - active=true (default): only active articles
        - active=false: only archived articles
        - active=all: all articles
        
        Returns last_consumed_at for each article (based on STOCK_CONSUMED/SURPLUS_CONSUMED).
        """
        active = request.args.get('active', 'true')
        
        # Subquery: get MAX(occurred_at) per article for consumption transactions only
        consumption_types = [Transaction.TX_STOCK_CONSUMED, Transaction.TX_SURPLUS_CONSUMED]
        last_consumed_subq = db.session.query(
            Transaction.article_id,
            db.func.max(Transaction.occurred_at).label('last_consumed_at')
        ).filter(
            Transaction.tx_type.in_(consumption_types)
        ).group_by(Transaction.article_id).subquery()
        
        # Build query with outer join
        query = db.session.query(
            Article,
            last_consumed_subq.c.last_consumed_at
        ).outerjoin(
            last_consumed_subq,
            Article.id == last_consumed_subq.c.article_id
        )
        
        # Apply active filter
        if active == 'all':
            pass  # No filter
        elif active == 'false':
            query = query.filter(Article.is_active == False)
        else:
            query = query.filter(Article.is_active == True)
        
        results = query.all()
        
        # Build response with last_consumed_at attached
        items = []
        for article, last_consumed_at in results:
            # Attach computed field to article object for schema serialization
            article.last_consumed_at = last_consumed_at
            items.append(article)
        
        return {
            'items': items,
            'total': len(items)
        }
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(ArticleCreateSchema)
    @blp.response(201, ArticleSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Article already exists')
    @jwt_required()
    @require_roles('ADMIN')
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
        
        return article, 201


@blp.route('/<string:article_no>')
class ArticleDetail(MethodView):
    """Single article resource."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, ArticleSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @jwt_required()
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
        return article


@blp.route('/<int:article_id>/archive')
class ArticleArchive(MethodView):
    """Archive an article."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, SuccessMessageSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @jwt_required()
    @require_roles('ADMIN')
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
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @jwt_required()
    @require_roles('ADMIN')
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
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Article in use')
    @jwt_required()
    @require_roles('ADMIN')
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


@blp.route('/resolve')
class ArticleResolve(MethodView):
    """Resolve article by article_no or alias."""
    
    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, ArticleSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Query parameter missing')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self):
        """Find article by query string (article_no or alias)."""
        query = request.args.get('query')
        if not query:
             return {
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Query parameter is required',
                }
            }, 400
            
        try:
            return article_alias_service.resolve_article(query)
        except AppError as e:
            return {
                'error': {
                    'code': e.error_code,
                    'message': e.message,
                    'details': e.details
                }
            }, e.status_code


@blp.route('/<int:article_id>/aliases')
class ArticleAliases(MethodView):
    """Article aliases collection."""

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, AliasListSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Article not found')
    @jwt_required()
    @require_roles('ADMIN')
    def get(self, article_id):
        """List aliases for an article."""
        try:
            aliases = article_alias_service.get_aliases(article_id)
            return {'items': aliases, 'total': len(aliases)}
        except AppError as e:
            return {
                'error': {
                    'code': e.error_code,
                    'message': e.message,
                    'details': e.details
                }
            }, e.status_code

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.arguments(AliasCreateSchema)
    @blp.response(201, ArticleAliasSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Validation error')
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Duplicate alias or limit reached')
    @jwt_required()
    @require_roles('ADMIN')
    def post(self, alias_data, article_id):
        """Create a new alias for an article."""
        try:
            return article_alias_service.create_alias(article_id, alias_data['alias'])
        except AppError as e:
            return {
                'error': {
                    'code': e.error_code,
                    'message': e.message,
                    'details': e.details
                }
            }, e.status_code


@blp.route('/<int:article_id>/aliases/<int:alias_id>')
class ArticleAliasDetail(MethodView):
    """Single alias resource."""

    @blp.doc(security=[{'bearerAuth': []}])
    @blp.response(200, SuccessMessageSchema)
    @blp.alt_response(401, schema=ErrorResponseSchema, description='Invalid token')
    @blp.alt_response(403, schema=ErrorResponseSchema, description='Admin role required')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Alias not found')
    @jwt_required()
    @require_roles('ADMIN')
    def delete(self, article_id, alias_id):
        """Delete an alias."""
        try:
            article_alias_service.delete_alias(alias_id)
            return {'message': 'Alias deleted successfully'}
        except AppError as e:
            return {
                'error': {
                    'code': e.error_code,
                    'message': e.message,
                    'details': e.details
                }
            }, e.status_code
