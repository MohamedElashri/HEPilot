"""Test database migration script syntax."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_migration_syntax():
    """Test that migration file can be imported without errors."""
    try:
        # Import alembic
        from alembic import op
        import sqlalchemy as sa
        from sqlalchemy.dialects import postgresql
        
        print("✓ Alembic imports successful")
        
        # Load migration file
        # Go up from tests/unit/embedding to project root, then into src/embedding/alembic
        project_root = Path(__file__).parent.parent.parent.parent
        migration_dir = project_root / "src" / "embedding" / "alembic" / "versions"
        migration_files = list(migration_dir.glob("*initial_schema*.py"))
        
        if not migration_files:
            print(f"✗ Migration file not found in {migration_dir}")
            print(f"  Available files: {list(migration_dir.glob('*.py'))}")
            return False
        
        migration_file = migration_files[0]
        print(f"✓ Found migration file: {migration_file.name}")
        
        # Try to load it as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration", migration_file)
        if spec and spec.loader:
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            print("✓ Migration file syntax is valid")
            
            # Check functions exist
            if hasattr(migration, 'upgrade') and hasattr(migration, 'downgrade'):
                print("✓ upgrade() and downgrade() functions exist")
            else:
                print("✗ Missing upgrade() or downgrade() functions")
                return False
                
            # Check metadata
            print(f"  Revision: {migration.revision}")
            print(f"  Down revision: {migration.down_revision}")
            
            return True
        else:
            print("✗ Failed to load migration module")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_db_models():
    """Test that database models can be imported."""
    try:
        from src.embedding.adapters.db_models import Base, Document, DocSegment
        print("\n✓ Database models imported successfully")
        print(f"  Tables: {', '.join(Base.metadata.tables.keys())}")
        return True
    except Exception as e:
        print(f"\n✗ Failed to import database models: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Database Migration")
    print("=" * 60)
    print()
    
    success = True
    
    print("1. Testing migration syntax...")
    if not test_migration_syntax():
        success = False
    
    print("\n2. Testing database models...")
    if not test_db_models():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nMigration is ready. To apply it when database is available:")
        print("  cd /data/home/melashri/LLM/HEPilot")
        print("  alembic -c src/embedding/alembic.ini upgrade head")
        print("\nTo rollback:")
        print("  alembic -c src/embedding/alembic.ini downgrade -1")
    else:
        print("❌ Some tests failed")
        print("=" * 60)
        sys.exit(1)
