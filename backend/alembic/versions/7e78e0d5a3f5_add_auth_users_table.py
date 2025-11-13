"""add auth_users table

Revision ID: 7e78e0d5a3f5
Revises: 8675288e9cf7
Create Date: 2025-11-12 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7e78e0d5a3f5"
down_revision: Union[str, Sequence[str], None] = "8675288e9cf7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "auth_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["yolk_staging.users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_yolk_staging_auth_users_user_id"),
        schema="yolk_staging",
    )
    op.create_index(
        "ix_yolk_staging_auth_users_email",
        "auth_users",
        ["email"],
        unique=True,
        schema="yolk_staging",
    )
    op.create_index(
        "ix_yolk_staging_auth_users_id",
        "auth_users",
        ["id"],
        unique=False,
        schema="yolk_staging",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_yolk_staging_auth_users_id",
        table_name="auth_users",
        schema="yolk_staging",
    )
    op.drop_index(
        "ix_yolk_staging_auth_users_email",
        table_name="auth_users",
        schema="yolk_staging",
    )
    op.drop_table("auth_users", schema="yolk_staging")

