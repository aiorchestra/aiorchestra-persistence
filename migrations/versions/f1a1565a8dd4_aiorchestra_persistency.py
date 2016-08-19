"""AIOrchestra persistence

Revision ID: f1a1565a8dd4
Revises: 
Create Date: 2016-08-19 11:04:20.567324

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = 'f1a1565a8dd4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        'context',
        sa.Column('name', sa.String(), nullable=False, unique=True, primary_key=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('template_path', sa.String(), nullable=False),
        sa.Column('inputs', sa.Text(), nullable=False),
    )
    op.create_table(
        'node',
        sa.Column('context', sa.String(), sa.ForeignKey('context.name'), ),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('is_provisioned', sa.Boolean(), nullable=False),
        sa.Column('properties', sa.Text(), nullable=True),
        sa.Column('attributes', sa.Text(), nullable=True),
        sa.Column('runtime_properties', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table('node')
    op.drop_table('context')
