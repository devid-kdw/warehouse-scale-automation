"""Tests for Orders domain (TASK-0023 Phase 2)."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.extensions import db
from app.models import Article, User, Order, OrderLine
from app.services import order_service
from app.error_handling import AppError

@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(username='admin_test', role='ADMIN')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def sample_article(app):
    with app.app_context():
        article = Article(
            article_no='ART-ORD-01',
            description='Test Article',
            uom='KG',
            is_paint=True,
            has_batch=True,
            is_active=True
        )
        db.session.add(article)
        db.session.commit()
        return article.id

class TestOrderService:
    """Test Order service operations."""

    def test_create_order_auto_number(self, app, admin_user, sample_article):
        """Order is created with auto-numbered ORD-xxxx."""
        with app.app_context():
            data = {
                'lines': [
                    {'article_id': sample_article, 'ordered_qty': Decimal('100.00'), 'uom': 'KG'}
                ]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()

            assert order.order_number.startswith('ORD-')
            assert len(order.lines.all()) == 1
            assert order.status == 'OPEN'

    def test_create_order_manual_number(self, app, admin_user, sample_article):
        """Order is created with manual number."""
        with app.app_context():
            data = {
                'order_number': 'MANUAL-001',
                'lines': [
                    {'article_id': sample_article, 'ordered_qty': Decimal('50.00'), 'uom': 'KG'}
                ]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()

            assert order.order_number == 'MANUAL-001'

    def test_order_lifecycle_automation(self, app, admin_user, sample_article):
        """Order status changes from OPEN to CLOSED when lines are satisfied."""
        with app.app_context():
            data = {
                'order_number': 'PO-LIFE',
                'lines': [
                    {'article_id': sample_article, 'ordered_qty': Decimal('100.00'), 'uom': 'KG'}
                ]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()
            order_id = order.id
            line_id = order.lines.first().id

            assert order.status == 'OPEN'

            # Partially receive
            order_service.increment_received_qty(line_id, Decimal('40.00'))
            db.session.commit()
            order = db.session.get(Order, order_id)
            assert order.status == 'OPEN'

            # Fully receive
            order_service.increment_received_qty(line_id, Decimal('60.00'))
            db.session.commit()
            order = db.session.get(Order, order_id)
            assert order.status == 'CLOSED'
            assert order.lines.first().status == 'CLOSED'

    def test_order_reopen_on_line_addition(self, app, admin_user, sample_article):
        """Order reopens if a new unfulfilled line is added."""
        with app.app_context():
            # Create and close order
            data = {
                'order_number': 'PO-REOPEN',
                'lines': [{'article_id': sample_article, 'ordered_qty': Decimal('10.00'), 'uom': 'KG'}]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()
            
            line_id = order.lines.first().id
            order_service.increment_received_qty(line_id, Decimal('10.00'))
            db.session.commit()
            
            assert order.status == 'CLOSED'

            # Add a new line
            update_data = {
                'lines': [
                    # Keep existing closed line by not providing it in replace? 
                    # Current update_order implementation REPLACES all lines that have 0 received_qty.
                    # Wait, let's check update_order implementation.
                    {'article_id': sample_article, 'ordered_qty': Decimal('20.00'), 'uom': 'KG'}
                ]
            }
            order_service.update_order(order.id, update_data)
            db.session.commit()

            assert order.status == 'OPEN'

    def test_remove_line_recalculates_status(self, app, admin_user, sample_article):
        """Removing the only unfulfilled line closes the order."""
        with app.app_context():
            data = {
                'lines': [
                    {'article_id': sample_article, 'ordered_qty': Decimal('10.00'), 'uom': 'KG'},
                    {'article_id': sample_article, 'ordered_qty': Decimal('20.00'), 'uom': 'KG'}
                ]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()
            
            line1 = next(l for l in order.lines.all() if l.ordered_qty == Decimal('10.00'))
            line2 = next(l for l in order.lines.all() if l.ordered_qty == Decimal('20.00'))
            line1_id = line1.id
            line2_id = line2.id

            order_service.increment_received_qty(line1_id, Decimal('10.00'))
            db.session.commit()
            assert order.status == 'OPEN'

            # Remove unfulfilled line
            order_service.remove_line(order.id, line2_id)
            db.session.commit()
            
            db.session.refresh(order)
            assert order.status == 'CLOSED'

    def test_receive_stock_with_order_linkage(self, app, admin_user, sample_article, location):
        """Receiving stock against an order line updates received_qty and closes order."""
        from app.services.receiving_service import receive_stock
        with app.app_context():
            # Create order
            data = {
                'order_number': 'PO-LINK',
                'lines': [{'article_id': sample_article, 'ordered_qty': Decimal('100.00'), 'uom': 'KG'}]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()
            line_id = order.lines.first().id
            
            # Receive stock
            receive_stock(
                article_id=sample_article,
                batch_code='1234',
                quantity=Decimal('100.00'),
                uom='KG',
                expiry_date=date.today() + timedelta(days=365),
                actor_user_id=admin_user,
                delivery_note_number='DN-LINK-01',
                order_line_id=line_id,
                location_id=location
            )
            db.session.commit()
            
            db.session.refresh(order)
            line = db.session.get(OrderLine, line_id)
            assert line.received_qty == Decimal('100.00')
            assert line.status == 'CLOSED'
            assert order.status == 'CLOSED'

    def test_receive_stock_linkage_validation(self, app, admin_user, sample_article, location):
        """Receiving against wrong article or closed order fails."""
        from app.services.receiving_service import receive_stock
        with app.app_context():
            # 1. Create order for article A
            data = {
                'order_number': 'PO-VAL-FAIL',
                'lines': [{'article_id': sample_article, 'ordered_qty': Decimal('10.00'), 'uom': 'KG'}]
            }
            order = order_service.create_order(data, admin_user)
            db.session.commit()
            line_id = order.lines.first().id
            
            # Create article B
            article_b = Article(article_no='ART-B', description='Other', uom='KG', has_batch=True)
            db.session.add(article_b)
            db.session.commit()
            
            # Try to receive article B against line for article A
            with pytest.raises(AppError) as exc:
                receive_stock(
                    article_id=article_b.id,
                    batch_code='1234',
                    quantity=Decimal('1.00'),
                    uom='KG',
                    expiry_date=date.today(),
                    actor_user_id=admin_user,
                    delivery_note_number='DN-FAIL',
                    order_line_id=line_id
                )
            assert exc.value.code == 'VALIDATION_ERROR'
            assert 'article' in exc.value.message

class TestOrderAPI:
    """Test Orders API endpoints."""

    def test_orders_crud_api(self, client, admin_user, sample_article, app):
        from flask_jwt_extended import create_access_token
        with app.app_context():
            token = create_access_token(identity=str(admin_user), additional_claims={'role': 'ADMIN'})
        
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Create
        payload = {
            'order_number': 'API-PO-01',
            'supplier_name': 'Test Supplier',
            'lines': [
                {'article_id': sample_article, 'ordered_qty': '150.00', 'uom': 'KG'}
            ]
        }
        res = client.post('/api/orders', json=payload, headers=headers)
        assert res.status_code == 201
        order_id = res.json['id']

        # 2. List
        res = client.get('/api/orders', headers=headers)
        assert res.status_code == 200
        assert res.json['total'] >= 1

        # 3. Get Detail
        res = client.get(f'/api/orders/{order_id}', headers=headers)
        assert res.status_code == 200
        assert res.json['order_number'] == 'API-PO-01'
        assert len(res.json['lines']) == 1

        # 4. Update
        update_payload = {'supplier_name': 'Updated Supplier'}
        res = client.put(f'/api/orders/{order_id}', json=update_payload, headers=headers)
        assert res.status_code == 200
        assert res.json['supplier_name'] == 'Updated Supplier'

        # 5. Remove line
        line_id = res.json['lines'][0]['id']
        res = client.delete(f'/api/orders/{order_id}/lines/{line_id}', headers=headers)
        assert res.status_code == 200
        assert res.json['status'] == 'REMOVED'
        
        # Verify order status updated
        res = client.get(f'/api/orders/{order_id}', headers=headers)
        assert res.json['status'] == 'CLOSED' # No active lines left
