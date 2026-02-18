"""Tests for v3 Phase 1 foundation: UOM catalog, has_batch, category."""
import pytest
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import Article, UomCatalog, User
from app.services.uom_service import get_or_create_uom, list_uom


class TestUomCatalog:
    """UOM catalog open-entry behavior."""

    def test_create_new_uom(self, app):
        with app.app_context():
            uom = get_or_create_uom('KG')
            assert uom.code == 'KG'
            assert uom.id is not None
            uom2 = get_or_create_uom('kg')
            assert uom2.id == uom.id
            db.session.commit()

    def test_create_novel_uom(self, app):
        with app.app_context():
            uom = get_or_create_uom('STUECK')
            assert uom.code == 'STUECK'
            assert UomCatalog.query.filter_by(code='STUECK').count() == 1
            db.session.commit()

    def test_uom_normalization(self, app):
        with app.app_context():
            uom = get_or_create_uom('  pak  ')
            assert uom.code == 'PAK'
            db.session.commit()

    def test_empty_uom_raises(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                get_or_create_uom('  ')

    def test_list_uom(self, app):
        with app.app_context():
            get_or_create_uom('KG')
            get_or_create_uom('L')
            db.session.commit()
            items = list_uom()
            assert len(items) >= 2
            codes = [u.code for u in items]
            assert codes == sorted(codes)


class TestUomEndpoint:
    """GET /api/uom list endpoint."""

    def test_list_uom_requires_auth(self, client):
        resp = client.get('/api/uom/')
        assert resp.status_code in (401, 422)

    def test_list_uom_returns_items(self, client, app):
        with app.app_context():
            u = User(username='uom_test', role='ADMIN', is_active=True)
            db.session.add(u)
            db.session.commit()
            get_or_create_uom('KG')
            get_or_create_uom('L')
            db.session.commit()
            token = create_access_token(identity=str(u.id))

        resp = client.get('/api/uom/', headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data
        assert len(data['items']) >= 2


class TestArticleHasBatch:
    """Article has_batch behavior."""

    def test_has_batch_true(self, app):
        with app.app_context():
            art = Article(article_no='HB-001', uom='KG', is_paint=True, has_batch=True)
            db.session.add(art)
            db.session.commit()
            assert art.has_batch is True

    def test_has_batch_false(self, app):
        with app.app_context():
            art = Article(article_no='HB-002', uom='KG', is_paint=False, has_batch=False)
            db.session.add(art)
            db.session.commit()
            assert art.has_batch is False

    def test_has_batch_independent_of_is_paint(self, app):
        with app.app_context():
            art = Article(article_no='HB-003', uom='KOM', is_paint=False, has_batch=True)
            db.session.add(art)
            db.session.commit()
            assert art.has_batch is True
            assert art.is_paint is False


class TestArticleCategory:
    """Article category."""

    def test_valid_category(self, app):
        with app.app_context():
            art = Article(article_no='CAT-001', uom='KG', category='raw_material')
            db.session.add(art)
            db.session.commit()
            assert art.category == 'raw_material'

    def test_null_category(self, app):
        with app.app_context():
            art = Article(article_no='CAT-002', uom='KG')
            db.session.add(art)
            db.session.commit()
            assert art.category is None


class TestArticleCreateApiV3:
    """POST /api/articles with v3 fields."""

    def test_create_article_with_open_uom(self, client, app):
        with app.app_context():
            u = User(username='adm_v3_1', role='ADMIN', is_active=True)
            db.session.add(u)
            db.session.commit()
            token = create_access_token(identity=str(u.id), additional_claims={'role': 'ADMIN'})

        resp = client.post('/api/articles', json={
            'article_no': 'OPEN-UOM-1',
            'uom': 'KOM',
            'is_paint': False,
        }, headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['uom'] == 'KOM'
        assert data['has_batch'] is False  # derived from is_paint

    def test_create_article_has_batch_explicit(self, client, app):
        with app.app_context():
            u = User(username='adm_v3_2', role='ADMIN', is_active=True)
            db.session.add(u)
            db.session.commit()
            token = create_access_token(identity=str(u.id), additional_claims={'role': 'ADMIN'})

        resp = client.post('/api/articles', json={
            'article_no': 'EXPLICIT-HB-1',
            'uom': 'KG',
            'is_paint': False,
            'has_batch': True,
        }, headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['has_batch'] is True
        assert data['is_paint'] is False

    def test_create_article_uom_normalized(self, client, app):
        with app.app_context():
            u = User(username='adm_v3_3', role='ADMIN', is_active=True)
            db.session.add(u)
            db.session.commit()
            token = create_access_token(identity=str(u.id), additional_claims={'role': 'ADMIN'})

        resp = client.post('/api/articles', json={
            'article_no': 'NORM-UOM-1',
            'uom': 'kg',
        }, headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 201
        assert resp.get_json()['uom'] == 'KG'

    def test_create_article_uom_persisted_in_catalog(self, client, app):
        with app.app_context():
            u = User(username='adm_v3_4', role='ADMIN', is_active=True)
            db.session.add(u)
            db.session.commit()
            token = create_access_token(identity=str(u.id), additional_claims={'role': 'ADMIN'})

        resp = client.post('/api/articles', json={
            'article_no': 'CAT-UOM-1',
            'uom': 'STUECK',
        }, headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 201
        with app.app_context():
            assert UomCatalog.query.filter_by(code='STUECK').count() == 1
