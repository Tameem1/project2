"""Add input_tokens_used and output_tokens

Revision ID: f35803229a70
Revises: ca92b287d82f
Create Date: 2025-02-06 20:48:02.928086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f35803229a70'
down_revision: Union[str, None] = 'ca92b287d82f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usage_tokens', sa.Column('input_tokens_used', sa.Integer(), server_default='0', nullable=False))
    op.add_column('usage_tokens', sa.Column('output_tokens_used', sa.Integer(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('usage_tokens', 'output_tokens_used')
    op.drop_column('usage_tokens', 'input_tokens_used')
    # ### end Alembic commands ###
