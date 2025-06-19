"""empty message

Revision ID: 06d3f416d4d2
Revises: fe40a427ce23
Create Date: 2025-06-19 11:19:36.623977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06d3f416d4d2'
down_revision: Union[str, Sequence[str], None] = 'fe40a427ce23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
