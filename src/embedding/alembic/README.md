# Database Migrations

This directory contains Alembic database migrations for the HEPilot embedding layer.

## Schema Overview

The embedding layer uses two main tables:

### `documents` Table
Stores document metadata for papers and other sources.

**Columns:**
- `id` (UUID, PK) - Unique document identifier
- `source_type` (VARCHAR(50)) - Source type (e.g., "arxiv", "pubmed")
- `source_id` (VARCHAR(500)) - External identifier (e.g., arXiv ID)
- `title` (TEXT) - Document title
- `authors` (JSONB) - List of authors
- `publication_date` (TIMESTAMP) - Publication date
- `source_url` (TEXT) - URL to source
- `meta` (JSONB) - Additional metadata
- `created_at` (TIMESTAMPTZ) - Record creation time

**Constraints:**
- Unique constraint on (`source_type`, `source_id`)

**Indexes:**
- `idx_documents_source` on (`source_type`, `source_id`)

### `doc_segments` Table
Stores text chunks/segments from documents.

**Columns:**
- `id` (UUID, PK) - Unique segment identifier
- `doc_id` (UUID, FK) - Reference to `documents.id`
- `text` (TEXT) - The actual text content
- `section_path` (JSONB) - Section hierarchy (e.g., ["introduction", "background"])
- `position_in_doc` (INTEGER) - Sequential position in document
- `token_count` (INTEGER) - Number of tokens in chunk
- `overlap_start` (INTEGER) - Number of overlapping tokens at start
- `overlap_end` (INTEGER) - Number of overlapping tokens at end
- `meta` (JSONB) - Additional metadata
- `created_at` (TIMESTAMPTZ) - Record creation time

**Constraints:**
- Foreign key to `documents.id` with CASCADE delete

**Indexes:**
- `idx_segments_doc_id` on (`doc_id`)
- `idx_segments_position` on (`doc_id`, `position_in_doc`)

## Running Migrations

### Prerequisites

1. **PostgreSQL database running:**
   ```bash
   # Check if PostgreSQL is running
   psql -h localhost -U hep -d hepilot -c "SELECT version();"
   ```

2. **Database configured in `config/embedding.toml`:**
   ```toml
   [docstore]
   database_url = "postgresql+asyncpg://hep:hep@localhost/hepilot"
   ```

### Apply Migrations

```bash
# From project root
cd /data/home/melashri/LLM/HEPilot

# Upgrade to latest
alembic upgrade head

# Check current version
alembic current

# Show migration history
alembic history --verbose
```

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to base (empty database)
alembic downgrade base

# Downgrade to specific revision
alembic downgrade 67906781f81e
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

## Testing Migrations

### Test Migration Syntax (without database)

```bash
# Run migration validation test
PYTHONPATH=/data/home/melashri/LLM/HEPilot python tests/unit/embedding/test_migration.py
```

This validates:
- Migration file syntax is correct
- upgrade() and downgrade() functions exist
- Database models can be imported
- Table metadata is correct

### Test Against Database

When PostgreSQL is available:

```bash
# Create test database
createdb -h localhost -U hep hepilot_test

# Run migration
HEPILOT_DB_URL="postgresql+asyncpg://hep:hep@localhost/hepilot_test" alembic upgrade head

# Verify tables
psql -h localhost -U hep hepilot_test -c "\dt"

# Test rollback
alembic downgrade base

# Clean up
dropdb -h localhost -U hep hepilot_test
```

## Migration Files

Current migrations:
- `67906781f81e` - Initial schema for embedding layer (documents + doc_segments tables)

## Troubleshooting

### Database connection errors
- Verify PostgreSQL is running: `systemctl status postgresql`
- Check connection details in `config/embedding.toml`
- Test connection: `psql -h localhost -U hep hepilot`

### Import errors
- Ensure virtual environment is activated
- Install dependencies: `pip install alembic sqlalchemy asyncpg`
- Set PYTHONPATH: `export PYTHONPATH=/data/home/melashri/LLM/HEPilot`

### Migration conflicts
- Check current version: `alembic current`
- View history: `alembic history`
- Stamp database if needed: `alembic stamp head`

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Project embedding config: `src/embedding/config.py`
- Database models: `src/embedding/adapters/db_models.py`
