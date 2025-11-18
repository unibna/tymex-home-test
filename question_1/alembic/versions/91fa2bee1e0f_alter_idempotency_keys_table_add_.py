"""alter_idempotency_keys_table_add_payment_constraint

Revision ID: 91fa2bee1e0f
Revises: 94aeab046aa4
Create Date: 2025-11-18 22:37:07.512739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '91fa2bee1e0f'
down_revision: Union[str, None] = '94aeab046aa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("idempotency_keys", sa.Column("payment_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_idempotency_keys_payment_id",
        "idempotency_keys",
        "payments",
        ["payment_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_idempotency_keys_payment_id", "idempotency_keys", type_="foreignkey")
    op.drop_column("idempotency_keys", "payment_id")


