"""Remove unique constraint from Customer.name

Revision ID: 803462df93e2
Revises: db97c41b26e8
Create Date: 2025-02-19 12:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "803462df93e2"
down_revision = "db97c41b26e8"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop the unique constraint named "customers_name_key" or similar 
    # Check how it was named in your DB (often "customers_name_key" or 
    # a random auto-generated name).
    op.drop_constraint('customers_name_key', 'customers', type_='unique')
    # If needed, also alter the column to be just a normal string
    # op.alter_column('customers', 'name', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    # Recreate the unique constraint if you ever need to revert
    op.create_unique_constraint('customers_name_key', 'customers', ['name'])