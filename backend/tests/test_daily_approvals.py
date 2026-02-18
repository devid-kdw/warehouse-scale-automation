import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from app.models import WeighInDraft, Article, Batch, Location, Stock, Surplus
from app.services.approval_service import (
    get_daily_approvals_list, get_daily_approvals_detail,
    update_aggregate_quantity, approve_day, reject_day,
    BERLIN_TZ
)
from app.extensions import db
from app.error_handling import AppError

def test_daily_approvals_grouping(app, location, article, batch):
    """Test drafts are grouped by Berlin operational day and location."""
    with app.app_context():
        # Berlin day is UTC+1 (or +2 in DST). 22:00 UTC is next day in Berlin.
        d1_time = datetime(2026, 2, 17, 10, 0, 0, tzinfo=timezone.utc) # 2026-02-17 in Berlin
        d2_time = datetime(2026, 2, 17, 23, 30, 0, tzinfo=timezone.utc) # 2026-02-18 in Berlin
        
        d1 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('10.50'),
            uom='KG',
            client_event_id='group-1',
            created_at=d1_time
        )
        d2 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('5.25'),
            uom='KG',
            client_event_id='group-2',
            created_at=d2_time
        )
        db.session.add_all([d1, d2])
        db.session.commit()
        
        groups = get_daily_approvals_list()
        # Filter for our specific dates and location
        active_days = [g['date'] for g in groups if g['location_id'] == location]
        assert '2026-02-17' in active_days
        assert '2026-02-18' in active_days

def test_aggregate_edit_delta_rule(app, user, location, article, batch):
    """Test aggregate quantity edit adjusts the first draft by delta."""
    with app.app_context():
        now = datetime.now(timezone.utc)
        today_str = now.astimezone(BERLIN_TZ).strftime('%Y-%m-%d')
        
        d1 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('10.00'),
            client_event_id='edit-1',
            created_at=now,
            uom='KG'
        )
        d2 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('5.00'),
            client_event_id='edit-2',
            created_at=now,
            uom='KG'
        )
        db.session.add_all([d1, d2])
        db.session.commit()
        
        # Target total = 20.00 (Current = 15.00). Delta = +5.00.
        res = update_aggregate_quantity(
            date_str=today_str,
            location_id=location,
            article_id=article,
            batch_id=batch,
            new_total_qty=Decimal('20.00'),
            actor_user_id=user
        )
        db.session.commit()
        
        assert res['status'] == 'updated'
        assert res['delta'] == 5.0
        
        db.session.refresh(d1)
        db.session.refresh(d2)
        assert float(d1.quantity) == 15.00
        assert float(d2.quantity) == 5.00

def test_aggregate_edit_negative_validation(app, user, location, article, batch):
    """Test adjustment that results in <= 0 quantity is rejected."""
    with app.app_context():
        now = datetime.now(timezone.utc)
        today_str = now.astimezone(BERLIN_TZ).strftime('%Y-%m-%d')
        
        d1 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('10.00'),
            uom='KG',
            client_event_id='neg-1',
            created_at=now
        )
        db.session.add(d1)
        db.session.commit()
        
        with pytest.raises(AppError) as exc:
            update_aggregate_quantity(
                date_str=today_str,
                location_id=location,
                article_id=article,
                batch_id=batch,
                new_total_qty=Decimal('0.00'),
                actor_user_id=user
            )
        assert exc.value.code == 'INVALID_ADJUSTMENT'

def test_uom_consistency_validation(app, user, location, article, batch):
    """Test aggregation fails if mixed UOMs are present in a group."""
    with app.app_context():
        now = datetime.now(timezone.utc)
        today_str = now.astimezone(BERLIN_TZ).strftime('%Y-%m-%d')
        
        d1 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('10.00'),
            client_event_id='uom-1',
            created_at=now,
            uom='KG'
        )
        d2 = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity=Decimal('5.00'),
            client_event_id='uom-2',
            created_at=now,
            uom='L'
        )
        db.session.add_all([d1, d2])
        db.session.commit()
        
        with pytest.raises(AppError) as exc:
            get_daily_approvals_detail(today_str, location)
        assert exc.value.code == 'MIXED_UOM_IN_AGGREGATION'

def test_mass_approval_atomicity(app, user, location, article, batch):
    """Test mass approval for a whole day's drafts."""
    with app.app_context():
        now = datetime.now(timezone.utc)
        today_str = now.astimezone(BERLIN_TZ).strftime('%Y-%m-%d')
        
        # Setup inventory: 100kg stock
        stock_obj = Stock(location_id=location, article_id=article, batch_id=batch, quantity=Decimal('100.00'), uom='KG')
        db.session.add(stock_obj)
        
        d1 = WeighInDraft(
            location_id=location, article_id=article, batch_id=batch,
            quantity=Decimal('10.00'), uom='KG', client_event_id='mass-1', created_at=now
        )
        d2 = WeighInDraft(
            location_id=location, article_id=article, batch_id=batch,
            quantity=Decimal('20.00'), uom='KG', client_event_id='mass-2', created_at=now
        )
        db.session.add_all([d1, d2])
        db.session.commit()
        
        res = approve_day(today_str, location, user)
        db.session.commit()
        
        assert res['status'] == 'success'
        assert res['count'] == 2
        
        db.session.refresh(stock_obj)
        assert float(stock_obj.quantity) == 70.00
        
        db.session.refresh(d1)
        db.session.refresh(d2)
        assert d1.status == WeighInDraft.STATUS_APPROVED
        assert d2.status == WeighInDraft.STATUS_APPROVED
