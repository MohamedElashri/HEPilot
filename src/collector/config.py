"""Adapter configuration loader aligned with project standards.

This module loads adapter configuration files, validates them against the
machine-readable specification, and exposes typed dataclasses for use across
collector adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import json

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path("standards/schemas/adapter_config.schema.json")


@dataclass(slots=True)
class ProcessingConfig:
    """Core processing parameters enforced by the standard."""

    chunk_size: int
    chunk_overlap: float
    preserve_tables: bool
    preserve_equations: bool
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AdapterConfig:
    """Validated adapter configuration."""

    name: str
    version: str
    source_type: str
    processing: ProcessingConfig
    config_hash: str
    credential_id: Optional[str] = None
    profile: Optional[str] = None
    extensions: Dict[str, Any] = field(default_factory=dict)

    @property
    def raw(self) -> Dict[str, Any]:
        """Return the canonical dictionary representation of the config."""

        root: Dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "source_type": self.source_type,
            "processing_config": {
                "chunk_size": self.processing.chunk_size,
                "chunk_overlap": self.processing.chunk_overlap,
                "preserve_tables": self.processing.preserve_tables,
                "preserve_equations": self.processing.preserve_equations,
                **self.processing.extras,
            },
            "config_hash": self.config_hash,
        }
        if self.credential_id:
            root["credential_id"] = self.credential_id
        if self.profile:
            root["profile"] = self.profile
        if self.extensions:
            root["x_extension"] = self.extensions
        return {"adapter_config": root}


class AdapterConfigError(RuntimeError):
    """Raised when configuration loading or validation fails."""


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _canonicalise_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy suitable for hashing (without config_hash)."""

    canonical = json.loads(json.dumps(config, sort_keys=True))
    adapter_cfg = canonical["adapter_config"]
    adapter_cfg = {
        key: value
        for key, value in adapter_cfg.items()
        if key != "config_hash"
    }
    canonical["adapter_config"] = adapter_cfg
    return canonical


def _compute_hash(config: Dict[str, Any]) -> str:
    canonical = _canonicalise_config(config)
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    import hashlib

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_adapter_config(
    path: Path,
    *,
    schema_path: Optional[Path] = None,
    auto_update_hash: bool = False,
) -> AdapterConfig:
    """Load an adapter configuration file.

    Args:
        path: Path to the adapter_config.json file.
        schema_path: Optional override for the schema path.
        auto_update_hash: When True, mismatched config hashes are rewritten to
            the file after recomputation. When False, mismatches raise
            AdapterConfigError.
    """

    if not path.exists():
        raise AdapterConfigError(f"Config file not found: {path}")

    raw = _load_json(path)

    schema = _load_json(schema_path or SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(raw), key=lambda e: e.path)
    if errors:
        message = "\n".join(f"{list(err.path)}: {err.message}" for err in errors)
        raise AdapterConfigError(
            f"Configuration validation failed for {path}:\n{message}"
        )

    recorded_hash = raw["adapter_config"]["config_hash"]
    computed_hash = _compute_hash(raw)

    if recorded_hash != computed_hash:
        if auto_update_hash:
            raw["adapter_config"]["config_hash"] = computed_hash
            with path.open("w", encoding="utf-8") as handle:
                json.dump(raw, handle, indent=2)
        else:
            raise AdapterConfigError(
                "Configuration hash mismatch. Re-run with auto_update_hash=True "
                "or update the config_hash manually."
            )

    adapter_root = raw["adapter_config"]
    processing_raw = adapter_root["processing_config"]
    x_extension = adapter_root.get("x_extension", {})

    extras = {
        key: value
        for key, value in processing_raw.items()
        if key
        not in {
            "chunk_size",
            "chunk_overlap",
            "preserve_tables",
            "preserve_equations",
        }
    }
    processing = {
        key: value
        for key, value in processing_raw.items()
        if key not in extras
    }
    extension_processing = x_extension.get("processing", {})
    extras = {**extension_processing, **extras}

    return AdapterConfig(
        name=adapter_root["name"],
        version=adapter_root["version"],
        source_type=adapter_root["source_type"],
        credential_id=adapter_root.get("credential_id"),
        profile=adapter_root.get("profile"),
        config_hash=adapter_root["config_hash"],
        processing=ProcessingConfig(
            chunk_size=processing["chunk_size"],
            chunk_overlap=processing["chunk_overlap"],
            preserve_tables=processing["preserve_tables"],
            preserve_equations=processing["preserve_equations"],
            extras=extras,
        ),
        extensions=x_extension,
    )


__all__ = [
    "AdapterConfig",
    "ProcessingConfig",
    "AdapterConfigError",
    "load_adapter_config",
]
