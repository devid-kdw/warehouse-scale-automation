"""Add article expansion, aliases, draft_type.

Revision ID: a3f5e8b2c1d4
Revises: f11e5d13d9f6
Create Date: 2026-02-03 11:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f5e8b2c1d4'
down_revision = 'f11e5d13d9f6'
branch_labels = None
depends_on = None


def upgrade():
    # === ARTICLES TABLE: Add new columns ===
    op.add_column('articles', sa.Column('uom', sa.String(10), nullable=True))
    op.add_column('articles', sa.Column('manufacturer', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('manufacturer_art_number', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('reorder_threshold', sa.Numeric(14, 2), nullable=True))
    
    # === ARTICLE_ALIASES TABLE: Create new table ===
    op.create_table(
        'article_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alias', name='uq_article_alias_global')
    )
    op.create_index('ix_article_aliases_article_id', 'article_aliases', ['article_id'])
    
    # === WEIGH_IN_DRAFTS TABLE: Add draft_type column ===
    op.add_column(
        'weigh_in_drafts',
        sa.Column('draft_type', sa.String(20), nullable=False, server_default='WEIGH_IN')
    )


def downgrade():
    # Remove draft_type column
    op.drop_column('weigh_in_drafts', 'draft_type')
    
    # Drop article_aliases table
    op.drop_index('ix_article_aliases_article_id', table_name='article_aliases')
    op.drop_table('article_aliases')
    
    # Remove article expansion columns
    op.drop_column('articles', 'reorder_threshold')
    op.drop_column('articles', 'manufacturer_art_number')
    op.drop_column('articles', 'manufacturer')
    op.drop_column('articles', 'uom')
