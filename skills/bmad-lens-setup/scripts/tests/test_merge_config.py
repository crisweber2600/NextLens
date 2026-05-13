from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "skills/bmad-lens-setup/scripts/merge-config.py"


def test_merge_config_replaces_existing_lens_and_uses_legacy_defaults(tmp_path: Path) -> None:
    module_yaml = tmp_path / "module.yaml"
    module_yaml.write_text(
        "\n".join(
            [
                "code: lens",
                "name: LENS",
                "description: Test module",
                "module_version: 1.0.0",
                "lens_output_folder:",
                "  default: \"{project-root}/_bmad-output/lens\"",
                "  result: \"{project-root}/{value}\"",
            ]
        ),
        encoding="utf-8",
    )
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps({"module": {}}), encoding="utf-8")
    config = tmp_path / "_bmad" / "config.yaml"
    user_config = tmp_path / "_bmad" / "config.user.yaml"
    config.parent.mkdir()
    config.write_text("output_folder: '{project-root}/_bmad-output'\nlens:\n  stale_key: old\n", encoding="utf-8")
    legacy = tmp_path / "_bmad" / "lens"
    legacy.mkdir()
    (legacy / "config.yaml").write_text("lens_output_folder: '{project-root}/legacy-lens'\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--config-path",
            str(config),
            "--user-config-path",
            str(user_config),
            "--module-yaml",
            str(module_yaml),
            "--answers",
            str(answers),
            "--legacy-dir",
            str(tmp_path / "_bmad"),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    merged = yaml.safe_load(config.read_text(encoding="utf-8"))
    assert payload["status"] == "success"
    assert "stale_key" not in merged["lens"]
    assert merged["lens"]["lens_output_folder"] == "{project-root}/legacy-lens"
    assert not (legacy / "config.yaml").exists()
