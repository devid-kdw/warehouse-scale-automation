"""Verification script for Phase 4 features."""
import pytest
from app.extensions import db
from app.models import Article, ArticleAlias, MissingArticleReport, Transaction, User, Location, Batch, Stock, Surplus
from app.services import identifikator_service, inventory_service, report_service
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def auth_context(app):
    """Wait for app context and db setup."""
    with app.app_context():
        # Ensure test data exists
        admin = User.query.filter_by(role='ADMIN').first()
        if not admin:
            admin = User(username='admin_v4', password_hash='hash', role='ADMIN')
            db.session.add(admin)
        
        loc = Location.query.filter_by(id=13).first()
        if not loc:
            loc = Location(id=13, code='W13', name='Warehouse 13')
            db.session.add(loc)
            
        db.session.commit()
        yield {'admin_id': admin.id, 'location_id': loc.id}

def test_missing_article_report_dedup(app, auth_context):
    """Test that hard deduplication works at both service and DB level."""
    with app.app_context():
        raw = "MISSING-12345"
        uid = auth_context['admin_id']
        lid = auth_context['location_id']
        
        # 1. First submission
        r1 = identifikator_service.submit_missing_article_report(raw, lid, uid)
        db.session.commit()
        assert r1.status == 'OPEN'
        
        # 2. Second submission (should return same object without error - service level)
        r2 = identifikator_service.submit_missing_article_report(raw.lower(), lid, uid)
        assert r1.id == r2.id
        
        # 3. DB level constraint check (bypass service)
        r_manual = MissingArticleReport(
            reported_by_user_id=uid,
            location_id=lid,
            raw_input="another",
            normalized_input=raw.lower(), # Same as r1
            status='OPEN'
        )
        db.session.add(r_manual)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        
        # 4. Resolve r1 and try reporting same input again (should allow new report)
        identifikator_service.update_report_status(r1.id, 'CLOSED', uid)
        db.session.commit()
        
        r3 = identifikator_service.submit_missing_article_report(raw, lid, uid)
        db.session.commit()
        assert r3.id != r1.id
        assert r3.status == 'OPEN'

def test_identify_article_variants(app, auth_context):
    """Test lookup by No, Alias, and partial Description."""
    with app.app_context():
        art = Article(article_no='PH4-ART', description='Premium Glossy Paint', uom='kg', is_active=True)
        db.session.add(art)
        db.session.flush()
        alias = ArticleAlias(article_id=art.id, alias='GLOSSY-01')
        db.session.add(alias)
        db.session.commit()
        
        # Exact No
        assert identifikator_service.identify_article('PH4-ART').id == art.id
        # Alias
        assert identifikator_service.identify_article('GLOSSY-01').id == art.id
        # Partial Description
        assert identifikator_service.identify_article('glossy').id == art.id
        assert identifikator_service.identify_article('PREMIUM').id == art.id

def test_inventory_consolidation(app, auth_context):
    """Test aggregated inventory sums."""
    with app.app_context():
        art = Article(article_no='CONS-01', description='Consolidated', uom='kg', is_active=True)
        db.session.add(art)
        db.session.flush()
        
        b1 = Batch(article_id=art.id, batch_code='1001')
        b2 = Batch(article_id=art.id, batch_code='1002')
        db.session.add_all([b1, b2])
        db.session.flush()
        
        # Stock for b1, Surplus for b2
        s1 = Stock(location_id=13, article_id=art.id, batch_id=b1.id, quantity=Decimal('10.50'), uom='kg')
        sur2 = Surplus(location_id=13, article_id=art.id, batch_id=b2.id, quantity=Decimal('5.25'), uom='kg')
        db.session.add_all([s1, sur2])
        db.session.commit()
        
        items = inventory_service.get_consolidated_inventory(13, article_no='CONS-01')
        # Service returns Article+Batch granularity (2 rows: b1 with stock, b2 with surplus)
        assert len(items) == 2
        
        # Sort for deterministic assertion
        items.sort(key=lambda x: x['batch_code'])
        
        # b1 = stock 10.50, no surplus
        assert items[0]['batch_code'] == '1001'
        assert items[0]['stock'] == 10.50
        assert items[0]['surplus'] == 0.0
        assert items[0]['total'] == 10.50
        
        # b2 = no stock, surplus 5.25
        assert items[1]['batch_code'] == '1002'
        assert items[1]['stock'] == 0.0
        assert items[1]['surplus'] == 5.25
        assert items[1]['total'] == 5.25

def test_article_inspection_dates(app, auth_context):
    """Test activity timestamps in inspection."""
    with app.app_context():
        art = Article(article_no='DATE-01', description='Date Test', uom='kg')
        db.session.add(art)
        db.session.flush()
        batch = Batch(article_id=art.id, batch_code='D1')
        db.session.add(batch)
        db.session.flush()
        
        # 1. Receipt
        t1 = Transaction(
            tx_type=Transaction.TX_STOCK_RECEIPT,
            location_id=13, article_id=art.id, batch_id=batch.id,
            quantity=10, uom='kg', user_id=auth_context['admin_id'],
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=10)
        )
        # 2. Consumption
        t2 = Transaction(
            tx_type=Transaction.TX_STOCK_CONSUMED,
            location_id=13, article_id=art.id, batch_id=batch.id,
            quantity=-2, uom='kg', user_id=auth_context['admin_id'],
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        db.session.add_all([t1, t2])
        db.session.commit()
        
        details = inventory_service.get_article_details(art.id, 13)
        activity = details['activity']
        assert activity['last_received_at'] is not None
        assert activity['last_issued_at'] is not None
        assert activity['last_activity_at'] == activity['last_issued_at']

def test_export_file_generation(app, auth_context):
    """Test that export functions return valid data types."""
    with app.app_context():
        # Excel
        excel_stream = report_service.export_inventurna_to_excel(13)
        assert excel_stream.getbuffer().nbytes > 100
        
        # PDF
        pdf_bytes = report_service.export_inventurna_to_pdf(13)
        assert len(pdf_bytes) > 100
        assert pdf_bytes.startswith(b'%PDF')
