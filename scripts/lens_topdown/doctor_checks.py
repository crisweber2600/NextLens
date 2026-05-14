"""Run non-mutating TopDownLens health checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.lens_topdown.rebuild_derived_graph import build_graph

BLOCKING = "blocking"
INFO = "info"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {"_invalid": f"{path} does not contain a JSON object"}
    return data


def _finding(severity: str, check: str, target_id: str | None, message: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "check": check,
        "target_id": target_id,
        "message": message,
    }


def _json_files(root: Path, pattern: str) -> list[Path]:
    return sorted(root.glob(pattern)) if root.exists() else []


def _load_records(feature_docs: Path) -> dict[str, list[tuple[Path, dict[str, Any]]]]:
    examples = feature_docs / "examples"
    return {
        "entities": [(path, _read_json(path)) for path in _json_files(examples / "entities", "*.json")],
        "relationships": [(path, _read_json(path)) for path in _json_files(examples, "relationship*.json")],
        "bmad_packets": [(path, _read_json(path)) for path in _json_files(examples, "bmad-packet*.json")],
        "salmon_signals": [(path, _read_json(path)) for path in _json_files(examples / "salmon-signals", "*.json")],
    }


def _stable_ids(records: dict[str, list[tuple[Path, dict[str, Any]]]]) -> set[str]:
    ids: set[str] = set()
    for group in records.values():
        for _, record in group:
            record_id = record.get("id")
            if isinstance(record_id, str):
                ids.add(record_id)
    return ids


def check_missing_ids(records: dict[str, list[tuple[Path, dict[str, Any]]]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for group_name, group in records.items():
        for path, record in group:
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id.strip():
                findings.append(
                    _finding(
                        BLOCKING,
                        "missing_id",
                        path.as_posix(),
                        f"{group_name} record {path.as_posix()} is missing a stable id",
                    )
                )
    return findings


def check_broken_references(feature_docs: Path, records: dict[str, list[tuple[Path, dict[str, Any]]]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    known_ids = _stable_ids(records)

    for _, relationship in records["relationships"]:
        relationship_id = relationship.get("id")
        for endpoint in ("from", "to"):
            target_id = relationship.get(endpoint)
            if target_id and target_id not in known_ids:
                findings.append(
                    _finding(BLOCKING, "broken_reference", target_id, f"{relationship_id} {endpoint} references missing entity {target_id}")
                )
        for evidence_id in relationship.get("evidence", []):
            if evidence_id not in known_ids:
                findings.append(
                    _finding(BLOCKING, "broken_reference", evidence_id, f"{relationship_id} evidence references missing entity {evidence_id}")
                )

    for _, packet in records["bmad_packets"]:
        packet_id = packet.get("id")
        selected_id = packet.get("selected_feature", {}).get("id")
        if selected_id and selected_id not in known_ids:
            findings.append(_finding(BLOCKING, "broken_reference", selected_id, f"{packet_id} selected_feature references missing entity"))
        traceability = packet.get("traceability", {})
        for values in traceability.values():
            if isinstance(values, list):
                for target_id in values:
                    if target_id not in known_ids:
                        findings.append(_finding(BLOCKING, "broken_reference", target_id, f"{packet_id} traceability references missing entity"))
        for evidence in packet.get("acceptance_evidence", []):
            evidence_id = evidence.get("evidence_id") if isinstance(evidence, dict) else None
            if evidence_id and evidence_id not in known_ids:
                findings.append(_finding(BLOCKING, "broken_reference", evidence_id, f"{packet_id} acceptance evidence references missing entity"))

    for _, signal in records["salmon_signals"]:
        signal_id = signal.get("id")
        source_id = signal.get("source", {}).get("id")
        if source_id and source_id not in known_ids:
            findings.append(_finding(BLOCKING, "broken_reference", source_id, f"{signal_id} source references missing entity"))
        for evidence_id in signal.get("evidence_refs", []):
            if evidence_id not in known_ids:
                findings.append(_finding(BLOCKING, "broken_reference", evidence_id, f"{signal_id} evidence_refs references missing entity"))
    return findings


def check_derived_freshness(feature_docs: Path) -> list[dict[str, Any]]:
    freshness_path = feature_docs / "derived" / "freshness.json"
    if not freshness_path.exists():
        return [_finding(INFO, "derived_freshness", None, "No derived freshness marker is present")]
    try:
        current_freshness = build_graph(feature_docs)[1]
    except (KeyError, ValueError) as exc:
        return [
            _finding(
                BLOCKING,
                "derived_freshness",
                "derived/freshness.json",
                f"Cannot compute freshness because source records are invalid: {exc}",
            )
        ]
    stored_freshness = _read_json(freshness_path)
    findings: list[dict[str, Any]] = []
    if stored_freshness.get("source_hash") != current_freshness["source_hash"]:
        findings.append(_finding(BLOCKING, "derived_freshness", "derived/freshness.json", "Derived graph freshness marker is stale"))
    for finding in stored_freshness.get("findings", []):
        if isinstance(finding, dict):
            findings.append(finding)
    if not findings:
        findings.append(_finding(INFO, "derived_freshness", "derived/freshness.json", "Derived graph freshness marker is current"))
    return findings


def check_bmad_packets(records: dict[str, list[tuple[Path, dict[str, Any]]]]) -> list[dict[str, Any]]:
    if not records["bmad_packets"]:
        return [_finding(BLOCKING, "bmad_traceability", None, "No BMAD packet examples were found")]
    findings: list[dict[str, Any]] = []
    required_traceability = ["outcomes", "journeys", "capabilities", "evidence"]
    for path, packet in records["bmad_packets"]:
        packet_id = packet.get("id", path.as_posix())
        selected = packet.get("selected_feature", {})
        if not selected.get("id"):
            findings.append(_finding(BLOCKING, "missing_feature_scope", packet_id, "BMAD packet is missing selected_feature.id"))
        boundaries = packet.get("scope_boundaries", {})
        for key in ("include", "exclude", "guardrails"):
            if not boundaries.get(key):
                findings.append(_finding(BLOCKING, "missing_feature_scope", packet_id, f"BMAD packet scope_boundaries.{key} is empty"))
        traceability = packet.get("traceability", {})
        for key in required_traceability:
            if not traceability.get(key):
                findings.append(_finding(BLOCKING, "bmad_traceability", packet_id, f"BMAD packet traceability.{key} is empty"))
    return findings


def check_salmon_signals(records: dict[str, list[tuple[Path, dict[str, Any]]]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for _, signal in records["salmon_signals"]:
        if signal.get("severity") == BLOCKING and signal.get("status") == "open":
            signal_id = signal.get("id")
            findings.append(_finding(BLOCKING, "open_blocking_salmon_signal", signal_id, signal.get("finding", "Open blocking Salmon signal")))
    if not findings:
        findings.append(_finding(INFO, "open_blocking_salmon_signal", None, "No open blocking Salmon signals found"))
    return findings


def run_doctor(feature_docs: Path) -> list[dict[str, Any]]:
    records = _load_records(feature_docs)
    findings: list[dict[str, Any]] = []
    findings.extend(check_missing_ids(records))
    findings.extend(check_broken_references(feature_docs, records))
    findings.extend(check_derived_freshness(feature_docs))
    findings.extend(check_bmad_packets(records))
    findings.extend(check_salmon_signals(records))
    return sorted(findings, key=lambda item: (item["severity"] != BLOCKING, item["check"], str(item.get("target_id"))))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TopDownLens doctor checks.")
    parser.add_argument(
        "--feature-docs",
        type=Path,
        default=Path("docs/nextlens/src/nextlens-src-topdownlens"),
        help="Feature docs root to inspect.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when blocking findings exist.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    findings = run_doctor(args.feature_docs.resolve())
    print(json.dumps(findings, indent=2, sort_keys=True))
    if args.strict and any(finding.get("severity") == BLOCKING for finding in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())