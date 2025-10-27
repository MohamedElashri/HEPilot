"""Schema validation utilities for collector artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

from jsonschema import Draft202012Validator

_SCHEMA_FILES = {
    "chunk_metadata": "chunk_metadata.schema.json",
    "catalog": "catalog.schema.json",
    "discovery_output": "discovery_output.schema.json",
    "document_metadata": "document_metadata.schema.json",
    "processing_metadata": "processing_metadata.schema.json",
}


class CollectorValidationError(RuntimeError):
    """Raised when collector artifacts fail schema validation."""


class CollectorSchemaValidator:
    """Validate collector artifacts against standard schemas."""

    def __init__(self, schema_dir: Path | None = None) -> None:
        if schema_dir is None:
            schema_dir = Path(__file__).resolve().parents[2] / "standards" / "schemas"
        self.schema_dir = schema_dir
        self._validators: Dict[str, Draft202012Validator] = {}

    def validate_chunk_metadata(self, payload: Dict[str, Any]) -> None:
        self._validate("chunk_metadata", payload)

    def validate_catalog(self, payload: Dict[str, Any]) -> None:
        self._validate("catalog", payload)

    def validate_discovery_output(self, payload: Dict[str, Any]) -> None:
        self._validate("discovery_output", payload)

    def validate_document_metadata(self, payload: Dict[str, Any]) -> None:
        self._validate("document_metadata", payload)

    def validate_processing_metadata(self, payload: Dict[str, Any]) -> None:
        self._validate("processing_metadata", payload)

    def _validate(self, schema_key: str, payload: Dict[str, Any]) -> None:
        validator = self._get_validator(schema_key)
        errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
        if errors:
            message = "\n".join(f"{list(err.path)}: {err.message}" for err in errors)
            raise CollectorValidationError(
                f"Payload failed '{schema_key}' schema validation:\n{message}"
            )

    def _get_validator(self, schema_key: str) -> Draft202012Validator:
        if schema_key not in _SCHEMA_FILES:
            raise CollectorValidationError(f"Unknown schema key: {schema_key}")
        if schema_key not in self._validators:
            schema_path = self.schema_dir / _SCHEMA_FILES[schema_key]
            if not schema_path.exists():
                raise CollectorValidationError(
                    f"Schema file not found: {schema_path}"
                )
            with schema_path.open("r", encoding="utf-8") as handle:
                schema = json.load(handle)
            self._validators[schema_key] = Draft202012Validator(schema)
        return self._validators[schema_key]


__all__ = [
    "CollectorSchemaValidator",
    "CollectorValidationError",
]
