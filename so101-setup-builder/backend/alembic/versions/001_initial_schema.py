"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )

    # Vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('ships_to_us', sa.Boolean(), nullable=False, default=True),
        sa.Column('ships_to_eu', sa.Boolean(), nullable=False, default=True),
        sa.Column('typical_shipping_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )

    # Components table
    op.create_table(
        'components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('specifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_default_for_so101', sa.Boolean(), nullable=False, default=False),
        sa.Column('quantity_per_arm', sa.Integer(), nullable=False, default=1),
        sa.Column('arm_type', sa.String(length=20), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_components_category_id', 'components', ['category_id'])
    op.create_index('ix_components_is_default', 'components', ['is_default_for_so101'])
    op.create_index(
        'ix_components_search_vector',
        'components',
        ['search_vector'],
        postgresql_using='gin'
    )

    # Component prices table
    op.create_table(
        'component_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('original_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('shipping_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('product_url', sa.String(length=1000), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=True),
        sa.Column('in_stock', sa.Boolean(), nullable=False, default=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=True),
        sa.Column('price_fetched_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['components.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_component_prices_component_vendor',
        'component_prices',
        ['component_id', 'vendor_id']
    )
    op.create_index('ix_component_prices_price', 'component_prices', ['price'])

    # Setups table
    op.create_table(
        'setups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('wizard_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('current_step', sa.Integer(), nullable=False, default=1),
        sa.Column('wizard_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('arm_type', sa.String(length=20), nullable=False, default='single'),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_setups_expires_at', 'setups', ['expires_at'])

    # Setup components table
    op.create_table(
        'setup_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('setup_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('selected_vendor_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['components.id']),
        sa.ForeignKeyConstraint(['selected_vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['setup_id'], ['setups.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_setup_components_setup_id', 'setup_components', ['setup_id'])
    op.create_index('ix_setup_components_component_id', 'setup_components', ['component_id'])

    # Documentation table
    op.create_table(
        'documentation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('slug', sa.String(length=300), nullable=False),
        sa.Column('source_path', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('source_updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(
        'ix_documentation_search_vector',
        'documentation',
        ['search_vector'],
        postgresql_using='gin'
    )
    op.create_index('ix_documentation_category', 'documentation', ['category'])


def downgrade() -> None:
    op.drop_table('documentation')
    op.drop_table('setup_components')
    op.drop_table('setups')
    op.drop_table('component_prices')
    op.drop_table('components')
    op.drop_table('vendors')
    op.drop_table('categories')
