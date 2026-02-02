"""CLI seed command."""
import click
from decimal import Decimal
from flask.cli import with_appcontext

from ..extensions import db
from ..models import User, Location, Article, Batch, Stock, Surplus


@click.command('seed')
@click.option('--demo', is_flag=True, help='Include demo articles, batches, and inventory')
@with_appcontext
def seed_command(demo):
    """Seed initial data: location "13" and users.
    
    Use --demo flag to also create sample articles, batches, and inventory.
    """
    click.echo('Seeding database...')
    
    # Create location "13" if not exists
    location = Location.query.filter_by(code='13').first()
    if not location:
        location = Location(code='13', name='Main Warehouse')
        db.session.add(location)
        db.session.flush()
        click.echo('  Created location: 13 (Main Warehouse)')
    else:
        click.echo('  Location 13 already exists')
    
    # Create admin user "stefan" if not exists
    admin = User.query.filter_by(username='stefan').first()
    if not admin:
        admin = User(username='stefan', role='ADMIN', is_active=True)
        db.session.add(admin)
        click.echo('  Created user: stefan (ADMIN)')
    else:
        click.echo('  User stefan already exists')
    
    # Create operator user if not exists
    operator = User.query.filter_by(username='operator').first()
    if not operator:
        operator = User(username='operator', role='OPERATOR', is_active=True)
        db.session.add(operator)
        click.echo('  Created user: operator (OPERATOR)')
    else:
        click.echo('  User operator already exists')
    
    # Demo data (optional)
    if demo:
        click.echo('  Adding demo data...')
        
        # Demo article 1 - Mankiewicz paint
        art1 = Article.query.filter_by(article_no='MNK-WHITE-5L').first()
        if not art1:
            art1 = Article(
                article_no='MNK-WHITE-5L',
                description='Mankiewicz White Paint 5L',
                is_paint=True
            )
            db.session.add(art1)
            db.session.flush()
            click.echo('  Created article: MNK-WHITE-5L')
        
        # Demo article 2 - Akzo paint
        art2 = Article.query.filter_by(article_no='AKZO-BLUE-10L').first()
        if not art2:
            art2 = Article(
                article_no='AKZO-BLUE-10L',
                description='Akzo Nobel Blue Paint 10L',
                is_paint=True
            )
            db.session.add(art2)
            db.session.flush()
            click.echo('  Created article: AKZO-BLUE-10L')
        
        # Demo batch 1 - Mankiewicz format (4 digits)
        batch1 = Batch.query.filter_by(
            article_id=art1.id,
            batch_code='0044'
        ).first()
        if not batch1:
            batch1 = Batch(article_id=art1.id, batch_code='0044')
            db.session.add(batch1)
            db.session.flush()
            click.echo('  Created batch: 0044 (Mankiewicz format)')
        
        # Demo batch 2 - Akzo format (9-10 digits)
        batch2 = Batch.query.filter_by(
            article_id=art2.id,
            batch_code='292456953'
        ).first()
        if not batch2:
            batch2 = Batch(article_id=art2.id, batch_code='292456953')
            db.session.add(batch2)
            db.session.flush()
            click.echo('  Created batch: 292456953 (Akzo format)')
        
        # Demo stock for batch 1
        stock1 = Stock.query.filter_by(
            location_id=location.id,
            article_id=art1.id,
            batch_id=batch1.id
        ).first()
        if not stock1:
            stock1 = Stock(
                location_id=location.id,
                article_id=art1.id,
                batch_id=batch1.id,
                quantity_kg=Decimal('25.00')
            )
            db.session.add(stock1)
            click.echo('  Created stock: 25.00kg for MNK-WHITE-5L batch 0044')
        
        # Demo surplus for batch 1
        surplus1 = Surplus.query.filter_by(
            location_id=location.id,
            article_id=art1.id,
            batch_id=batch1.id
        ).first()
        if not surplus1:
            surplus1 = Surplus(
                location_id=location.id,
                article_id=art1.id,
                batch_id=batch1.id,
                quantity_kg=Decimal('3.50'),
                reason='Initial surplus from previous batch'
            )
            db.session.add(surplus1)
            click.echo('  Created surplus: 3.50kg for MNK-WHITE-5L batch 0044')
        
        # Demo stock for batch 2
        stock2 = Stock.query.filter_by(
            location_id=location.id,
            article_id=art2.id,
            batch_id=batch2.id
        ).first()
        if not stock2:
            stock2 = Stock(
                location_id=location.id,
                article_id=art2.id,
                batch_id=batch2.id,
                quantity_kg=Decimal('50.00')
            )
            db.session.add(stock2)
            click.echo('  Created stock: 50.00kg for AKZO-BLUE-10L batch 292456953')
    
    db.session.commit()
    click.echo('Seed completed!')


def register_cli(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(seed_command)
