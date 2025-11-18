"""add_payments_table

Revision ID: 94aeab046aa4
Revises: 0133f2a10451
Create Date: 2025-11-18 22:33:18.443028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '94aeab046aa4'
down_revision: Union[str, None] = '0133f2a10451'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", name="payment_status"), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_foreign_key(
        "fk_payments_idempotency_key",
        "payments",
        "idempotency_keys",
        ["idempotency_key"],
        ["key"],
    )


def downgrade() -> None:
    op.drop_table("payments")

