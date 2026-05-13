from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "skills/bmad-lens-setup/scripts/cleanup-legacy.py"


def run_cleanup(bmad_dir: Path) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bmad-dir",
            str(bmad_dir),
            "--module-code",
            "lens",
            "--also-remove",
            "_config",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_cleanup_legacy_removes_expected_dirs_and_is_idempotent(tmp_path: Path) -> None:
    bmad_dir = tmp_path / "_bmad"
    for name in ["lens", "core", "_config"]:
        path = bmad_dir / name
        path.mkdir(parents=True)
        (path / "placeholder.txt").write_text("legacy", encoding="utf-8")

    first = run_cleanup(bmad_dir)
    second = run_cleanup(bmad_dir)

    assert set(first["directories_removed"]) == {"lens", "core", "_config"}
    assert first["files_removed_count"] == 3
    assert first["safety_checks"] is None
    assert second["directories_removed"] == []
    assert set(second["directories_not_found"]) == {"lens", "core", "_config"}
