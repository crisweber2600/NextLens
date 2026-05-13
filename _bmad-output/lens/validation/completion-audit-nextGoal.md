# LENS Completion Audit - nextGoal.md

Date: 2026-05-13

Source goal: `nextGoal.md`
Supporting context: `context.md` was present but empty.

Official references checked:

- BMAD Builder documentation: https://bmad-builder-docs.bmad-method.org/llms-full.txt
- BMAD Method documentation: https://docs.bmad-method.org/llms-full.txt

## Result

Status: pass

The repository contains a BMAD-native LENS module using the `lens` module code and the `bmad-lens-*` skill surface. The change keeps LENS self-contained, keeps slices as the central unit, preserves top-down and bottom-up modes, and does not scaffold NorthStarET or any application product.

## Requirement Evidence

### A. Help System Gate

- Updated `skills/bmad-lens-setup/assets/module-help.csv`.
- Updated `_bmad/module-help.csv`.
- `bmad-lens-context-check` is `required=true`.
- `bmad-lens-context-check` runs after `bmad-lens-synthesize` and before `bmad-lens-prepare-bmad`.
- Downstream internal sequence is registered through prepare, sync, guard, validation, Salmon, Doctor, and Auspex.
- Parent BMAD workflow identifiers are documented in references/evals, not placed in the module CSV, because the BMAD Builder module validator validates `after` and `before` references inside the module skill set.

### B. Schema, Templates, Fixtures, Validator

- Updated `skills/bmad-lens-setup/assets/lens/schemas/lens-entity.schema.json` with actual LENS major artifact kinds and reconciled status values.
- Added or reconciled metadata on relationship, promotion gate, impact map, story guard, BMAD packet, and top-down fixture artifacts.
- Strengthened `skills/bmad-lens-setup/assets/lens/scripts/validate_lens_assets.py` to derive required skills from `.claude-plugin/marketplace.json`, enforce semantic kind/status consistency, require metadata on major entities, require top-down fixture coverage, require dual BMAD packet templates, and require setup-script tests.

### C. Project Context

- Added canonical template `skills/bmad-lens-setup/assets/lens/templates/project-context.md`.
- Updated `_bmad-output/project-context.md`.
- Updated `skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py init` to create rich project context when absent without overwriting an existing file.

### D. Impact Map Graph Projection

- Updated `lens_artifact_ops.py` so impact maps project:
  - `directly_impacted` to `impacted_by` relationships and traceability.
  - `possibly_conflicting` to `possibly_conflicts_with`.
  - `shared_files` to `touches_file`.
  - `shared_contracts` to `touches_contract`.
  - non-empty related workstream gates to `workstream_impact_gate` warnings.
- Updated top-down impact fixture and tests.

### E. BMAD Packet Surface

- Added `skills/bmad-lens-setup/assets/lens/templates/bmad-packet.yaml`.
- Added top-down `bmad-packet.md` fixture.
- Reconciled top-down `bmad-packet.yaml` fixture with the Markdown packet.
- Validator and tests now require both Markdown and YAML packet surfaces.

### F. Doctor Auditing

- Broadened deterministic Doctor checks in `lens_artifact_ops.py`:
  - duplicate IDs
  - orphan references
  - missing or empty source refs
  - stale or needs-review records
  - missing ledger directories
  - untraced stories
  - unresolved promoted refs
  - relationship self-loops
  - missing relationship types
  - unresolved decisions
  - BMAD sync gaps
  - workstream impact gates
- Added regression coverage with a temporary anomaly fixture in `test_lens_artifact_ops.py`.
- Updated README, module guide, skill contracts, validation checklist, and evals.

### G. Fixtures

- Expanded top-down fixture folder:
  - `discovery-epoch.yaml`
  - `impact-map.yaml`
  - `bmad-packet.md`
  - `bmad-packet.yaml`
  - `story-guard.yaml`
  - existing slice, journey, story, validation result, and Salmon signal fixtures
- Preserved bottom-up slice-first fixture behavior for `slice.download_model_images`.
- Existing bottom-up adjacency and promotion gate continue to exercise repeated pressure without automatic promotion.

### H. Tests

- Extended `skills/bmad-lens-setup/assets/lens/scripts/tests/test_lens_artifact_ops.py`.
- Added setup-script tests:
  - `skills/bmad-lens-setup/scripts/tests/test_merge_config.py`
  - `skills/bmad-lens-setup/scripts/tests/test_merge_help_csv.py`
  - `skills/bmad-lens-setup/scripts/tests/test_cleanup_legacy.py`
- Covered anti-zombie help merge behavior, legacy fallback/default migration, module-help merge, cleanup idempotency, rich project-context init, impact graph projection, BMAD packet YAML validity, and Doctor anomaly categories.

### I. Evals And Docs

- Updated `skills/bmad-lens-setup/assets/lens/evals/lens-evals.yaml`.
- Updated `evals/lens/evals.json`.
- Updated `evals/lens/triggers.json`.
- Updated:
  - `README.md`
  - `skills/bmad-lens-setup/assets/lens/references/lens-module-guide.md`
  - `skills/bmad-lens-setup/assets/lens/references/skill-contracts.md`
  - `skills/bmad-lens-setup/assets/lens/schemas/validation-checklist.yaml`

## Validation Commands

All final validation commands passed:

```text
./.venv/bin/pytest skills/bmad-lens-setup/assets/lens/scripts/tests -q
6 passed in 0.53s

./.venv/bin/pytest skills/bmad-lens-setup/scripts/tests -q
3 passed in 0.08s

python3 .agents/skills/bmad-module-builder/scripts/validate-module.py skills
status: pass, total_findings: 0

./.venv/bin/python skills/bmad-lens-setup/assets/lens/scripts/validate_lens_assets.py --module-root .
status: pass, findings: []

./.venv/bin/python -m py_compile skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py skills/bmad-lens-setup/assets/lens/scripts/validate_lens_assets.py skills/bmad-lens-setup/scripts/merge-config.py skills/bmad-lens-setup/scripts/merge-help-csv.py skills/bmad-lens-setup/scripts/cleanup-legacy.py
pass

./.venv/bin/python -c "structured parser check"
structured parse ok 53

find . -type d -name '*NorthStarET*' -print
no output
```

Artifact smoke commands:

```text
./.venv/bin/python skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py init --project-root .
status: ok, directories: 31

./.venv/bin/python skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py map-rebuild --project-root .
status: ok, nodes: 17, relationships: 41, traceability: 2, warnings: 37

./.venv/bin/python skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py doctor --project-root .
status: ok, warnings: 37
warning types: workstream_impact_gate, duplicate_id, orphan_ref, unresolved_promoted_ref, unresolved_decision

./.venv/bin/python skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py auspex --project-root .
status: ok, active_slices: 2
```

Note: an earlier py_compile command referenced the wrong legacy path `skills/bmad-lens-setup/scripts/setup_lens_module.py`; the corrected compile command above passed.

## Assumptions

- `nextGoal.md` is the operative source of truth.
- `context.md` adds no extra requirements because it is empty.
- External BMAD workflow sequencing is documented and evaluated, while module-help `after` and `before` fields remain internal to satisfy BMAD Builder validation.

## Blockers

None.
