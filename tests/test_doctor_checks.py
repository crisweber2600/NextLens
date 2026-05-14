from __future__ import annotations

import json
from pathlib import Path

from scripts.lens_topdown.doctor_checks import main, run_doctor
from scripts.lens_topdown.rebuild_derived_graph import main as rebuild_main


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture_definitions(name: str) -> dict:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "nextlens" / "src" / "nextlens-src-topdownlens" / "examples" / "doctor-fixtures" / f"{name}.json"
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise AssertionError(f"doctor fixture {name} not found")


def _apply_fixture(feature_docs: Path, fixture: dict) -> None:
    for filename, data in fixture.get("entities", {}).items():
        _write_json(feature_docs / "examples" / "entities" / filename, data)
    for filename, data in fixture.get("relationships", {}).items():
        _write_json(feature_docs / "examples" / filename, data)
    for filename, data in fixture.get("bmad_packets", {}).items():
        _write_json(feature_docs / "examples" / filename, data)
    for filename, data in fixture.get("salmon_signals", {}).items():
        _write_json(feature_docs / "examples" / "salmon-signals" / filename, data)


def _valid_fixture(tmp_path: Path) -> Path:
    feature_docs = tmp_path / "feature-docs"
    _apply_fixture(feature_docs, _fixture_definitions("positive"))
    assert rebuild_main(["--feature-docs", str(feature_docs)]) == 0
    return feature_docs


def test_doctor_positive_fixture_has_no_blocking_findings(tmp_path: Path) -> None:
    feature_docs = _valid_fixture(tmp_path)

    findings = run_doctor(feature_docs)

    assert not [finding for finding in findings if finding["severity"] == "blocking"]
    assert {finding["check"] for finding in findings} >= {"derived_freshness", "open_blocking_salmon_signal"}


def test_doctor_negative_fixture_reports_each_blocking_check(tmp_path: Path) -> None:
    feature_docs = _valid_fixture(tmp_path)
    _apply_fixture(feature_docs, _fixture_definitions("negative"))

    findings = run_doctor(feature_docs)
    checks = {finding["check"] for finding in findings if finding["severity"] == "blocking"}

    assert "missing_id" in checks
    assert "broken_reference" in checks
    assert "derived_freshness" in checks
    assert "missing_feature_scope" in checks
    assert "bmad_traceability" in checks
    assert "open_blocking_salmon_signal" in checks


def test_strict_mode_exits_nonzero_on_blocking_findings(tmp_path: Path) -> None:
    feature_docs = _valid_fixture(tmp_path)
    _apply_fixture(feature_docs, _fixture_definitions("negative"))

    assert main(["--feature-docs", str(feature_docs), "--strict"]) == 1