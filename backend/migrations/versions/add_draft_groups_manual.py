"""Add draft groups and link to weigh_in_drafts.

Revision ID: draft_groups_v1
Revises: (existing head)
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone
import logging

# revision identifiers, used by Alembic.
revision = 'add_draft_groups'
down_revision = 'a3f5e8b2c1d4'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create draft_groups table
    op.create_table('draft_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, server_default='DRAFT'),
        sa.Column('source', sa.Text(), nullable=False, server_default='ui_operator'),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_draft_groups_status_created_at', 'draft_groups', ['status', 'created_at'], unique=False)
    op.create_index('idx_draft_groups_source_created_at', 'draft_groups', ['source', 'created_at'], unique=False)

    # 2. Add draft_group_id to weigh_in_drafts (start as nullable)
    op.add_column('weigh_in_drafts', sa.Column('draft_group_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_draft_group', 'weigh_in_drafts', 'draft_groups', ['draft_group_id'], ['id'], ondelete='RESTRICT')
    op.create_index('idx_weigh_in_drafts_group_id', 'weigh_in_drafts', ['draft_group_id'], unique=False)

    # 3. Data Migration: Backfill existing drafts into groups
    # We use raw connection for efficiency or just execute SQL
    connection = op.get_bind()
    
    # Get all drafts that don't have a group
    drafts = connection.execute(
        sa.text("SELECT id, location_id, created_by_user_id, created_at FROM weigh_in_drafts WHERE draft_group_id IS NULL")
    ).fetchall()
    
    if drafts:
        print(f"Backfilling {len(drafts)} drafts into groups...")
        for draft in drafts:
            # Create a group for this draft
            # Name format: AutoSingleDraft_YYYYMMDD_HHMMSS
            dt = draft.created_at
            name = f"AutoSingleDraft_{dt.strftime('%Y%m%d_%H%M%S')}"
            
            res = connection.execute(
                sa.text("""
                    INSERT INTO draft_groups (name, status, source, location_id, created_by_user_id, created_at)
                    VALUES (:name, 'DRAFT', 'ui_operator', :loc_id, :user_id, :created_at)
                    RETURNING id
                """),
                {"name": name, "loc_id": draft.location_id, "user_id": draft.created_by_user_id, "created_at": dt}
            )
            group_id = res.fetchone()[0]
            
            # Link draft to group
            connection.execute(
                sa.text("UPDATE weigh_in_drafts SET draft_group_id = :group_id WHERE id = :draft_id"),
                {"group_id": group_id, "draft_id": draft.id}
            )

    # 4. Final step: Make column NOT NULL
    op.alter_column('weigh_in_drafts', 'draft_group_id', existing_type=sa.Integer(), nullable=False)

def downgrade():
    op.drop_constraint('fk_draft_group', 'weigh_in_drafts', type_='foreignkey')
    op.drop_index('idx_weigh_in_drafts_group_id', table_name='weigh_in_drafts')
    op.drop_column('weigh_in_drafts', 'draft_group_id')
    op.drop_index('idx_draft_groups_source_created_at', table_name='draft_groups')
    op.drop_index('idx_draft_groups_status_created_at', table_name='draft_groups')
    op.drop_table('draft_groups')
