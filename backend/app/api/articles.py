"""Articles API endpoints."""
from flask.views import MethodView
from flask_smorest import Blueprint

from ..extensions import db
from ..auth import require_token
from ..models import Article
from ..schemas.articles import ArticleSchema, ArticleCreateSchema, ArticleListSchema
from ..schemas.common import ErrorResponseSchema

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
        """List all articles.
        
        Returns all active articles.
        """
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
