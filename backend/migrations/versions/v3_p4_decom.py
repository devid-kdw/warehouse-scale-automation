"""v3_phase4_decommission

Revision ID: v3_p4_decom
Revises: v3_p4_remed
Create Date: 2026-02-17 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v3_p4_decom'
down_revision = 'v3_p4_remed'
branch_labels = None
depends_on = None


def upgrade():
    # Drop legacy quantity_kg columns
    op.drop_column('transactions', 'quantity_kg')
    op.drop_column('stock', 'quantity_kg')
    op.drop_column('surplus', 'quantity_kg')
    op.drop_column('weigh_in_drafts', 'quantity_kg')


def downgrade():
    # Re-add legacy columns (nullable)
    op.add_column('transactions', sa.Column('quantity_kg', sa.Numeric(10, 2), nullable=True))
    op.add_column('stock', sa.Column('quantity_kg', sa.Numeric(10, 2), nullable=True))
    op.add_column('surplus', sa.Column('quantity_kg', sa.Numeric(10, 2), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('quantity_kg', sa.Numeric(10, 2), nullable=True))
