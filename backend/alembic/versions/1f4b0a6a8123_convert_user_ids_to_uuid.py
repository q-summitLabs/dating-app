"""convert user identifiers to uuid

Revision ID: 1f4b0a6a8123
Revises: 7e78e0d5a3f5
Create Date: 2025-11-14 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1f4b0a6a8123"
down_revision: Union[str, Sequence[str], None] = "7e78e0d5a3f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "yolk_staging"


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))

    # Add UUID columns to users and auth_users tables.
    op.add_column(
        "users",
        sa.Column(
            "id_uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "auth_users",
        sa.Column(
            "id_uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "auth_users",
        sa.Column(
            "user_id_uuid",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema=SCHEMA,
    )

    # Copy relationships to the new UUID columns.
    op.execute(
        sa.text(
            """
            UPDATE yolk_staging.auth_users AS au
            SET user_id_uuid = u.id_uuid
            FROM yolk_staging.users AS u
            WHERE au.user_id = u.id
            """
        )
    )

    # Drop constraints tied to integer identifiers.
    op.drop_constraint(
        "auth_users_user_id_fkey",
        "auth_users",
        type_="foreignkey",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "uq_yolk_staging_auth_users_user_id",
        "auth_users",
        type_="unique",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "auth_users_pkey",
        "auth_users",
        type_="primary",
        schema=SCHEMA,
    )
    op.drop_constraint(
        "users_pkey",
        "users",
        type_="primary",
        schema=SCHEMA,
    )

    # Drop indexes that reference integer identifiers.
    op.drop_index(
        "ix_yolk_staging_users_id",
        table_name="users",
        schema=SCHEMA,
    )
    op.drop_index(
        "ix_yolk_staging_auth_users_id",
        table_name="auth_users",
        schema=SCHEMA,
    )

    # Drop integer columns and rename UUID columns.
    op.drop_column("auth_users", "user_id", schema=SCHEMA)
    op.drop_column("auth_users", "id", schema=SCHEMA)
    op.drop_column("users", "id", schema=SCHEMA)

    op.alter_column(
        "users",
        "id_uuid",
        new_column_name="id",
        schema=SCHEMA,
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column(
        "auth_users",
        "id_uuid",
        new_column_name="id",
        schema=SCHEMA,
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column(
        "auth_users",
        "user_id_uuid",
        new_column_name="user_id",
        schema=SCHEMA,
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    # Recreate constraints and indexes for UUID identifiers.
    op.create_primary_key(
        "users_pkey",
        "users",
        ["id"],
        schema=SCHEMA,
    )
    op.create_primary_key(
        "auth_users_pkey",
        "auth_users",
        ["id"],
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_yolk_staging_auth_users_user_id",
        "auth_users",
        ["user_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_yolk_staging_users_id",
        "users",
        ["id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_index(
        "ix_yolk_staging_auth_users_id",
        "auth_users",
        ["id"],
        unique=False,
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "auth_users_user_id_fkey",
        "auth_users",
        "users",
        ["user_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    raise RuntimeError("Downgrade from UUID identifiers is not supported.")


