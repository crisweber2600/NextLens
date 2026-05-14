"""Persist NextLens landscape state in the control-repo docs tree."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
from pathlib import Path
import stat
import tempfile
from typing import Any, Mapping

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - exercised in runtime environments
    yaml = None
    _YAML_IMPORT_ERROR = exc
else:
    _YAML_IMPORT_ERROR = None


LANDSCAPE_ENTITY_DIRECTORIES = (
    "system",
    "role",
    "outcome",
    "journey",
    "operating_loop",
    "capability",
    "decision",
    "risk",
)


@dataclass(frozen=True)
class LandscapeEntityRecord:
    entity_type: str
    semantic_id: str
    opaque_id: str
    name: str
    snapshot: Mapping[str, Any]
    relationships: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LandscapePersistenceResult:
    status: str
    path: Path | None = None
    error: str | None = None
    rollback_performed: bool = False
    blocks_packet_emission: bool = False


def initialize_landscape_dirs(docs_path: str | Path) -> dict[str, Path]:
    docs_root = Path(docs_path)
    landscape_root = docs_root / "landscape"
    landscape_root.mkdir(parents=True, exist_ok=True)

    directories: dict[str, Path] = {}
    for directory_name in LANDSCAPE_ENTITY_DIRECTORIES:
        directory_path = landscape_root / directory_name
        directory_path.mkdir(parents=True, exist_ok=True)
        directories[directory_name] = directory_path

    return directories


def persist_landscape_entity(
    docs_path: str | Path,
    entity: LandscapeEntityRecord,
) -> LandscapePersistenceResult:
    yaml_module = _require_yaml_support()

    try:
        directories = initialize_landscape_dirs(docs_path)
        entity_directory = _entity_directory_name(entity.entity_type)
        if entity_directory not in directories:
            raise ValueError(
                f"Unsupported landscape entity type '{entity.entity_type}'."
            )

        final_path = directories[entity_directory] / f"{entity.semantic_id}.yaml"
        payload = _build_payload(entity, entity_directory)
        existed_before = final_path.exists()
        backup_path = final_path.with_suffix(final_path.suffix + ".bak")
        temp_path: Path | None = None
        rollback_performed = False

        try:
            fd, temp_name = tempfile.mkstemp(
                dir=str(final_path.parent),
                prefix=f"{entity.semantic_id}-",
                suffix=".tmp",
            )
            temp_path = Path(temp_name)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                yaml_module.safe_dump(payload, handle, sort_keys=False)

            if existed_before:
                os.replace(final_path, backup_path)

            os.replace(temp_path, final_path)
            temp_path = None
            _set_read_write_permissions(final_path)
            _validate_written_payload(final_path, payload, yaml_module)

            if backup_path.exists():
                backup_path.unlink()

            return LandscapePersistenceResult(status="pass", path=final_path)
        except Exception as exc:  # pragma: no cover - exercised via tests through failure simulation
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

            if existed_before and backup_path.exists():
                if final_path.exists():
                    final_path.unlink()
                os.replace(backup_path, final_path)
                rollback_performed = True
            elif final_path.exists():
                final_path.unlink()
                rollback_performed = True

            return LandscapePersistenceResult(
                status="fail",
                path=final_path,
                error=str(exc),
                rollback_performed=rollback_performed,
                blocks_packet_emission=True,
            )
    except Exception as exc:
        return LandscapePersistenceResult(
            status="fail",
            error=str(exc),
            rollback_performed=False,
            blocks_packet_emission=True,
        )


def _require_yaml_support():
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to persist landscape state. Install PyYAML before running the landscape store."
        ) from _YAML_IMPORT_ERROR
    return yaml


def _entity_directory_name(entity_type: str) -> str:
    return str(entity_type).strip().lower().replace("-", "_").replace(" ", "_")


def _build_payload(entity: LandscapeEntityRecord, entity_directory: str) -> dict[str, Any]:
    timestamp = _utc_timestamp()
    metadata = dict(entity.metadata)
    metadata.setdefault("createdAt", timestamp)
    metadata.setdefault("updatedAt", timestamp)
    metadata.setdefault("source", "nextlens")
    metadata.setdefault("author", "nextlens")

    return {
        "entityType": entity_directory,
        "identity": {
            "semanticId": entity.semantic_id,
            "opaqueId": entity.opaque_id,
            "name": entity.name,
        },
        "snapshot": dict(entity.snapshot),
        "relationships": dict(entity.relationships),
        "metadata": metadata,
    }


def _validate_written_payload(path: Path, expected_payload: Mapping[str, Any], yaml_module: Any) -> None:
    loaded = yaml_module.safe_load(path.read_text(encoding="utf-8"))
    if loaded != dict(expected_payload):
        raise ValueError(f"Persisted landscape payload validation failed for '{path}'.")


def _set_read_write_permissions(path: Path) -> None:
    path.chmod(
        stat.S_IRUSR
        | stat.S_IWUSR
        | stat.S_IRGRP
        | stat.S_IWGRP
        | stat.S_IROTH
    )


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")