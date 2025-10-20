"""Initial schema for embedding layer

Revision ID: 67906781f81e
Revises: 
Create Date: 2025-10-20 12:04:16.812341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '67906781f81e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', sa.String(500), nullable=False),
        sa.Column('title', sa.Text),
        sa.Column('authors', postgresql.JSONB),
        sa.Column('publication_date', sa.TIMESTAMP),
        sa.Column('source_url', sa.Text),
        sa.Column('meta', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    )
    
    # Create doc_segments table
    op.create_table(
        'doc_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('section_path', postgresql.JSONB),
        sa.Column('position_in_doc', sa.Integer, nullable=False),
        sa.Column('token_count', sa.Integer, nullable=False),
        sa.Column('overlap_start', sa.Integer, nullable=False),
        sa.Column('overlap_end', sa.Integer, nullable=False),
        sa.Column('meta', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['doc_id'], ['documents.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_segments_doc_id', 'doc_segments', ['doc_id'])
    op.create_index('idx_segments_position', 'doc_segments', ['doc_id', 'position_in_doc'])
    op.create_index('idx_documents_source', 'documents', ['source_type', 'source_id'])
    
    # Create unique constraint
    op.create_unique_constraint('uq_documents_source', 'documents', ['source_type', 'source_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order (child table first)
    op.drop_table('doc_segments')
    op.drop_table('documents')
