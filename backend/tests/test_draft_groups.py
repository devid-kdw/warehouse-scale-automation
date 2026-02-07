"""Tests for Draft Group service and endpoints."""
from datetime import date
from decimal import Decimal
import pytest
from app.extensions import db
from app.models import DraftGroup, WeighInDraft, Stock, Surplus, Transaction
from app.services import draft_group_service
from app.error_handling import AppError, InsufficientStockError


class TestDraftGroupService:
    """Test Draft Group service logic."""

    def test_create_group_single_line_compatibility(self, app, location, article, batch, user):
        """Creating a single-line group auto-names it correctly."""
        with app.app_context():
            lines = [{
                'article_id': article,
                'batch_id': batch,
                'quantity_kg': 10.5,
                'client_event_id': 'evt-001',
                'note': 'Single line test'
            }]
            
            group = draft_group_service.create_group(
                location_id=location,
                user_id=user,
                lines=lines,
                source='ui_operator'
            )
            
            assert group.name.startswith("OperatorDraft_") or "Draft_" in group.name
            assert len(group.drafts) == 1
            assert group.drafts[0].quantity_kg == Decimal('10.50')
            assert group.status == 'DRAFT'

    def test_create_group_multi_line(self, app, location, article, batch, user):
        """Creating a multi-line group works."""
        with app.app_context():
            lines = [
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 5.0, 'client_event_id': 'evt-m1'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 3.0, 'client_event_id': 'evt-m2'}
            ]
            
            group = draft_group_service.create_group(
                location_id=location,
                user_id=user,
                lines=lines,
                name='Batch Production A',
                source='ui_admin'
            )
            
            assert group.name == 'Batch Production A'
            assert len(group.drafts) == 2
            assert group.total_quantity_kg == 8.0

    def test_approve_group_atomic_success(self, app, location, article, batch, user):
        """Group approval succeeds atomically and updates inventory."""
        with app.app_context():
            # Prep stock: 10kg
            s = Stock(location_id=location, article_id=article, batch_id=batch, quantity_kg=Decimal('10.00'))
            db.session.add(s)
            
            lines = [
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 4.0, 'client_event_id': 'evt-ok1'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 4.0, 'client_event_id': 'evt-ok2'}
            ]
            group = draft_group_service.create_group(location, user, lines)
            
            result = draft_group_service.approve_group(group.id, user)
            
            assert group.status == 'APPROVED'
            assert all(d.status == 'APPROVED' for d in group.drafts)
            
            # Verify stock: 10 - 4 - 4 = 2
            stock_after = Stock.query.filter_by(location_id=location, article_id=article, batch_id=batch).one()
            assert stock_after.quantity_kg == Decimal('2.00')

    def test_approve_group_atomic_failure(self, app, location, article, batch, user):
        """If one line fails due to stock, the whole group remains DRAFT and no stock is changed."""
        with app.app_context():
            # Prep stock: 5kg
            s = Stock(location_id=location, article_id=article, batch_id=batch, quantity_kg=Decimal('5.00'))
            db.session.add(s)
            db.session.commit()
            
            lines = [
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 3.0, 'client_event_id': 'evt-fail1'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 3.0, 'client_event_id': 'evt-fail2'} # Total 6.0 > 5.0
            ]
            group = draft_group_service.create_group(location, user, lines)
            
            with pytest.raises(InsufficientStockError):
                draft_group_service.approve_group(group.id, user)
            
            # Rolled back? (In-request rollback)
            db.session.rollback()
            
            # Verify state
            group_reload = db.session.get(DraftGroup, group.id)
            assert group_reload.status == 'DRAFT'
            assert all(d.status == 'DRAFT' for d in group_reload.drafts)
            
            stock_reload = Stock.query.filter_by(location_id=location, article_id=article, batch_id=batch).one()
            assert stock_reload.quantity_kg == Decimal('5.00')

    def test_reject_group_atomic(self, app, location, article, batch, user):
        """Rejecting a group updates all lines."""
        with app.app_context():
            lines = [{'article_id': article, 'batch_id': batch, 'quantity_kg': 1.0, 'client_event_id': 'evt-rej'}]
            group = draft_group_service.create_group(location, user, lines)
            
            draft_group_service.reject_group(group.id, user)
            
            assert group.status == 'REJECTED'
            assert group.drafts[0].status == 'REJECTED'

    def test_precision_summing(self, app, location, article, batch, user):
        """Draft group correctly sums small decimals (0.01)."""
        with app.app_context():
            lines = [
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 0.01, 'client_event_id': 'evt-p1'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 0.01, 'client_event_id': 'evt-p2'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 0.01, 'client_event_id': 'evt-p3'}
            ]
            group = draft_group_service.create_group(location, user, lines)
            # 0.01 + 0.01 + 0.01 = 0.03
            assert group.total_quantity_kg == 0.03

    def test_create_group_auto_name_pattern(self, app, location, user, article, batch):
        """Multi-line group without name gets auto-generated name."""
        with app.app_context():
            # Clear existing groups to ensure counter starts at 1
            db.session.query(WeighInDraft).delete()
            db.session.query(DraftGroup).delete()
            db.session.commit()
            
            lines = [
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 1.0, 'client_event_id': 'auto-1'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 1.0, 'client_event_id': 'auto-2'}
            ]
            
            # 1. First group
            group1 = draft_group_service.create_group(
                location, user, lines, source='ui_admin'
            )
            
            today_str = date.today().strftime('%Y-%m-%d')
            expected_name1 = f"AdminDraft_001-{today_str}"
            assert group1.name == expected_name1
            
            # 2. Second group (counter increments)
            lines2 = [{'article_id': article, 'batch_id': batch, 'quantity_kg': 1.0, 'client_event_id': 'auto-3'}] # Single line but check standard pattern if name missing? 
            # Wait, single line logic has specific override if len=1 and no name -> AutoSingleDraft_...
            # The new logic says: if not name -> generate name.
            # But specific logic for single line was:
            # if not name and len(lines) == 1: name = AutoSingleDraft...
            # The new code REMOVED that specific block and replaced it with general _generate_group_name?
            # Let's check the code I wrote.
            # I replaced:
            # -    # Auto-name if single line and no name provided
            # -    if not name and len(lines) == 1:
            # with:
            # +    # Auto-name if no name provided
            # +    if not name:
            # +        name = _generate_group_name(source)
            
            # So "AutoSingleDraft" logic is GONE.
            # I should update the "test_create_group_single_line_compatibility" test too!
            
            group2 = draft_group_service.create_group(
                location, user, lines=lines2, source='ui_admin'
            )
            expected_name2 = f"AdminDraft_002-{today_str}"
            assert group2.name == expected_name2


class TestDraftGroupAPI:
    """Test Draft Group API endpoints."""

    def test_list_groups(self, client, app, location, user, article, batch):
        """GET /api/draft-groups returns list."""
        with app.app_context():
            # Create a group via service first
            draft_group_service.create_group(location, user, [{'article_id': article, 'batch_id': batch, 'quantity_kg': 1.0, 'client_event_id': 'evt-api-1'}])
        
        # Get JWT for admin
        from flask_jwt_extended import create_access_token
        with app.app_context():
            token = create_access_token(identity=str(user))
            
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/draft-groups', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
        assert 'line_count' in data['items'][0]
        assert 'total_quantity_kg' in data['items'][0]

    def test_post_group_with_lines(self, client, app, location, user, article, batch):
        """POST /api/draft-groups creates a group."""
        from flask_jwt_extended import create_access_token
        with app.app_context():
            token = create_access_token(identity=str(user))
            
        payload = {
            'location_id': location,
            'name': 'API Group',
            'lines': [
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 2.5, 'client_event_id': 'api-evt-1'},
                {'article_id': article, 'batch_id': batch, 'quantity_kg': 1.5, 'client_event_id': 'api-evt-2'}
            ]
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.post('/api/draft-groups', json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'API Group'
        assert data['line_count'] == 2
        assert data['total_quantity_kg'] == 4.0

    def test_backward_compatibility_single_post(self, client, app, location, user, article, batch):
        """POST /api/drafts still works and creates an implicit group."""
        from flask_jwt_extended import create_access_token
        with app.app_context():
            token = create_access_token(identity=str(user))
            
        payload = {
            'location_id': location,
            'article_id': article,
            'batch_id': batch,
            'quantity_kg': 7.77,
            'client_event_id': 'legacy-evt-1'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.post('/api/drafts', json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['quantity_kg'] == 7.77
        
        # Verify group exists in DB
        with app.app_context():
            d = WeighInDraft.query.filter_by(client_event_id='legacy-evt-1').one()
            assert d.draft_group_id is not None
            assert d.draft_group_id is not None
            g = d.draft_group
            assert "Draft_" in g.name

    def test_rename_group(self, client, app, location, user, article, batch):
        """PATCH /api/draft-groups/{id} renames the group."""
        from flask_jwt_extended import create_access_token
        with app.app_context():
            token = create_access_token(identity=str(user))
            # Create group
            g = draft_group_service.create_group(location, user, [{'article_id': article, 'batch_id': batch, 'quantity_kg': 1.0, 'client_event_id': 'rn-1'}], name="OldName")
            group_id = g.id
            
        headers = {'Authorization': f'Bearer {token}'}
        payload = {'name': 'NewNameUpdated'}
        
        response = client.patch(f'/api/draft-groups/{group_id}', json=payload, headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'NewNameUpdated'
        
        with app.app_context():
            g = db.session.get(DraftGroup, group_id)
            assert g.name == 'NewNameUpdated'

