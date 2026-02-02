"""Tests for approval service."""
import pytest
from decimal import Decimal

from app.extensions import db
from app.models import WeighInDraft, Stock, Surplus, Transaction
from app.services.approval_service import approve_draft, reject_draft
from app.error_handling import AppError, InsufficientStockError


class TestApproveWithSurplusOnly:
    """Test approval consuming only from surplus."""
    
    def test_surplus_only_consumption(self, app, location, article, batch, user, surplus, stock, draft):
        """When surplus >= draft quantity, only surplus is consumed."""
        with app.app_context():
            # Draft is 3kg, surplus is 5kg, stock is 10kg
            # Should use 3kg from surplus, 0kg from stock
            result = approve_draft(draft, user)
            db.session.commit()
            
            assert result['consumed_surplus_kg'] == 3.0
            assert result['consumed_stock_kg'] == 0.0
            assert result['remaining_surplus_kg'] == 2.0
            assert result['remaining_stock_kg'] == 10.0
            assert result['new_status'] == 'APPROVED'
            
            # Verify database state
            surplus_obj = Surplus.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(surplus_obj.quantity_kg) == 2.0
            
            stock_obj = Stock.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(stock_obj.quantity_kg) == 10.0
            
            # Verify transactions
            txs = Transaction.query.filter_by(client_event_id='test-event-001').all()
            tx_types = {tx.tx_type for tx in txs}
            assert 'WEIGH_IN' in tx_types
            assert 'SURPLUS_CONSUMED' in tx_types
            assert 'STOCK_CONSUMED' not in tx_types


class TestApproveWithSurplusAndStock:
    """Test approval consuming from both surplus and stock."""
    
    def test_surplus_plus_stock_consumption(self, app, location, article, batch, user, surplus, stock):
        """When surplus < draft quantity, use surplus first then stock."""
        with app.app_context():
            # Create draft for 8kg (surplus: 5kg, stock: 10kg)
            d = WeighInDraft(
                location_id=location,
                article_id=article,
                batch_id=batch,
                quantity_kg=Decimal('8.00'),
                client_event_id='test-event-002',
                created_by_user_id=user,
                source='manual'
            )
            db.session.add(d)
            db.session.commit()
            
            result = approve_draft(d.id, user)
            db.session.commit()
            
            # Should use 5kg from surplus (all of it), 3kg from stock
            assert result['consumed_surplus_kg'] == 5.0
            assert result['consumed_stock_kg'] == 3.0
            assert result['remaining_surplus_kg'] == 0.0
            assert result['remaining_stock_kg'] == 7.0
            
            # Verify transactions
            txs = Transaction.query.filter_by(client_event_id='test-event-002').all()
            tx_types = {tx.tx_type for tx in txs}
            assert 'WEIGH_IN' in tx_types
            assert 'SURPLUS_CONSUMED' in tx_types
            assert 'STOCK_CONSUMED' in tx_types


class TestApproveInsufficientStock:
    """Test approval failure when stock is insufficient."""
    
    def test_insufficient_stock_raises_error(self, app, location, article, batch, user, surplus, stock):
        """When combined surplus + stock < draft, raise InsufficientStockError."""
        with app.app_context():
            # Create draft for 20kg (surplus: 5kg, stock: 10kg = 15kg available)
            d = WeighInDraft(
                location_id=location,
                article_id=article,
                batch_id=batch,
                quantity_kg=Decimal('20.00'),
                client_event_id='test-event-003',
                created_by_user_id=user,
                source='manual'
            )
            db.session.add(d)
            db.session.commit()
            
            with pytest.raises(InsufficientStockError) as exc_info:
                approve_draft(d.id, user)
            
            error = exc_info.value
            assert error.code == 'INSUFFICIENT_STOCK'
            assert error.details['required_kg'] == 20.0
            assert error.details['available_stock_kg'] == 10.0
            assert error.details['available_surplus_kg'] == 5.0
            assert error.details['shortage_kg'] == 5.0
            
            # Verify draft status unchanged
            db.session.rollback()
            draft_obj = db.session.get(WeighInDraft, d.id)
            assert draft_obj.status == 'DRAFT'
            
            # Verify no inventory changes
            surplus_obj = Surplus.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(surplus_obj.quantity_kg) == 5.0
            
            stock_obj = Stock.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(stock_obj.quantity_kg) == 10.0


class TestApproveEdgeCases:
    """Test edge cases in approval."""
    
    def test_draft_not_found(self, app, user):
        """Non-existent draft raises error."""
        with app.app_context():
            with pytest.raises(AppError) as exc_info:
                approve_draft(99999, user)
            
            assert exc_info.value.code == 'DRAFT_NOT_FOUND'
    
    def test_already_approved_draft(self, app, location, article, batch, user, surplus, stock, draft):
        """Already approved draft cannot be approved again."""
        with app.app_context():
            # First approval
            approve_draft(draft, user)
            db.session.commit()
            
            # Second approval should fail
            with pytest.raises(AppError) as exc_info:
                approve_draft(draft, user)
            
            assert exc_info.value.code == 'DRAFT_NOT_DRAFT'
    
    def test_user_not_found(self, app, draft):
        """Non-existent user raises error."""
        with app.app_context():
            with pytest.raises(AppError) as exc_info:
                approve_draft(draft, 99999)
            
            assert exc_info.value.code == 'USER_NOT_FOUND'


class TestRejectDraft:
    """Test draft rejection."""
    
    def test_reject_draft_no_inventory_change(self, app, location, article, batch, user, surplus, stock, draft):
        """Rejection should not change inventory."""
        with app.app_context():
            result = reject_draft(draft, user, 'Incorrect weight')
            db.session.commit()
            
            assert result['new_status'] == 'REJECTED'
            
            # Verify no inventory changes
            surplus_obj = Surplus.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(surplus_obj.quantity_kg) == 5.0
            
            stock_obj = Stock.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(stock_obj.quantity_kg) == 10.0
