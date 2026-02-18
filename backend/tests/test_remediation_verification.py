
import pytest
from decimal import Decimal
from app.extensions import db
from app.models import Article, Stock, Transaction, DraftGroup, User, Location, Surplus, Batch
from app.services import inventory_service, report_service, draft_group_service

@pytest.fixture
def clean_db(app):
    with app.app_context():
        db.create_all()
        # Create mandatory Location 13
        loc = Location(id=13, name='Main Warehouse', code='WH1')
        db.session.add(loc)
        db.session.commit()
        
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_user(clean_db):
    user = User(username='admin', role='ADMIN') # Removed email
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user

def test_inventory_adjustment_unit_logic(app, admin_user):
    with app.app_context():
        # 1. Create Article with Density (UOM=L, Density=0.8)
        art = Article(
            article_no='LIT-001', 
            description='Test Liter Item',
            uom='L',
            category='paint',
            density=0.8
        )
        db.session.add(art)
        db.session.commit()
        
        # Create Batch
        batch = Batch(article_id=art.id, batch_code='B1')
        db.session.add(batch)
        db.session.commit()
        
        # 2. Adjust Stock +10 L
        res = inventory_service.adjust_inventory(
            location_id=13,
            article_id=art.id,
            batch_id=batch.id,
            target='stock',
            mode='delta',
            quantity=10.0,
            uom='L',
            actor_user_id=admin_user.id,
            note='Test adjustment'
        )
        db.session.commit()
        
        # 3. Verify Stock Unit Quantity
        stock = db.session.query(Stock).filter_by(article_id=art.id).first()
        # Should be exactly 10.000
        assert stock.quantity == Decimal('10.000')
        assert stock.uom == 'L'
        
        # 4. Verify Transaction
        tx = db.session.query(Transaction).filter_by(
            article_id=art.id,
            batch_id=batch.id,
            tx_type='INVENTORY_ADJUSTMENT'
        ).first()
        
        assert tx is not None
        assert tx.quantity == Decimal('10.000') # Unit quantity stored
        assert tx.uom == 'L'

def test_reorder_risk_filtering(app, clean_db):
    with app.app_context():
        # Setup Articles
        # Red: Stock 50, Threshold 100
        art_red = Article(article_no='RED-001', description='Red Risk', uom='KG', reorder_threshold=100.0)
        db.session.add(art_red)
        db.session.flush()
        b_red = Batch(article_id=art_red.id, batch_code='B1')
        db.session.add(b_red)
        db.session.flush()
        stock_red = Stock(location_id=13, article_id=art_red.id, batch_id=b_red.id, quantity=50.0, uom='KG')
        db.session.add(stock_red)
        
        # Yellow: Stock 105, Threshold 100 (<= 110)
        art_yel = Article(article_no='YEL-001', description='Yellow Risk', uom='KG', reorder_threshold=100.0)
        db.session.add(art_yel)
        db.session.flush()
        b_yel = Batch(article_id=art_yel.id, batch_code='B1')
        db.session.add(b_yel)
        db.session.flush()
        stock_yel = Stock(location_id=13, article_id=art_yel.id, batch_id=b_yel.id, quantity=105.0, uom='KG')
        db.session.add(stock_yel)
        
        # Green: Stock 200, Threshold 100
        art_grn = Article(article_no='GRN-001', description='Green Risk', uom='KG', reorder_threshold=100.0)
        db.session.add(art_grn)
        db.session.flush()
        b_grn = Batch(article_id=art_grn.id, batch_code='B1')
        db.session.add(b_grn)
        db.session.flush()
        stock_grn = Stock(location_id=13, article_id=art_grn.id, batch_id=b_grn.id, quantity=200.0, uom='KG')
        db.session.add(stock_grn)
        
        db.session.commit()
        
        # Test Default (include_green=False)
        items = report_service.get_reorder_risk_lista(13, include_green=False)
        nos = [i['article_no'] for i in items]
        assert 'RED-001' in nos
        assert 'YEL-001' in nos
        assert 'GRN-001' not in nos
        
        # Test Include Green
        items_all = report_service.get_reorder_risk_lista(13, include_green=True)
        nos_all = [i['article_no'] for i in items_all]
        assert 'GRN-001' in nos_all

def test_draft_group_description(app, admin_user):
    with app.app_context():
        # Setup Article
        art = Article(article_no='DRAFT-001', uom='KG', has_batch=False)
        db.session.add(art)
        db.session.commit()
        
        # No batch needed for input lines if not provided (service handles getting system batch)
        # But we need to ensure batch_service works. 
        # Actually create_group uses batch_service.get_or_create_system_batch
        
        lines = [{
            'article_id': art.id,
            'quantity': 10.0, # Unit quantity
            'uom': 'KG', # UOM required now
            'client_event_id': 'evt-1'
        }]
        
        # Create Group with Description
        desc = "Test Description 123"
        group = draft_group_service.create_group(
            location_id=13,
            user_id=admin_user.id,
            lines=lines,
            description=desc
        )
        
        assert group.description == desc
        
        # Verify DB persistence
        db_group = db.session.get(DraftGroup, group.id)
        assert db_group.description == desc

def test_consolidated_inventory_unit_logic(app, clean_db):
    with app.app_context():
         # Article with UOM=L, Density=0.8
        art = Article(article_no='CON-001', uom='L', density=0.8)
        db.session.add(art)
        db.session.flush()
        
        b = Batch(article_id=art.id, batch_code='B1')
        db.session.add(b)
        db.session.flush()
        
        # Stock: 10 L
        stock = Stock(location_id=13, article_id=art.id, batch_id=b.id, quantity=10.0, uom='L')
        db.session.add(stock)
        
        # Surplus: 5 L
        surplus = Surplus(location_id=13, article_id=art.id, batch_id=b.id, quantity=5.0, uom='L')
        db.session.add(surplus)
        
        db.session.commit()
        
        items = inventory_service.get_consolidated_inventory(13, article_no='CON-001')
        item = items[0]
        
        # Tolerance for float comparison
        assert abs(item['stock'] - 10.0) < 0.001
        assert abs(item['surplus'] - 5.0) < 0.001
        assert abs(item['total'] - 15.0) < 0.001


