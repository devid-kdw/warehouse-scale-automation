"""v3_phase2_orders -- Orders domain, order_lines, FK on transactions

Revision ID: v3_phase2_orders
Revises: v3_phase1_foundation
Create Date: 2026-02-17

Phase 2: Orders & receiving linkage:
  - orders table (order_number unique)
  - order_lines table
  - FK constraint: transactions.order_line_id -> order_lines.id
"""
from alembic import op
import sqlalchemy as sa


revision = 'v3_phase2_orders'
down_revision = 'v3_phase1_foundation'
branch_labels = None
depends_on = None


def upgrade():
    # 1) orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_number', sa.String(50), unique=True, nullable=False),
        sa.Column('supplier_code', sa.String(50), nullable=True),
        sa.Column('supplier_name', sa.String(200), nullable=True),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='OPEN'),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_status', 'orders', ['status'])

    # 2) order_lines table
    op.create_table(
        'order_lines',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('article_id', sa.Integer, sa.ForeignKey('articles.id'), nullable=False),
        sa.Column('ordered_qty', sa.Numeric(14, 3), nullable=False),
        sa.Column('received_qty', sa.Numeric(14, 3), nullable=False,
                  server_default=sa.text('0')),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('delivery_date', sa.Date, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='OPEN'),
        sa.Column('note', sa.Text, nullable=True),
    )
    op.create_index('ix_order_lines_order_id', 'order_lines', ['order_id'])
    op.create_index('ix_order_lines_article_id', 'order_lines', ['article_id'])

    # 3) FK constraint on transactions.order_line_id (column exists from Phase 1)
    op.create_foreign_key(
        'fk_transactions_order_line_id',
        'transactions', 'order_lines',
        ['order_line_id'], ['id']
    )


def downgrade():
    op.drop_constraint('fk_transactions_order_line_id', 'transactions', type_='foreignkey')

    op.drop_index('ix_order_lines_article_id', table_name='order_lines')
    op.drop_index('ix_order_lines_order_id', table_name='order_lines')
    op.drop_table('order_lines')

    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_table('orders')
