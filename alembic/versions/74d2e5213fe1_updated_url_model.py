"""Updated URL Model

Revision ID: 74d2e5213fe1
Revises: a8a69ee43263
Create Date: 2025-04-04 17:56:01.953081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74d2e5213fe1'
down_revision: Union[str, None] = 'a8a69ee43263'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('urls', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('urls', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
    op.drop_constraint('urls_short_url_key', 'urls', type_='unique')
    op.create_index(op.f('ix_urls_short_url'), 'urls', ['short_url'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_urls_short_url'), table_name='urls')
    op.create_unique_constraint('urls_short_url_key', 'urls', ['short_url'])
    op.drop_column('urls', 'expires_at')
    op.drop_column('urls', 'created_at')
    # ### end Alembic commands ###
