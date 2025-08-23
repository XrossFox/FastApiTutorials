"""Modify phone_number column to be required and have a default value

Revision ID: cab35927bf54
Revises: 99832a608605
Create Date: 2025-08-22 22:15:37.112884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cab35927bf54'
down_revision: Union[str, Sequence[str], None] = '99832a608605'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE users SET phone_number = '0'")
    op.alter_column('users', 'phone_number', nullable=False, server_default='0')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'phone_number', nullable=True, server_default=None)
