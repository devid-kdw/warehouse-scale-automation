import pytest
from flask_jwt_extended import create_access_token
from app.models import Article, Batch, WeighInDraft, DraftGroup
from app.extensions import db

def test_create_group_consumable_no_batch(client, app, user, location):
    """Test creating a draft group with a consumable line and NO batch_id."""
    
    with app.app_context():
        # Setup a consumable article
        article = Article(
            article_no="CONS-001",
            description="Cleaning Cloths",
            uom="PCS",
            is_paint=False,
            is_active=True
        )
        db.session.add(article)
        db.session.commit()
        art_id = article.id
        
        token = create_access_token(identity=str(user))
    
    payload = {
        "location_id": location,
        "name": "Consumable Group",
        "lines": [{
            "article_id": art_id,
            "quantity_kg": 5.0,
            "client_event_id": "evt-cons-1"
        }]
    }
    
    res = client.post(
        '/api/draft-groups',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert res.status_code == 201
    group_id = res.json['id']
    
    # 3. Verify draft has the 'NA' batch
    with app.app_context():
        draft = db.session.query(WeighInDraft).filter_by(draft_group_id=group_id).first()
        assert draft is not None
        assert draft.batch.batch_code == 'NA'
        assert draft.article_id == art_id

def test_create_group_paint_no_batch_fails(client, app, user, location):
    """Test creating a draft group with a paint article and NO batch_id should fail."""
    
    with app.app_context():
        # Setup a paint article
        article = Article(
            article_no="PNT-001",
            description="Base White",
            uom="KG",
            is_paint=True,
            is_active=True
        )
        db.session.add(article)
        db.session.commit()
        art_id = article.id
        
        token = create_access_token(identity=str(user))
    
    payload = {
        "location_id": location,
        "name": "Paint Group Fail",
        "lines": [{
            "article_id": art_id,
            "quantity_kg": 10.0,
            "client_event_id": "evt-pnt-fail"
        }]
    }
    
    res = client.post(
        '/api/draft-groups',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert res.status_code == 400
    assert res.json['error']['code'] == 'BATCH_REQUIRED'
