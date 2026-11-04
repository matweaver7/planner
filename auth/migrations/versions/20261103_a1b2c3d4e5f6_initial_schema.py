"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-11-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            username      VARCHAR(64)  UNIQUE NOT NULL,
            email         VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT         NOT NULL,
            created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
            updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS token_blocklist (
            token_jti  VARCHAR(36)  PRIMARY KEY,
            blocked_at TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS token_blocklist")
    op.execute("DROP TABLE IF EXISTS users")
