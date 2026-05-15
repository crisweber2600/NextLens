from __future__ import annotations

from pathlib import Path

import yaml


MODULE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = MODULE_ROOT / "assets" / "module.yaml"


def test_module_manifest_identity_fields_are_present() -> None:
    manifest = _manifest()

    assert manifest["module_id"] == "nextlens-src"
    assert manifest["module_name"] == "NextLens Top-Down Bridge"
    assert manifest["module_version"] == "1.0.0"
    assert manifest["description"]
    assert manifest["author"] == "NextLens Team"
    assert manifest["license"] == "MIT"


def test_module_manifest_declares_expected_command_capabilities() -> None:
    manifest = _manifest()
    capabilities = {item["command"]: item for item in manifest["capabilities"]}

    assert set(capabilities) == {"nextlens-new", "nextlens-doctor", "nextlens-salmon"}
    assert capabilities["nextlens-new"]["description"] == "Create one Feature packet from top-down discovery context"
    assert capabilities["nextlens-doctor"]["description"] == "Run non-mutating validation checks on packet or landscape"
    assert capabilities["nextlens-salmon"]["description"] == "Route correction signals through deduplication and impact classification"
    assert all(item["entry_point"] == ".agents/skills/bmad-nextlens/SKILL.md" for item in capabilities.values())
    assert all(item["skill_type"] == "command" for item in capabilities.values())


def test_module_manifest_declares_configuration_variables_and_dependencies() -> None:
    manifest = _manifest()
    configuration = {item["name"]: item for item in manifest["configuration"]}

    assert configuration["NEXTLENS_DOCS_PATH"]["type"] == "string"
    assert configuration["NEXTLENS_DOCS_PATH"]["required"] is True
    assert configuration["NEXTLENS_DOCS_PATH"]["source"] == "feature.yaml"
    assert configuration["NEXTLENS_LANDSCAPE_STORE"]["default"] == "{docs_path}/landscape"
    assert configuration["NEXTLENS_IDEMPOTENCY_TTL_HOURS"]["type"] == "number"
    assert configuration["NEXTLENS_IDEMPOTENCY_TTL_HOURS"]["default"] == 24
    assert manifest["dependencies"] == ["feature-yaml-resolver", "bmad-constitution-resolver"]


def _manifest() -> dict[str, object]:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))