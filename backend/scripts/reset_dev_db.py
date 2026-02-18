import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import (
    User, Location, Article, Batch, Stock, Surplus, Transaction, 
    WeighInDraft, DraftGroup, Order, OrderLine, ArticleAlias, 
    MissingArticleReport, ApprovalAction, UomCatalog
)

def reset_db():
    app = create_app()
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Target Database: {db_url}")
        
        # Safety check
        if 'prod' in db_url or 'aws' in db_url:
            print("ABORTING: Database URL looks like production!")
            return

        print("Truncating tables...")
        # Explicit list of tables to truncate
        # Using CASCADE to handle foreign keys
        tables = [
             'users', 
             'locations', 
             'articles', 
             'article_aliases', 
             'batches', 
             'stock', 
             'surplus', 
             'transactions', 
             'weigh_in_drafts', 
             'draft_groups', 
             'approval_actions',
             'orders', 
             'order_lines',
             'missing_article_reports', 
             'uom_catalog'
        ]
        
        try:
            # Validating tables exist before truncating to avoid errors if some are missing
            # Actually, TRUNCATE IF EXISTS is not standard SQL for all DBs, but PostgreSQL supports it?
            # Or just ignore errors.
            # Better: list tables in public schema and truncate them.
            
            # For now, explicit list with CASCADE.
            # Restart identity resets serial sequences.
            db.session.execute(text("TRUNCATE TABLE " + ", ".join(tables) + " RESTART IDENTITY CASCADE;"))
            db.session.commit()
            print("Tables truncated.")
        except Exception as e:
            print(f"Error truncating: {e}")
            db.session.rollback()
            return

        print("Seeding bootstrap data...")
        
        # Location 13
        # Validating if it needs to be inserted or if 13 is a specific requirement
        loc = Location(id=13, name='Glavno Skladiste', code='13')
        db.session.add(loc)
        
        # User Stefan
        user = User(username='stefan', role='ADMIN', is_active=True)
        user.set_password('ChangeMe123!')
        db.session.add(user)
        
        db.session.commit()
        print("Bootstrap data seeded.")
        
        # Verify
        u_count = User.query.count()
        l_count = Location.query.count()
        a_count = Article.query.count()
        
        print("-" * 20)
        print(f"Users: {u_count} (Expected: 1)")
        print(f"Locations: {l_count} (Expected: 1)")
        print(f"Articles: {a_count} (Expected: 0)")
        print("-" * 20)
        
        if u_count == 1 and l_count == 1 and a_count == 0:
            print("SUCCESS: Database reset to clean baseline.")
        else:
            print("WARNING: Verification failed.")

if __name__ == "__main__":
    reset_db()
