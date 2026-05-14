"""Load and validate NextLens top-down discovery context."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - exercised in runtime environments
    yaml = None
    _YAML_IMPORT_ERROR = exc
else:
    _YAML_IMPORT_ERROR = None


EXPECTED_SCHEMA_VERSION = "lens.topdown-context.v1"
ENVELOPE_KEY = "top_down_context"
REQUIRED_ROOT_FIELDS = (
    "schemaVersion",
    "system",
    "discoveryEpoch",
    "roles",
    "outcomes",
    "journeys",
    "candidateFeatures",
)
REQUIRED_OBJECT_FIELDS = {
    "system": ("id", "name", "thesis", "status", "confidence"),
    "discoveryEpoch": ("id", "status", "sourceRefs"),
}
REQUIRED_COLLECTION_ITEM_FIELDS = {
    "roles": ("id",),
    "outcomes": ("id",),
    "journeys": ("id",),
    "candidateFeatures": ("id",),
}


@dataclass(frozen=True)
class LoadedContext:
    payload: dict[str, Any]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    version_mismatch: bool = False
    source_path: Path | None = None
    envelope_key: str | None = None


class ContextValidationError(ValueError):
    pass


def load_context_file(path: str | Path) -> LoadedContext:
    source_path = Path(path)
    try:
        raw_text = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContextValidationError(
            f"Failed to read context file '{source_path}': {exc}"
        ) from exc

    return parse_context_yaml(raw_text, source_path=source_path)


def parse_context_yaml(raw_text: str, *, source_path: str | Path | None = None) -> LoadedContext:
    yaml_module = _require_yaml_support()
    source_label = str(source_path) if source_path is not None else "<memory>"

    try:
        document = yaml_module.safe_load(raw_text)
    except yaml_module.YAMLError as exc:
        raise ContextValidationError(
            f"Failed to parse YAML from {source_label}: {exc}"
        ) from exc

    if not isinstance(document, Mapping):
        raise ContextValidationError(
            f"Context document from {source_label} must be a mapping at the root."
        )

    payload, envelope_key = _extract_payload(document, source_label)
    warnings = _validate_payload(payload, source_label)

    return LoadedContext(
        payload=copy.deepcopy(dict(payload)),
        warnings=tuple(warnings),
        version_mismatch=bool(warnings),
        source_path=Path(source_path) if source_path is not None else None,
        envelope_key=envelope_key,
    )


def _require_yaml_support():
    if yaml is None:
        raise ContextValidationError(
            "PyYAML is required to load NextLens context files. "
            "Install PyYAML before running the context parser."
        ) from _YAML_IMPORT_ERROR
    return yaml


def _extract_payload(document: Mapping[str, Any], source_label: str) -> tuple[Mapping[str, Any], str | None]:
    if ENVELOPE_KEY not in document:
        return document, None

    payload = document[ENVELOPE_KEY]
    if not isinstance(payload, Mapping):
        raise ContextValidationError(
            f"Field '{ENVELOPE_KEY}' in {source_label} must contain a mapping."
        )
    return payload, ENVELOPE_KEY


def _validate_payload(payload: Mapping[str, Any], source_label: str) -> list[str]:
    missing_fields: list[str] = []
    invalid_fields: list[str] = []

    for field_name in REQUIRED_ROOT_FIELDS:
        if field_name not in payload:
            missing_fields.append(field_name)

    if "schemaVersion" in payload and _is_blank(payload.get("schemaVersion")):
        invalid_fields.append("schemaVersion must be a non-empty string")

    _validate_required_objects(payload, missing_fields, invalid_fields)
    _validate_required_collections(payload, missing_fields, invalid_fields)

    if missing_fields or invalid_fields:
        raise ContextValidationError(
            _build_validation_error_message(source_label, missing_fields, invalid_fields)
        )

    schema_version = str(payload["schemaVersion"]).strip()
    if schema_version != EXPECTED_SCHEMA_VERSION:
        return [
            "Schema version mismatch: expected "
            f"'{EXPECTED_SCHEMA_VERSION}' but received '{schema_version}'. Continuing with a warning."
        ]

    return []


def _validate_required_objects(
    payload: Mapping[str, Any],
    missing_fields: list[str],
    invalid_fields: list[str],
) -> None:
    for object_name, required_fields in REQUIRED_OBJECT_FIELDS.items():
        if object_name not in payload:
            continue

        value = payload[object_name]
        if not isinstance(value, Mapping):
            invalid_fields.append(f"{object_name} must be a mapping")
            continue

        for field_name in required_fields:
            field_path = f"{object_name}.{field_name}"
            if field_name not in value or _is_blank(value.get(field_name)):
                missing_fields.append(field_path)


def _validate_required_collections(
    payload: Mapping[str, Any],
    missing_fields: list[str],
    invalid_fields: list[str],
) -> None:
    for collection_name, required_fields in REQUIRED_COLLECTION_ITEM_FIELDS.items():
        if collection_name not in payload:
            continue

        value = payload[collection_name]
        if not isinstance(value, list):
            invalid_fields.append(f"{collection_name} must be a list")
            continue

        for index, item in enumerate(value):
            item_path = f"{collection_name}[{index}]"
            if not isinstance(item, Mapping):
                invalid_fields.append(f"{item_path} must be a mapping")
                continue

            for field_name in required_fields:
                field_path = f"{item_path}.{field_name}"
                if field_name not in item or _is_blank(item.get(field_name)):
                    missing_fields.append(field_path)


def _build_validation_error_message(
    source_label: str,
    missing_fields: list[str],
    invalid_fields: list[str],
) -> str:
    parts = [f"Context validation failed for {source_label}."]
    if missing_fields:
        parts.append("Missing required field(s): " + ", ".join(sorted(set(missing_fields))) + ".")
    if invalid_fields:
        parts.append("Invalid field(s): " + ", ".join(sorted(set(invalid_fields))) + ".")
    return " ".join(parts)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False