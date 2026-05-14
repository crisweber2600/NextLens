from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


MODULE_PATH = Path(__file__).resolve().parent.parent / "context_loader.py"
SPEC = importlib.util.spec_from_file_location("nextlens_context_loader", MODULE_PATH)
CONTEXT_LOADER = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = CONTEXT_LOADER
SPEC.loader.exec_module(CONTEXT_LOADER)


def test_parse_context_yaml_accepts_direct_payload() -> None:
    loaded = CONTEXT_LOADER.parse_context_yaml(_context_yaml())

    assert loaded.envelope_key is None
    assert loaded.version_mismatch is False
    assert loaded.warnings == ()
    assert loaded.payload["system"]["id"] == "nextlens"
    assert loaded.payload["roles"][0]["id"] == "role-operator"


def test_load_context_file_accepts_top_down_context_envelope(tmp_path: Path) -> None:
    context_path = tmp_path / "top-down-context.yaml"
    context_path.write_text(_context_yaml(envelope=True), encoding="utf-8")

    loaded = CONTEXT_LOADER.load_context_file(context_path)

    assert loaded.source_path == context_path
    assert loaded.envelope_key == "top_down_context"
    assert loaded.payload["discoveryEpoch"]["id"] == "epoch-2026-05-14"


def test_parse_context_yaml_warns_on_schema_version_mismatch() -> None:
    loaded = CONTEXT_LOADER.parse_context_yaml(
        _context_yaml(schema_version="lens.topdown-context.v0")
    )

    assert loaded.version_mismatch is True
    assert len(loaded.warnings) == 1
    assert "expected 'lens.topdown-context.v1'" in loaded.warnings[0]


def test_parse_context_yaml_rejects_malformed_yaml() -> None:
    with pytest.raises(CONTEXT_LOADER.ContextValidationError) as exc_info:
        CONTEXT_LOADER.parse_context_yaml("top_down_context:\n  schemaVersion: [")

    assert "Failed to parse YAML" in str(exc_info.value)


def test_parse_context_yaml_reports_missing_root_field() -> None:
    with pytest.raises(CONTEXT_LOADER.ContextValidationError) as exc_info:
        CONTEXT_LOADER.parse_context_yaml(_context_yaml(include_system=False))

    message = str(exc_info.value)
    assert "Missing required field(s): system." in message


def test_parse_context_yaml_reports_missing_nested_field() -> None:
    with pytest.raises(CONTEXT_LOADER.ContextValidationError) as exc_info:
        CONTEXT_LOADER.parse_context_yaml(_context_yaml(include_role_id=False))

    assert "roles[0].id" in str(exc_info.value)


def _context_yaml(
    *,
    envelope: bool = False,
    schema_version: str = "lens.topdown-context.v1",
    include_system: bool = True,
    include_role_id: bool = True,
) -> str:
    body_lines = [
        f"schemaVersion: {schema_version}",
    ]

    if include_system:
        body_lines.extend(
            [
                "system:",
                "  id: nextlens",
                "  name: NextLens",
                "  thesis: Improve planning fidelity",
                "  status: active",
                "  confidence: high",
            ]
        )

    body_lines.extend(
        [
            "discoveryEpoch:",
            "  id: epoch-2026-05-14",
            "  status: synthesized",
            "  sourceRefs:",
            "    - docs/discovery.md",
            "roles:",
            "  - name: Operator" if not include_role_id else "  - id: role-operator",
            "    name: Operator",
            "outcomes:",
            "  - id: outcome-reduce-ambiguity",
            "    name: Reduce ambiguity",
            "journeys:",
            "  - id: journey-intake",
            "    name: Intake",
            "candidateFeatures:",
            "  - id: feature-context-gate",
            "    title: Context sufficiency gate",
            "stakeholders: []",
            "operatingLoops: []",
            "openQuestions: []",
            "risks: []",
            "decisions: []",
            "relationshipRefs: []",
        ]
    )

    if not envelope:
        return "\n".join(body_lines) + "\n"

    return "\n".join(["top_down_context:", *[f"  {line}" for line in body_lines]]) + "\n"