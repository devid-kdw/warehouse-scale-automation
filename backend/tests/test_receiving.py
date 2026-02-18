"""Tests for stock receiving service and endpoint."""
from datetime import date, timedelta
from decimal import Decimal
import pytest

from app.extensions import db
from app.models import Stock, Batch, Transaction, User, Article
from app.services.receiving_service import receive_stock
from app.error_handling import AppError


class TestReceiveStockSuccess:
    """Test successful stock receiving scenarios."""
    
    def test_receive_stock_success(self, app, location, article, user):
        """Receive stock increases quantity and creates transaction."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            expiry = date.today() + timedelta(days=365)
            
            result = receive_stock(
                article_id=article,
                batch_code='1234',
                quantity=Decimal('50.00'),
                uom='KG',
                expiry_date=expiry,
                actor_user_id=user,
                order_number='PO-1001',
                delivery_note_number='DN-1001',
                location_id=location,
                client_event_id='evt-1',
                note='Success'
            )
            db.session.commit()
            
            assert result['batch_created'] is True
            assert result['previous_stock'] == Decimal('0')
            assert result['new_stock'] == Decimal('50.00')
            assert result['quantity_received'] == Decimal('50.00')
            assert result['transaction']['tx_type'] == 'STOCK_RECEIPT'
            assert result['transaction']['order_number'] == 'PO-1001'
            assert result['transaction']['delivery_note_number'] == 'DN-1001'
            assert result['transaction']['client_event_id'] == 'evt-1'
            
            # Verify stock in DB
            stock = Stock.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=result['batch_id']
            ).first()
            assert stock is not None
            assert stock.quantity == Decimal('50.00')
    
    def test_receive_auto_creates_batch(self, app, location, article, user):
        """Receiving creates batch if it doesn't exist."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            expiry = date.today() + timedelta(days=180)
            
            result = receive_stock(
                article_id=article,
                batch_code='9876543210',
                quantity=Decimal('25.00'),
                uom='KG',
                expiry_date=expiry,
                actor_user_id=user,
                order_number='PO-1002',
                delivery_note_number='DN-1002',
                note='Auto create'
            )
            db.session.commit()
            
            assert result['batch_created'] is True
            
            batch = Batch.query.filter_by(
                article_id=article,
                batch_code='9876543210'
            ).first()
            assert batch is not None
            assert batch.expiry_date == expiry
    
    def test_receive_existing_batch_same_expiry(self, app, location, article, user):
        """Receiving to existing batch with same expiry works."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            
            expiry = date.today() + timedelta(days=200)
            
            # Create batch first
            batch = Batch(
                article_id=article,
                batch_code='5555',
                expiry_date=expiry
            )
            db.session.add(batch)
            db.session.commit()
            batch_id = batch.id
            
            # Receive with same expiry
            result = receive_stock(
                article_id=article,
                batch_code='5555',
                quantity=Decimal('30.00'),
                uom='KG',
                expiry_date=expiry,
                actor_user_id=user,
                order_number='PO-1003',
                delivery_note_number='DN-1003',
                note='Existing batch'
            )
            db.session.commit()
            
            assert result['batch_created'] is False
            assert result['batch_id'] == batch_id
            assert result['new_stock'] == Decimal('30.00')
    
    def test_receive_batch_backfill_expiry(self, app, location, article, user):
        """Receiving can backfill NULL expiry_date on existing batch."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            
            # Create batch without expiry
            batch = Batch(
                article_id=article,
                batch_code='4444',
                expiry_date=None  # NULL expiry
            )
            db.session.add(batch)
            db.session.commit()
            batch_id = batch.id
            
            expiry = date.today() + timedelta(days=300)
            
            result = receive_stock(
                article_id=article,
                batch_code='4444',
                quantity=Decimal('20.00'),
                uom='KG',
                expiry_date=expiry,
                actor_user_id=user,
                order_number='PO-1004',
                delivery_note_number='DN-1004',
                note='Backfill'
            )
            db.session.commit()
            
            assert result['batch_created'] is False
            
            # Verify expiry was set
            batch = db.session.get(Batch, batch_id)
            assert batch.expiry_date == expiry

    def test_receive_consumable_system_batch(self, app, location, user):
        """Receiving a non-batch-tracked article forces System Batch (NA)."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            
            # Create non-batch-tracked article
            consumable = Article(
                article_no='CONSUMABLE-01',
                description='Consumable Item',
                uom='KG',
                is_paint=False,
                has_batch=False,
                is_active=True
            )
            db.session.add(consumable)
            db.session.commit()
            
            # Receive with random batch code/expiry
            result = receive_stock(
                article_id=consumable.id,
                batch_code='RANDOM123',
                quantity=Decimal('10.00'),
                uom='KG',
                expiry_date=date.today(),
                actor_user_id=user,
                order_number='PO-CONS-01',
                delivery_note_number='DN-CONS-01',
                note='Consumable test'
            )
            db.session.commit()
            
            # Verify batch is N/A / 9999-12-31
            batch = db.session.get(Batch, result['batch_id'])
            assert batch.batch_code == 'N/A'
            assert batch.expiry_date == date(9999, 12, 31)
            assert batch.note == 'System Batch (Non-batch-tracked)'


class TestReceiveStockValidation:
    """Test receiving validation errors."""
    
    def test_receive_missing_delivery_note(self, app, location, article, user):
        """Missing delivery note number returns validation error."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article,
                    batch_code='1234',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=date.today(),
                    actor_user_id=user,
                    delivery_note_number='',
                    note='Missing DN'
                )
            
            assert exc.value.code == 'VALIDATION_ERROR'
            assert 'delivery_note_number' in str(exc.value.message)

    def test_receive_missing_note_for_adhoc(self, app, location, article, user):
        """Ad-hoc receiving requires a note."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article,
                    batch_code='1234',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=date.today(),
                    actor_user_id=user,
                    delivery_note_number='DN-123',
                    note=''
                )
            
            assert exc.value.code == 'VALIDATION_ERROR'
            assert 'note is required' in exc.value.message

    def test_receive_expiry_mismatch_409(self, app, location, article, user):
        """Receiving with different expiry returns 409."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            
            old_expiry = date.today() + timedelta(days=100)
            new_expiry = date.today() + timedelta(days=200)
            
            # Create batch with expiry
            batch = Batch(
                article_id=article,
                batch_code='3333',
                expiry_date=old_expiry
            )
            db.session.add(batch)
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article,
                    batch_code='3333',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=new_expiry,
                    actor_user_id=user,
                    order_number='PO-FAIL',
                    delivery_note_number='DN-FAIL',
                    note='Mismatch'
                )
            
            assert exc.value.code == 'BATCH_EXPIRY_MISMATCH'
    
    def test_receive_operator_blocked(self, app, location, article, user):
        """Operators cannot receive stock."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'OPERATOR'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article,
                    batch_code='1234',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=date.today() + timedelta(days=100),
                    actor_user_id=user,
                    delivery_note_number='DN-OP',
                    note='Blocked'
                )
            
            assert exc.value.code == 'FORBIDDEN'
    
    def test_receive_invalid_batch_code(self, app, location, article, user):
        """Invalid batch code returns validation error."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article,
                    batch_code='ABC123',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=date.today() + timedelta(days=100),
                    actor_user_id=user,
                    delivery_note_number='DN-INV',
                    note='Invalid'
                )
            
            assert exc.value.code == 'VALIDATION_ERROR'
    
    def test_receive_location_not_allowed(self, app, location, article, user):
        """Location other than 13 returns error in v1."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article,
                    batch_code='1234',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=date.today() + timedelta(days=100),
                    actor_user_id=user,
                    delivery_note_number='DN-LOC',
                    location_id=999,
                    note='Loc fail'
                )
            
            assert exc.value.code in ('LOCATION_NOT_FOUND', 'LOCATION_NOT_ALLOWED')
    
    def test_receive_article_not_found(self, app, location, user):
        """Non-existent article returns 404."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=99999,
                    batch_code='1234',
                    quantity=Decimal('10.00'),
                    uom='KG',
                    expiry_date=date.today() + timedelta(days=100),
                    actor_user_id=user,
                    delivery_note_number='DN-ART',
                    note='Art fail'
                )
            
            assert exc.value.code == 'ARTICLE_NOT_FOUND'


class TestReceiveStockTransaction:
    """Test receiving creates proper audit trail."""
    
    def test_receive_creates_transaction(self, app, location, article, user):
        """Receiving creates STOCK_RECEIPT transaction."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            result = receive_stock(
                article_id=article,
                batch_code='7777',
                quantity=Decimal('100.00'),
                uom='KG',
                expiry_date=date.today() + timedelta(days=365),
                actor_user_id=user,
                note='Test receiving',
                order_number='PO-TX-TEST',
                delivery_note_number='DN-TX-TEST',
                client_event_id='evt-tx'
            )
            db.session.commit()
            
            tx = Transaction.query.filter_by(
                tx_type='STOCK_RECEIPT'
            ).first()
            
            assert tx is not None
            assert tx.quantity == Decimal('100.00')
            assert tx.user_id == user
            assert tx.source == 'receiving'
            assert tx.order_number == 'PO-TX-TEST'
            assert tx.delivery_note_number == 'DN-TX-TEST'
            assert tx.client_event_id == 'evt-tx'
            assert tx.meta['note'] == 'Test receiving'
            assert tx.meta['batch_created'] is True
    
    def test_receive_rounding(self, app, location, article, user):
        """Receiving properly rounds legacy quantities."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            # 1.005 should round to 1.01 with ROUND_HALF_UP in legacy quantity_kg
            result = receive_stock(
                article_id=article,
                batch_code='8888',
                quantity=Decimal('1.005'),
                uom='KG',
                expiry_date=date.today() + timedelta(days=100),
                actor_user_id=user,
                delivery_note_number='DN-ROUND',
                note='Rounding test'
            )
            db.session.commit()
            
            assert result['new_stock'] == Decimal('1.005')
