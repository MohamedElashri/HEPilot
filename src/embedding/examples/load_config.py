"""Example: Loading and using embedding configuration.

This script demonstrates how to load and use the embedding configuration.
"""

from pathlib import Path
from src.embedding import load_config, EmbeddingConfig


def main():
    """Load and display embedding configuration."""
    # Load configuration from default location
    config_path = Path("config/embedding.toml")
    config = load_config(config_path)
    
    print("=" * 60)
    print("HEPilot Embedding Configuration")
    print("=" * 60)
    
    # Display encoder configuration
    print("\n📝 Encoder Configuration:")
    print(f"  Type: {config.encoder.type}")
    print(f"  Model: {config.encoder.model_name}")
    print(f"  Batch Size: {config.encoder.batch_size}")
    print(f"  Device: {config.encoder.device}")
    print(f"  Normalize: {config.encoder.normalize}")
    print(f"  Cache Dir: {config.encoder.cache_dir}")
    
    # Display vector database configuration
    print("\n🗄️  Vector Database Configuration:")
    print(f"  Type: {config.vectordb.type}")
    print(f"  Persist Directory: {config.vectordb.persist_directory}")
    print(f"  Collection Name: {config.vectordb.collection_name}")
    print(f"  Distance Metric: {config.vectordb.distance_metric}")
    
    # Display document store configuration
    print("\n💾 Document Store Configuration:")
    print(f"  Type: {config.docstore.type}")
    print(f"  Database URL: {config.docstore.database_url}")
    print(f"  Pool Size: {config.docstore.pool_size}")
    print(f"  Max Overflow: {config.docstore.max_overflow}")
    
    # Display pipeline configuration
    print("\n⚙️  Pipeline Configuration:")
    print(f"  Batch Size: {config.pipeline.batch_size}")
    print(f"  Max Workers: {config.pipeline.max_workers}")
    print(f"  Checkpoint Interval: {config.pipeline.checkpoint_interval}")
    
    print("\n" + "=" * 60)
    print("✅ Configuration loaded successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
