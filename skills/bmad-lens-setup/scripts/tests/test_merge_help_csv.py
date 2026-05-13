from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "skills/bmad-lens-setup/scripts/merge-help-csv.py"
HEADER = "module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs\n"


def rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8")))


def test_merge_help_csv_replaces_existing_module_rows_and_preserves_others(tmp_path: Path) -> None:
    target = tmp_path / "module-help.csv"
    target.write_text(
        HEADER
        + "Other,other-skill,Other,OT,Other desc,run,,anytime,,,false,out,thing\n"
        + "LENS,bmad-lens-old,Old,OLD,Old desc,old,,anytime,,,false,out,old\n",
        encoding="utf-8",
    )
    source = tmp_path / "source.csv"
    source.write_text(
        HEADER
        + "LENS,bmad-lens-help,LENS Help,LHP,Guide,guide,,anytime,,,false,lens_output_folder,help\n"
        + "LENS,bmad-lens-context-check,Context Check,LCC,Gate,check-context,,1-analysis,,bmad-lens-prepare-bmad:prepare-bmad,true,lens_gates_folder,gate\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--target", str(target), "--source", str(source)],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    merged = rows(target)
    assert payload["rows_removed"] == 1
    assert payload["rows_added"] == 2
    assert {row["skill"] for row in merged} == {"other-skill", "bmad-lens-help", "bmad-lens-context-check"}
    assert next(row for row in merged if row["skill"] == "bmad-lens-context-check")["required"] == "true"
