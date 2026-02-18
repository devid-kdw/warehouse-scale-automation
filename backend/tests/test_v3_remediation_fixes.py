
import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from app.extensions import db
from app.models import Article, Batch, Stock, Transaction, WeighInDraft, DraftGroup, User, Location
from app.services.receiving_service import receive_stock
from app.services.approval_service import approve_draft, update_aggregate_quantity, get_daily_approvals_detail
from app.services.report_service import get_top_20_monthly_consumers
from app.error_handling import AppError

@pytest.fixture
def setup_location(app):
    with app.app_context():
        # Create Location
        loc = Location.query.get(13)
        if not loc:
            loc = Location(id=13, name='Test Location', code='LOC13')
            db.session.add(loc)
        
        # Create User
        user = User.query.get(1)
        if not user:
            user = User(id=1, username='testuser', role='ADMIN')
            user.set_password('password')
            db.session.add(user)
            
        db.session.commit()
    return 13

def test_receive_stock_uom_mismatch(app, setup_location):
    """Test that receiving with mismatching UOM raises AppError."""
    with app.app_context():
        # Setup
        article = Article(article_no='TEST-UOM', description='Test', uom='L', density=1.0)
        db.session.add(article)
        db.session.commit()

        # Test
        with pytest.raises(AppError) as excinfo:
            receive_stock(
                location_id=13,
                article_id=article.id,
                batch_code='1234',
                expiry_date=date.today(),
                actor_user_id=1,
                delivery_note_number='DN1',
                quantity=Decimal('10'),
                uom='KG' # Mismatch
            )
        assert 'Received' in str(excinfo.value)
        assert 'KG' in str(excinfo.value)

def test_approval_unit_consumption(app, setup_location):
    """Test that approval correctly consumes units (replacing legacy mass check)."""
    with app.app_context():
        # Setup Article
        article = Article(article_no='TEST-UNIT', description='Unit Test', uom='PCS', density=0)
        db.session.add(article)
        db.session.flush()
        
        batch = Batch(article_id=article.id, batch_code='B1', is_active=True)
        db.session.add(batch)
        db.session.flush()
        
        # Create Draft with only quantity (unit-aware)
        draft = WeighInDraft(
            draft_group_id=None,
            location_id=13,
            article_id=article.id,
            batch_id=batch.id,
            quantity=Decimal('10.000'), # 10 PCS
            uom='PCS',
            draft_type='WEIGH_IN',
            status='DRAFT',
            client_event_id='evt_123',
            source='manual'
        )
        db.session.add(draft)
        # Seed positive stock to allow consumption
        stock = Stock(location_id=13, article_id=article.id, batch_id=batch.id, quantity=100, uom='PCS')
        db.session.add(stock)
        db.session.commit()

        res = approve_draft(draft.id, actor_user_id=1)
        
        # Check transaction
        txs = res['transactions']
        weigh_in_tx = next(t for t in txs if t['tx_type'] == 'WEIGH_IN')
        
        # Should be -10.0
        assert float(weigh_in_tx['quantity']) == -10.0
        assert weigh_in_tx['uom'] == 'PCS'
        # quantity_kg should NOT be present or None if legacy output kept
        # Actually our refactor removed it from dict output probably?
        # Transaction.to_dict might still check for property? No, removed from model.
        assert 'quantity_kg' not in weigh_in_tx or weigh_in_tx.get('quantity_kg') is None

def test_top_20_consumers_sorting(app, setup_location):
    """Test that top consumers are sorted by magnitude of consumption (most negative first)."""
    with app.app_context():
        # Setup
        # Create unique article numbers to avoid conflict
        suffix = datetime.now().strftime('%f')
        a1 = Article(article_no=f'A1-{suffix}', description='High Consumption', uom='L')
        a2 = Article(article_no=f'A2-{suffix}', description='Low Consumption', uom='L')
        db.session.add_all([a1, a2])
        db.session.flush()
        
        batch = Batch(article_id=a1.id, batch_code='B1')
        db.session.add(batch)
        db.session.flush()
        
        # Transactions (negative quantity for consumption)
        # A1: -100
        t1 = Transaction(
            tx_type='STOCK_CONSUMED', article_id=a1.id, location_id=13, batch_id=batch.id,
            quantity=-100, uom='L', occurred_at=datetime.now(timezone.utc)
        )
        # A2: -10
        t2 = Transaction(
            tx_type='STOCK_CONSUMED', article_id=a2.id, location_id=13, batch_id=batch.id,
            quantity=-10, uom='L', occurred_at=datetime.now(timezone.utc)
        )
        db.session.add_all([t1, t2])
        db.session.commit()
        
        results = get_top_20_monthly_consumers()
        
        # Find our articles
        r1 = next((r for r in results if r['article_no'] == a1.article_no), None)
        r2 = next((r for r in results if r['article_no'] == a2.article_no), None)
        
        assert r1 and r2
        # Check order in list? get_top_20 returns list.
        # Index of r1 should be < Index of r2 because -100 is "smaller" (algebraically) than -10
        # The sort is ASC. So -100 comes first.
        idx1 = results.index(r1)
        idx2 = results.index(r2)
        assert idx1 < idx2, f"Expected A1 (-100) at {idx1} to be before A2 (-10) at {idx2}"
