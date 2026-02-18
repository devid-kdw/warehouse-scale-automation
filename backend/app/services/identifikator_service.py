"""Article Identifikator service - lookup and missing article reporting."""
from datetime import datetime, timezone
from typing import List, Dict, Optional
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Article, ArticleAlias, MissingArticleReport, User
from ..error_handling import AppError
from .article_alias_service import resolve_article as base_resolve


def identify_article(query: str) -> Optional[Article]:
    """Find article by Article No, Alias, or Partial Description (Normalized)."""
    if not query or not query.strip():
        raise AppError('VALIDATION_ERROR', 'Query is required')
        
    normalized = query.strip().upper()
    
    # 1. Try exact match on Article No or Alias (via base service)
    try:
        return base_resolve(query)
    except AppError:
        pass
        
    # 2. Try partial match on Description
    article = Article.query.filter(
        Article.is_active == True,
        func.upper(Article.description).contains(normalized)
    ).first()
    
    return article


def submit_missing_article_report(
    raw_input: str,
    location_id: int,
    actor_user_id: int
) -> MissingArticleReport:
    """Submit a report for a missing article with hard deduplication."""
    if not raw_input or not raw_input.strip():
        raise AppError('VALIDATION_ERROR', 'Description or code is required')
        
    normalized = raw_input.strip().lower()
    
    # Check for existing OPEN report for this normalized input + location (Service-level check)
    existing = MissingArticleReport.query.filter(
        MissingArticleReport.normalized_input == normalized,
        MissingArticleReport.location_id == location_id,
        MissingArticleReport.status == MissingArticleReport.STATUS_OPEN
    ).first()
    
    if existing:
        return existing  # Transparently return existing instead of error (dedup)

    report = MissingArticleReport(
        reported_by_user_id=actor_user_id,
        location_id=location_id,
        raw_input=raw_input.strip(),
        normalized_input=normalized,
        status=MissingArticleReport.STATUS_OPEN
    )
    
    db.session.add(report)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        # Race condition: someone else inserted it between our check and flush
        existing_after_race = MissingArticleReport.query.filter(
            MissingArticleReport.normalized_input == normalized,
            MissingArticleReport.location_id == location_id,
            MissingArticleReport.status == MissingArticleReport.STATUS_OPEN
        ).first()
        if existing_after_race is None:
            raise AppError(
                'INTERNAL_ERROR',
                'Duplicate report conflict could not be resolved. Please retry.'
            )
        return existing_after_race
        
    return report


def get_report_queue(status: Optional[str] = None) -> List[MissingArticleReport]:
    """Get the admin reporting queue."""
    query = MissingArticleReport.query
    if status:
        query = query.filter_by(status=status)
    return query.order_by(MissingArticleReport.created_at.desc()).all()


def update_report_status(
    report_id: int,
    status: str,
    actor_user_id: int,
    admin_note: Optional[str] = None,
    resolved_article_id: Optional[int] = None
) -> MissingArticleReport:
    """Update report status and resolution (Admin only)."""
    report = db.session.get(MissingArticleReport, report_id)
    if not report:
        raise AppError('NOT_FOUND', f'Report {report_id} not found')
        
    report.status = status
    if admin_note:
        report.admin_note = admin_note
        
    if status == MissingArticleReport.STATUS_RESOLVED:
        if not resolved_article_id:
            raise AppError('VALIDATION_ERROR', 'resolved_article_id required for RESOLVED status')
        report.resolved_article_id = resolved_article_id
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by_user_id = actor_user_id
        
    if status == MissingArticleReport.STATUS_CLOSED:
        # Explicit close
        pass
        
    db.session.flush()
    return report
