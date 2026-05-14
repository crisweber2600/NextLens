from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.lens_topdown.rebuild_derived_graph import main


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _copy_fixture(tmp_path: Path) -> Path:
    source = None
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "nextlens" / "src" / "nextlens-src-topdownlens" / "examples"
        if candidate.exists():
            source = candidate
            break
    assert source is not None
    feature_docs = tmp_path / "feature-docs"
    shutil.copytree(source, feature_docs / "examples")
    return feature_docs


def test_rebuild_from_clean_tree(tmp_path: Path) -> None:
    feature_docs = _copy_fixture(tmp_path)

    exit_code = main(["--feature-docs", str(feature_docs)])

    assert exit_code == 0
    graph = json.loads((feature_docs / "derived" / "graph.json").read_text(encoding="utf-8"))
    freshness = json.loads((feature_docs / "derived" / "freshness.json").read_text(encoding="utf-8"))
    assert graph["derived"] is True
    assert graph["rebuildable_from"]
    assert {node["id"] for node in graph["nodes"]} >= {"system.nextlens", "feature.topdownlens_contract"}
    assert freshness["status"] == "fresh"
    assert freshness["findings"] == []


def test_rebuild_reports_broken_references(tmp_path: Path) -> None:
    feature_docs = tmp_path / "feature-docs"
    _write_json(
        feature_docs / "examples" / "entities" / "system.nextlens.json",
        {
            "id": "system.nextlens",
            "kind": "system",
        },
    )
    _write_json(
        feature_docs / "examples" / "relationship-example.json",
        {
            "id": "rel.system.nextlens.depends_on.feature.missing",
            "from": "system.nextlens",
            "to": "feature.missing",
            "type": "depends_on",
        },
    )

    exit_code = main(["--feature-docs", str(feature_docs)])

    freshness = json.loads((feature_docs / "derived" / "freshness.json").read_text(encoding="utf-8"))

    assert exit_code == 2
    assert freshness["status"] == "stale"
    assert freshness["findings"][0]["check"] == "broken_reference"
    assert freshness["findings"][0]["target_id"] == "feature.missing"


def test_rebuild_is_idempotent(tmp_path: Path) -> None:
    feature_docs = _copy_fixture(tmp_path)

    assert main(["--feature-docs", str(feature_docs)]) == 0
    graph_before = (feature_docs / "derived" / "graph.json").read_text(encoding="utf-8")
    freshness_before = (feature_docs / "derived" / "freshness.json").read_text(encoding="utf-8")

    assert main(["--feature-docs", str(feature_docs)]) == 0

    assert (feature_docs / "derived" / "graph.json").read_text(encoding="utf-8") == graph_before
    assert (feature_docs / "derived" / "freshness.json").read_text(encoding="utf-8") == freshness_before