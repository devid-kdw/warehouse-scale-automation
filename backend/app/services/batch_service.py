"""Batch service - shared batch logic."""
from datetime import date
from sqlalchemy.orm import Session
from ..extensions import db
from ..models import Batch

def get_or_create_system_batch(article_id: int) -> Batch:
    """Get or create the system 'NA' batch for a given article.
    
    This is used primarily for consumables which do not have manufacturer batches.
    
    Args:
        article_id: The ID of the article.
        
    Returns:
        The 'NA' Batch object.
    """
    batch_code = 'NA'
    expiry_date = date(2099, 12, 31)
    
    # Try to find existing NA batch
    batch = db.session.query(Batch).filter_by(
        article_id=article_id,
        batch_code=batch_code
    ).first()
    
    if not batch:
        # Create new NA batch
        batch = Batch(
            article_id=article_id,
            batch_code=batch_code,
            expiry_date=expiry_date,
            note='System Batch (Consumable)',
            is_active=True
        )
        db.session.add(batch)
        db.session.flush() # Get ID
        
    return batch
