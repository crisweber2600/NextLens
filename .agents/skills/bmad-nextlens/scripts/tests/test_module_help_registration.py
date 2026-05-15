from __future__ import annotations

import csv
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[2]
MODULE_HELP_PATH = MODULE_ROOT / "assets" / "module-help.csv"


def test_module_help_csv_has_required_header_and_commands() -> None:
    rows = _rows()

    assert rows[0].keys() == {"command", "category", "description", "entry_point", "trigger_keywords"}
    assert [row["command"] for row in rows] == ["nextlens-new", "nextlens-doctor", "nextlens-salmon"]


def test_module_help_csv_registers_expected_command_metadata() -> None:
    rows = {row["command"]: row for row in _rows()}

    assert rows["nextlens-new"] == {
        "command": "nextlens-new",
        "category": "command",
        "description": "Create one Feature packet from top-down discovery context",
        "entry_point": "commands/new.ts",
        "trigger_keywords": "nextlens new,top-down bridge,feature packet,deterministic selection",
    }
    assert rows["nextlens-doctor"] == {
        "command": "nextlens-doctor",
        "category": "command",
        "description": "Run non-mutating validation checks on packet or landscape",
        "entry_point": "commands/doctor.ts",
        "trigger_keywords": "nextlens doctor,validate packet,check landscape,doctor validation",
    }
    assert rows["nextlens-salmon"] == {
        "command": "nextlens-salmon",
        "category": "command",
        "description": "Route correction signals through deduplication and impact classification",
        "entry_point": "commands/salmon.ts",
        "trigger_keywords": "nextlens salmon,route correction,deduplicate events,correction routing",
    }


def test_module_help_keywords_cover_command_feature_function_and_domain_terms() -> None:
    rows = {row["command"]: row for row in _rows()}

    assert _keywords(rows["nextlens-new"]) >= {"nextlens new", "top-down bridge", "feature packet", "deterministic selection"}
    assert _keywords(rows["nextlens-doctor"]) >= {"nextlens doctor", "validate packet", "check landscape", "doctor validation"}
    assert _keywords(rows["nextlens-salmon"]) >= {"nextlens salmon", "route correction", "deduplicate events", "correction routing"}


def _rows() -> list[dict[str, str]]:
    with MODULE_HELP_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _keywords(row: dict[str, str]) -> set[str]:
    return {item.strip() for item in row["trigger_keywords"].split(",") if item.strip()}