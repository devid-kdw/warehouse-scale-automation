"""v3_phase1_foundation -- Article extensions, UOM catalog, unit-aware columns, hardware fields

Revision ID: v3_phase1_foundation
Revises: c8f64cf6440c
Create Date: 2026-02-17

Phase 1 foundation migration for v3.0:
  - Article: has_batch, supplier_code, category
  - UOM catalog table with seed data
  - Unit-aware transition columns (quantity, uom) on stock, surplus, transactions, weigh_in_drafts
  - Hardware source identity fields on weigh_in_drafts
  - Transaction receiving linkage columns (delivery_note_number, order_line_id)
  - Backfill: has_batch from is_paint, category defaults, quantity/uom from legacy
"""
from alembic import op
import sqlalchemy as sa


revision = 'v3_phase1_foundation'
down_revision = 'c8f64cf6440c'
branch_labels = None
depends_on = None


def upgrade():
    # 1) UOM catalog table
    op.create_table(
        'uom_catalog',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(20), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 2) Article new columns
    op.add_column('articles', sa.Column('has_batch', sa.Boolean, nullable=True))
    op.add_column('articles', sa.Column('supplier_code', sa.String(50), nullable=True))
    op.add_column('articles', sa.Column('category', sa.String(50), nullable=True))

    # Backfill has_batch = is_paint
    op.execute("UPDATE articles SET has_batch = is_paint")
    # Make NOT NULL after backfill
    op.alter_column('articles', 'has_batch', nullable=False, server_default=sa.text('true'))

    # Backfill category: paint -> raw_material, others -> operational_supplies
    op.execute("""
        UPDATE articles SET category = CASE
            WHEN is_paint = true THEN 'raw_material'
            ELSE 'operational_supplies'
        END
    """)

    # 3) Unit-aware transition columns on stock
    op.add_column('stock', sa.Column('quantity', sa.Numeric(14, 3), nullable=True))
    op.add_column('stock', sa.Column('uom', sa.String(20), nullable=True))

    # 4) Unit-aware transition columns on surplus
    op.add_column('surplus', sa.Column('quantity', sa.Numeric(14, 3), nullable=True))
    op.add_column('surplus', sa.Column('uom', sa.String(20), nullable=True))

    # 5) Unit-aware transition columns + receiving linkage on transactions
    op.add_column('transactions', sa.Column('quantity', sa.Numeric(14, 3), nullable=True))
    op.add_column('transactions', sa.Column('uom', sa.String(20), nullable=True))
    op.add_column('transactions', sa.Column('delivery_note_number', sa.String(100), nullable=True))
    op.add_column('transactions', sa.Column('order_line_id', sa.Integer, nullable=True))

    # 6) Unit-aware transition + hardware identity columns on weigh_in_drafts
    op.add_column('weigh_in_drafts', sa.Column('quantity', sa.Numeric(14, 3), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('uom', sa.String(20), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('scale_id', sa.String(50), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('scanner_id', sa.String(50), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('station_id', sa.String(50), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('source_label', sa.String(100), nullable=True))
    op.add_column('weigh_in_drafts', sa.Column('source_meta', sa.JSON, nullable=True))

    # 7) Backfill unit-aware columns from legacy quantity_kg + article UOM
    # Use COALESCE to handle historically nullable uom: articles.uom > UPPER(articles.base_uom) > 'KG'
    op.execute("""
        UPDATE stock SET
            quantity = quantity_kg,
            uom = COALESCE(
                (SELECT a.uom FROM articles a WHERE a.id = stock.article_id),
                (SELECT UPPER(a.base_uom) FROM articles a WHERE a.id = stock.article_id),
                'KG'
            )
    """)
    op.execute("""
        UPDATE surplus SET
            quantity = quantity_kg,
            uom = COALESCE(
                (SELECT a.uom FROM articles a WHERE a.id = surplus.article_id),
                (SELECT UPPER(a.base_uom) FROM articles a WHERE a.id = surplus.article_id),
                'KG'
            )
    """)
    op.execute("""
        UPDATE transactions SET
            quantity = quantity_kg,
            uom = COALESCE(
                (SELECT a.uom FROM articles a WHERE a.id = transactions.article_id),
                (SELECT UPPER(a.base_uom) FROM articles a WHERE a.id = transactions.article_id),
                'KG'
            )
    """)
    op.execute("""
        UPDATE weigh_in_drafts SET
            quantity = quantity_kg,
            uom = COALESCE(
                (SELECT a.uom FROM articles a WHERE a.id = weigh_in_drafts.article_id),
                (SELECT UPPER(a.base_uom) FROM articles a WHERE a.id = weigh_in_drafts.article_id),
                'KG'
            )
    """)

    # 8) Seed UOM catalog: base seeds + existing distinct UOMs
    op.execute("INSERT INTO uom_catalog (code) VALUES ('KG') ON CONFLICT (code) DO NOTHING")
    op.execute("INSERT INTO uom_catalog (code) VALUES ('L') ON CONFLICT (code) DO NOTHING")
    op.execute("INSERT INTO uom_catalog (code) VALUES ('KOM') ON CONFLICT (code) DO NOTHING")
    op.execute("INSERT INTO uom_catalog (code) VALUES ('PAK') ON CONFLICT (code) DO NOTHING")
    # Ingest any distinct UOMs already in articles
    op.execute("""
        INSERT INTO uom_catalog (code)
        SELECT DISTINCT UPPER(COALESCE(uom, base_uom))
        FROM articles
        WHERE UPPER(COALESCE(uom, base_uom)) IS NOT NULL
        ON CONFLICT (code) DO NOTHING
    """)

    # 9) Indexes for new columns
    op.create_index('ix_transactions_delivery_note', 'transactions', ['delivery_note_number'])
    op.create_index('ix_transactions_order_line_id', 'transactions', ['order_line_id'])


def downgrade():
    op.drop_index('ix_transactions_order_line_id', table_name='transactions')
    op.drop_index('ix_transactions_delivery_note', table_name='transactions')

    op.drop_column('weigh_in_drafts', 'source_meta')
    op.drop_column('weigh_in_drafts', 'source_label')
    op.drop_column('weigh_in_drafts', 'station_id')
    op.drop_column('weigh_in_drafts', 'scanner_id')
    op.drop_column('weigh_in_drafts', 'scale_id')
    op.drop_column('weigh_in_drafts', 'uom')
    op.drop_column('weigh_in_drafts', 'quantity')

    op.drop_column('transactions', 'order_line_id')
    op.drop_column('transactions', 'delivery_note_number')
    op.drop_column('transactions', 'uom')
    op.drop_column('transactions', 'quantity')

    op.drop_column('surplus', 'uom')
    op.drop_column('surplus', 'quantity')

    op.drop_column('stock', 'uom')
    op.drop_column('stock', 'quantity')

    op.drop_column('articles', 'category')
    op.drop_column('articles', 'supplier_code')
    op.drop_column('articles', 'has_batch')

    op.drop_table('uom_catalog')
