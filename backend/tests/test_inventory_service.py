"""Tests for inventory adjustment service."""
import pytest
from decimal import Decimal

from app.extensions import db
from app.models import Stock, Surplus, Transaction, User
from app.services.inventory_service import adjust_inventory
from app.error_handling import AppError


class TestInventoryAdjustSetMode:
    """Test inventory adjustment with set mode."""
    
    def test_set_stock_value(self, app, location, article, batch, user):
        """Set stock to absolute value."""
        with app.app_context():
            # Make user admin
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            result = adjust_inventory(
                location_id=location,
                article_id=article,
                batch_id=batch,
                target='stock',
                mode='set',
                quantity_kg=100.00,
                actor_user_id=user,
                note='Initial stock setup'
            )
            db.session.commit()
            
            assert result['new_value'] == 100.0
            assert result['previous_value'] == 0.0
            assert result['target'] == 'stock'
            assert result['mode'] == 'set'
            
            # Verify DB
            stock = Stock.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(stock.quantity_kg) == 100.0
    
    def test_set_surplus_value(self, app, location, article, batch, user):
        """Set surplus to absolute value."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            result = adjust_inventory(
                location_id=location,
                article_id=article,
                batch_id=batch,
                target='surplus',
                mode='set',
                quantity_kg=25.50,
                actor_user_id=user
            )
            db.session.commit()
            
            assert result['new_value'] == 25.5
            
            surplus = Surplus.query.filter_by(
                location_id=location,
                article_id=article,
                batch_id=batch
            ).first()
            assert float(surplus.quantity_kg) == 25.5


class TestInventoryAdjustDeltaMode:
    """Test inventory adjustment with delta mode."""
    
    def test_delta_add_to_stock(self, app, location, article, batch, user, stock):
        """Add to existing stock with delta."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            # stock fixture has 10kg
            result = adjust_inventory(
                location_id=location,
                article_id=article,
                batch_id=batch,
                target='stock',
                mode='delta',
                quantity_kg=5.00,
                actor_user_id=user
            )
            db.session.commit()
            
            assert result['previous_value'] == 10.0
            assert result['new_value'] == 15.0
            assert result['delta'] == 5.0
    
    def test_delta_subtract_valid(self, app, location, article, batch, user, stock):
        """Subtract valid amount from stock."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            result = adjust_inventory(
                location_id=location,
                article_id=article,
                batch_id=batch,
                target='stock',
                mode='delta',
                quantity_kg=-3.00,
                actor_user_id=user
            )
            db.session.commit()
            
            assert result['previous_value'] == 10.0
            assert result['new_value'] == 7.0
    
    def test_delta_below_zero_blocked(self, app, location, article, batch, user, stock):
        """Cannot delta below zero."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                adjust_inventory(
                    location_id=location,
                    article_id=article,
                    batch_id=batch,
                    target='stock',
                    mode='delta',
                    quantity_kg=-15.00,  # Would go to -5
                    actor_user_id=user
                )
            
            assert exc.value.code == 'NEGATIVE_INVENTORY_NOT_ALLOWED'


class TestInventoryAdjustValidation:
    """Test validation errors."""
    
    def test_non_admin_rejected(self, app, location, article, batch, user):
        """Non-admin users cannot adjust inventory."""
        with app.app_context():
            # user is ADMIN by default in fixture, change to OPERATOR
            u = db.session.get(User, user)
            u.role = 'OPERATOR'
            db.session.commit()
            
            with pytest.raises(AppError) as exc:
                adjust_inventory(
                    location_id=location,
                    article_id=article,
                    batch_id=batch,
                    target='stock',
                    mode='set',
                    quantity_kg=100.0,
                    actor_user_id=user
                )
            
            assert exc.value.code == 'VALIDATION_ERROR'
            assert 'ADMIN' in exc.value.message
    
    def test_creates_transaction(self, app, location, article, batch, user):
        """Adjustment creates transaction record."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            result = adjust_inventory(
                location_id=location,
                article_id=article,
                batch_id=batch,
                target='stock',
                mode='set',
                quantity_kg=50.0,
                actor_user_id=user,
                note='Test adjustment'
            )
            db.session.commit()
            
            tx = Transaction.query.filter_by(
                tx_type='INVENTORY_ADJUSTMENT'
            ).first()
            
            assert tx is not None
            assert float(tx.quantity_kg) == 50.0
            assert tx.meta['target'] == 'stock'
            assert tx.meta['mode'] == 'set'
            assert tx.meta['note'] == 'Test adjustment'
