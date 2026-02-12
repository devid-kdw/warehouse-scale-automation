"""Shared pytest fixtures for all tests."""
import os
from datetime import timedelta
import pytest

from app import create_app
from app.extensions import db
from app.models import User, Location, Article, Batch, Stock, Surplus, WeighInDraft


class TestConfig:
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql+psycopg2://localhost:5432/warehouse_test'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'testing'
    
    # JWT Configuration
    JWT_SECRET_KEY = 'test-jwt-secret-key-for-testing'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Required for flask-smorest
    API_TITLE = 'Warehouse API Test'
    API_VERSION = '0.1.0'
    OPENAPI_VERSION = '3.0.3'
    
    # CORS
    CORS_ORIGINS = 'http://localhost:3000'
    CORS_ALLOW_ALL = False
    
    @classmethod
    def get_cors_origins(cls):
        return [cls.CORS_ORIGINS]
    
    @classmethod
    def validate_production_config(cls):
        """No-op for testing."""
        pass


@pytest.fixture
def app():
    """Create application for testing."""
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for API requests."""
    return app.test_client()


@pytest.fixture
def location(app):
    """Create test location with id=13 (per RULES_OF_ENGAGEMENT)."""
    with app.app_context():
        loc = Location(id=13, code='13', name='Test Warehouse')
        db.session.add(loc)
        db.session.commit()
        loc_id = loc.id
    return loc_id


@pytest.fixture
def user(app):
    """Create test user (username: testuser, role: ADMIN)."""
    with app.app_context():
        u = User(username='testuser', role='ADMIN', is_active=True)
        db.session.add(u)
        db.session.commit()
        user_id = u.id
    return user_id


@pytest.fixture
def article(app):
    """Create test article."""
    with app.app_context():
        art = Article(article_no='TEST-001', description='Test Article', uom='KG')
        db.session.add(art)
        db.session.commit()
        art_id = art.id
    return art_id


@pytest.fixture
def batch(app, article):
    """Create test batch."""
    from decimal import Decimal
    with app.app_context():
        b = Batch(article_id=article, batch_code='1234')
        db.session.add(b)
        db.session.commit()
        batch_id = b.id
    return batch_id


@pytest.fixture
def stock(app, location, article, batch):
    """Create test stock with 10kg."""
    from decimal import Decimal
    with app.app_context():
        s = Stock(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity_kg=Decimal('10.00')
        )
        db.session.add(s)
        db.session.commit()
        stock_id = s.id
    return stock_id


@pytest.fixture
def surplus(app, location, article, batch):
    """Create test surplus with 5kg."""
    from decimal import Decimal
    with app.app_context():
        s = Surplus(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity_kg=Decimal('5.00')
        )
        db.session.add(s)
        db.session.commit()
        surplus_id = s.id
    return surplus_id


@pytest.fixture
def draft(app, location, article, batch, user):
    """Create test draft for 3kg."""
    from decimal import Decimal
    with app.app_context():
        d = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity_kg=Decimal('3.00'),
            client_event_id='test-event-001',
            created_by_user_id=user,
            source='manual'
        )
        db.session.add(d)
        db.session.commit()
        draft_id = d.id
    return draft_id


@pytest.fixture
def pending_draft(app, location, article, batch, user):
    """Create pending draft for 5kg (for approval tests)."""
    from decimal import Decimal
    with app.app_context():
        d = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity_kg=Decimal('5.00'),
            client_event_id='test-pending-draft-001',
            created_by_user_id=user,
            source='manual',
            status='DRAFT'
        )
        db.session.add(d)
        db.session.commit()
        draft_id = d.id
    return draft_id
