"""add linkedin_posts table

Revision ID: a0a249e1c96c
Revises: 0e9032d05637
Create Date: 2026-01-28 11:11:35.380315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0a249e1c96c'
down_revision: Union[str, Sequence[str], None] = '0e9032d05637'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'linkedin_posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('brand_id', sa.Integer(), sa.ForeignKey('brand_profiles.id'), nullable=False),

        sa.Column('linkedin_post_urn', sa.String(length=255), nullable=False, unique=True),
        sa.Column('text', sa.Text(), nullable=False),

        sa.Column('status', sa.String(length=50), nullable=False, server_default='published'),
        sa.Column('error_message', sa.Text(), nullable=True),

        sa.Column(
            'published_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )



def downgrade() -> None:
    op.drop_table('linkedin_posts')
