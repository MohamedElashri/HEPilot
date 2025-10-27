"""CLI entrypoint for running the ArXiv collector via the generic pipeline."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from src.collector import CollectorPipeline, CollectorRequest
from src.collector.validation import CollectorSchemaValidator, CollectorValidationError

from .config import ConfigManager
from .discovery import ArxivDiscovery

app = typer.Typer(add_completion=False)


def _build_discovery_payload(discovery_results) -> Dict[str, Any]:
    """Build discovery output payload for validation."""
    return {
        "discovered_documents": [
            {
                "document_id": str(doc.document_id),
                "source_type": "arxiv",
                "source_url": doc.source_url,
                "title": doc.title,
                "authors": doc.authors if doc.authors else None,
                "discovery_timestamp": doc.discovery_timestamp.isoformat(),
                "estimated_size": doc.estimated_size,
                "content_type": "application/pdf",
            }
            for doc in discovery_results
        ]
    }


def _build_requests(discovery_results) -> List[CollectorRequest]:
    requests: List[CollectorRequest] = []
    for doc in discovery_results:
        metadata = {
            "document_id": str(doc.document_id),
            "source_id": doc.arxiv_id or str(doc.document_id),
            "source_url": doc.source_url,
            "title": doc.title,
            "authors": doc.authors,
            "arxiv_id": doc.arxiv_id,
            "arxiv_version": doc.arxiv_version,
            "discovered_at": doc.discovery_timestamp.isoformat(),
        }
        requests.append(
            CollectorRequest(
                url=doc.source_url,
                source_id=doc.arxiv_id or str(doc.document_id),
                metadata=metadata,
            )
        )
    return requests


@app.command()
def collect(  # noqa: PLR0913 - command interface
    config: Path = typer.Option(
        Path("src/collector/adapters/arxiv/adapter_config.json"),
        "--config",
        help="Path to adapter configuration file.",
    ),
    query: str = typer.Option(
        "all:lhcb",
        "--query",
        help="ArXiv query string (defaults to LHCb papers).",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        help="Optional limit on number of documents to ingest.",
    ),
    persist: bool = typer.Option(
        False,
        "--persist/--no-persist",
        help="Persist collector artefacts to disk (defaults to off).",
    ),
    output_dir: Path = typer.Option(  # noqa: B008 - Typer handles default Path
        Path(".data/collector/arxiv"),
        "--output-dir",
        help="Directory used when persistence is enabled.",
    ),
    use_docstore: bool = typer.Option(
        False,
        "--docstore/--no-docstore",
        help="Store chunks in the registered docstore (in-memory by default).",
    ),
) -> None:
    """Run the ArXiv collector using the shared pipeline."""

    config_manager = ConfigManager(config)

    discovery = ArxivDiscovery(
        max_results=limit,
        include_authors=config_manager.get_include_authors_metadata(),
    )
    docs = discovery.search(query)

    if not docs:
        typer.echo("🚫 No documents discovered for the provided query.")
        raise typer.Exit(code=1)

    typer.echo(f"🔍 Discovered {len(docs)} documents")

    # Validate discovery output against schema
    validator = CollectorSchemaValidator()
    discovery_payload = _build_discovery_payload(docs)
    try:
        validator.validate_discovery_output(discovery_payload)
        typer.echo("✓ Discovery output validated against schema")
    except CollectorValidationError as exc:
        typer.echo(f"⚠️  Discovery validation warning: {exc}", err=True)

    requests = _build_requests(docs)

    component_config = {
        "cleaner": {
            "processing_config": config_manager.config.processing,
        },
        "chunker": {
            "chunk_size": config_manager.get_chunk_size(),
            "chunk_overlap": config_manager.get_chunk_overlap(),
            "model_name": config_manager.get_embedding_model_name(),
            "use_model_tokenizer": config_manager.get_use_model_tokenizer(),
            "cache_dir": config_manager.get_model_cache_dir(),
        },
    }

    adapter_metadata = {
        "adapter_name": config_manager.config.name,
        "adapter_version": config_manager.config.version,
        "source_type": config_manager.config.source_type,
    }

    pipeline = CollectorPipeline(
        scraper="arxiv_pdf",
        cleaner="arxiv_docling",
        chunker="arxiv_chunker",
        docstore="arxiv_docstore" if use_docstore else None,
        component_config=component_config,
        persist_output=persist,
        output_dir=output_dir,
        adapter_metadata=adapter_metadata,
    )

    typer.echo("🚀 Starting collection pipeline")
    start_time = datetime.now()
    result = asyncio.run(pipeline.collect(requests))
    duration = datetime.now() - start_time

    typer.echo("✨ Collection complete")
    typer.echo(f"   Documents processed: {len(result.documents)}")
    typer.echo(f"   Errors: {len(result.errors)}")
    typer.echo(f"   Duration: {duration.total_seconds():.1f}s")

    if result.catalog:
        catalog_doc_count = result.catalog.get("total_documents", 0)
        catalog_chunk_count = result.catalog.get("total_chunks", 0)
        typer.echo(
            f"   Catalog summary: {catalog_doc_count} docs / {catalog_chunk_count} chunks"
        )
        if persist:
            catalog_path = output_dir / "catalog.json"
            typer.echo(f"   Catalog written to: {catalog_path}")

    if result.errors:
        typer.echo("⚠️  Errors encountered:")
        for error in result.errors[:5]:
            typer.echo(f"   • {error.url}: {error.message}")


def main() -> None:
    """Entry point used by legacy scripts."""

    app()


if __name__ == "__main__":  # pragma: no cover
    main()
