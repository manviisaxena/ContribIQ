"""create issues table

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("repo_full_name", sa.String(511), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("url", sa.String(1024), nullable=True),
        sa.Column("labels", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("files_affected", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("difficulty", sa.Float(), nullable=False),
        sa.Column("difficulty_factors", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("estimated_hours", sa.Float(), nullable=True),
        sa.Column("scored_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("repo_full_name", "number", name="uq_issues_repo_number"),
    )
    op.create_index("ix_issues_repo_full_name", "issues", ["repo_full_name"])


def downgrade() -> None:
    op.drop_index("ix_issues_repo_full_name", table_name="issues")
    op.drop_table("issues")
