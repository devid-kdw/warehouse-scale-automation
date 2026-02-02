"""CLI seed command."""
import click
from flask.cli import with_appcontext

from ..extensions import db
from ..models import User, Location


@click.command('seed')
@with_appcontext
def seed_command():
    """Seed initial data: location "13" and admin user "stefan"."""
    
    click.echo('Seeding database...')
    
    # Create location "13" if not exists
    location = Location.query.filter_by(code='13').first()
    if not location:
        location = Location(code='13', name='Main Warehouse')
        db.session.add(location)
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
    
    db.session.commit()
    click.echo('Seed completed!')


def register_cli(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(seed_command)
