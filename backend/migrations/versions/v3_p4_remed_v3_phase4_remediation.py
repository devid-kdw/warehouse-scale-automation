"""v3_phase4_remediation

Revision ID: v3_p4_remed
Revises: ad7df8209648
Create Date: 2026-02-17 14:23:47.128767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v3_p4_remed'
down_revision = 'ad7df8209648'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add density to articles (default 1.0)
    op.add_column('articles', sa.Column('density', sa.Numeric(10, 4), nullable=False, server_default='1.0'))
    
    # 2. Backfill Transactions: assumption is that historical transactions were KG-based
    # We update rows where quantity is NULL
    op.execute("UPDATE transactions SET quantity = quantity_kg, uom = 'KG' WHERE quantity IS NULL")
    
    # 3. Enforce NOT NULL on Transactions
    op.alter_column('transactions', 'quantity', existing_type=sa.Numeric(14, 3), nullable=False)
    op.alter_column('transactions', 'uom', existing_type=sa.String(20), nullable=False)


def downgrade():
    op.alter_column('transactions', 'uom', existing_type=sa.String(20), nullable=True)
    op.alter_column('transactions', 'quantity', existing_type=sa.Numeric(14, 3), nullable=True)
    op.drop_column('articles', 'density')
