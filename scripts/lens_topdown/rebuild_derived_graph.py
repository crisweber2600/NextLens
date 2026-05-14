"""Rebuild a disposable TopDownLens derived graph from source records."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v1.0"
GRAPH_ID = "graph.topdownlens_derived"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _write_json_if_changed(path: Path, data: dict[str, Any]) -> bool:
    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == rendered:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return True


def _stable_timestamp(source_hash: str) -> str:
    offset = int(source_hash[:8], 16) % (366 * 24 * 60 * 60)
    day, remainder = divmod(offset, 24 * 60 * 60)
    hour, remainder = divmod(remainder, 60 * 60)
    minute, second = divmod(remainder, 60)
    return f"2026-01-{day % 31 + 1:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


def _source_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def load_sources(feature_docs: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[Path]]:
    entity_paths = sorted((feature_docs / "examples" / "entities").glob("*.json"))
    relationship_paths = sorted((feature_docs / "examples").glob("relationship*.json"))
    entities = [_read_json(path) | {"_source_path": _relative(path, feature_docs)} for path in entity_paths]
    relationships = [_read_json(path) | {"_source_path": _relative(path, feature_docs)} for path in relationship_paths]
    return entities, relationships, entity_paths + relationship_paths


def build_graph(feature_docs: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    entities, relationships, source_paths = load_sources(feature_docs)
    source_digest = _source_hash(source_paths)
    generated_at = _stable_timestamp(source_digest)

    entity_ids = {entity["id"] for entity in entities if "id" in entity}
    findings: list[dict[str, Any]] = []
    for relationship in relationships:
        relationship_id = relationship.get("id", "rel.unknown")
        for endpoint in ("from", "to"):
            target_id = relationship.get(endpoint)
            if target_id not in entity_ids:
                findings.append(
                    {
                        "severity": "blocking",
                        "check": "broken_reference",
                        "relationship_id": relationship_id,
                        "field": endpoint,
                        "target_id": target_id,
                        "message": f"{relationship_id} {endpoint} references missing entity {target_id}",
                    }
                )

    graph = {
        "id": GRAPH_ID,
        "derived": True,
        "rebuildable_from": [_relative(path, feature_docs) for path in sorted(source_paths)],
        "generated_at": generated_at,
        "nodes": [
            {
                "id": entity["id"],
                "kind": entity["kind"],
                "source_path": entity["_source_path"],
            }
            for entity in sorted(entities, key=lambda item: item["id"])
        ],
        "edges": [
            {
                "relationship_id": relationship["id"],
                "from": relationship["from"],
                "to": relationship["to"],
                "type": relationship["type"],
            }
            for relationship in sorted(relationships, key=lambda item: item["id"])
        ],
    }
    freshness = {
        "schema_version": SCHEMA_VERSION,
        "derived": True,
        "source_hash": source_digest,
        "timestamp_source": "sha256(source_paths_and_contents)",
        "rebuilt_at": generated_at,
        "source_files": graph["rebuildable_from"],
        "graph_path": "derived/graph.json",
        "status": "stale" if findings else "fresh",
        "findings": findings,
    }
    return graph, freshness


def rebuild(feature_docs: Path, output_dir: Path) -> tuple[dict[str, Any], bool]:
    graph, freshness = build_graph(feature_docs)
    changed = False
    changed |= _write_json_if_changed(output_dir / "graph.json", graph)
    changed |= _write_json_if_changed(output_dir / "freshness.json", freshness)
    return freshness, changed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild the TopDownLens derived graph.")
    parser.add_argument(
        "--feature-docs",
        type=Path,
        default=Path("docs/nextlens/src/nextlens-src-topdownlens"),
        help="Feature docs root containing examples/entities and relationship records.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for graph.json and freshness.json. Defaults to <feature-docs>/derived.",
    )
    parser.add_argument(
        "--allow-broken",
        action="store_true",
        help="Write outputs and return success even when broken references are found.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    feature_docs = args.feature_docs.resolve()
    output_dir = (args.output_dir or feature_docs / "derived").resolve()
    freshness, changed = rebuild(feature_docs, output_dir)
    result = {
        "status": freshness["status"],
        "changed": changed,
        "graph_path": str(output_dir / "graph.json"),
        "freshness_path": str(output_dir / "freshness.json"),
        "findings": freshness["findings"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if freshness["findings"] and not args.allow_broken:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())