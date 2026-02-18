"""v3_phase3_approvals

Revision ID: v3_phase3_approvals
Revises: v3_phase2_orders
Create Date: 2026-02-17 13:08:02.282945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v3_phase3_approvals'
down_revision = 'v3_phase2_orders'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add columns as nullable
    op.add_column('draft_groups', sa.Column('receipt_number', sa.String(length=50), nullable=True))
    op.add_column('draft_groups', sa.Column('description', sa.Text(), nullable=True))
    
    # 2. Backfill existing groups
    connection = op.get_bind()
    # We use raw sql or core for backfill to avoid model dependency
    # First, copy name to description
    connection.execute(sa.text("UPDATE draft_groups SET description = name"))
    
    # Second, sequential backfill for receipt_number
    # Get all IDs ordered by time
    result = connection.execute(sa.text("SELECT id FROM draft_groups ORDER BY created_at ASC, id ASC"))
    rows = result.fetchall()
    
    for i, row in enumerate(rows, start=1):
        receipt_no = f"{i:04d}"
        connection.execute(
            sa.text("UPDATE draft_groups SET receipt_number = :receipt_no WHERE id = :id"),
            {"receipt_no": receipt_no, "id": row[0]}
        )
    
    # 3. Enforcement
    # After backfill, we can add unique constraint and NOT NULL
    op.create_index('ix_draft_groups_receipt_number', 'draft_groups', ['receipt_number'], unique=True)
    # Note: SQLite doesn't support alter_column to NOT NULL directly usually, 
    # but Alembic might handle it or we use batch_alter_table.
    with op.batch_alter_table('draft_groups') as batch_op:
        batch_op.alter_column('receipt_number', existing_type=sa.String(length=50), nullable=False)


def downgrade():
    with op.batch_alter_table('draft_groups') as batch_op:
        batch_op.drop_index('ix_draft_groups_receipt_number')
        batch_op.drop_column('description')
        batch_op.drop_column('receipt_number')
