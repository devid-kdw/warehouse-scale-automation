"""Article alias service - CRUD with uniqueness and limit rules."""
from typing import Optional

from ..extensions import db
from ..models import Article, ArticleAlias
from ..error_handling import AppError


# Maximum aliases per article
MAX_ALIASES_PER_ARTICLE = 5


def create_alias(article_id: int, alias: str) -> ArticleAlias:
    """Create an alias for an article.
    
    Args:
        article_id: Article ID
        alias: Alias string
        
    Returns:
        Created ArticleAlias
        
    Raises:
        AppError: If article not found, alias limit reached, or alias already exists
    """
    # Check article exists
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')
    
    # Check alias limit
    current_count = ArticleAlias.query.filter_by(article_id=article_id).count()
    if current_count >= MAX_ALIASES_PER_ARTICLE:
        raise AppError(
            'ALIAS_LIMIT_REACHED',
            f'Maximum {MAX_ALIASES_PER_ARTICLE} aliases per article',
            {'current_count': current_count, 'max_allowed': MAX_ALIASES_PER_ARTICLE}
        )
    
    # Check global uniqueness
    existing = ArticleAlias.query.filter_by(alias=alias).first()
    if existing:
        raise AppError(
            'DUPLICATE_ALIAS',
            f'Alias "{alias}" already exists',
            {'existing_article_id': existing.article_id}
        )
    
    # Create alias
    new_alias = ArticleAlias(article_id=article_id, alias=alias)
    db.session.add(new_alias)
    db.session.flush()
    
    return new_alias


def get_aliases(article_id: int) -> list:
    """Get all aliases for an article.
    
    Args:
        article_id: Article ID
        
    Returns:
        List of ArticleAlias objects
        
    Raises:
        AppError: If article not found
    """
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')
    
    return ArticleAlias.query.filter_by(article_id=article_id).order_by(ArticleAlias.created_at).all()


def delete_alias(alias_id: int) -> bool:
    """Delete an alias by ID.
    
    Args:
        alias_id: Alias ID
        
    Returns:
        True if deleted
        
    Raises:
        AppError: If alias not found
    """
    alias = db.session.get(ArticleAlias, alias_id)
    if not alias:
        raise AppError('ALIAS_NOT_FOUND', f'Alias {alias_id} not found')
    
    db.session.delete(alias)
    db.session.flush()
    
    return True


def resolve_article(query: str) -> Optional[Article]:
    """Find article by article_no or alias.
    
    Args:
        query: Search string (article_no or alias)
        
    Returns:
        Article object if found
        
    Raises:
        AppError: If not found
    """
    if not query:
        raise AppError('VALIDATION_ERROR', 'Query is required')
    
    # Try to find by article_no first
    article = Article.query.filter_by(article_no=query).first()
    if article:
        return article
    
    # Try to find by alias
    alias = ArticleAlias.query.filter_by(alias=query).first()
    if alias:
        return alias.article
    
    raise AppError('ARTICLE_NOT_FOUND', f'No article found for query: {query}')
