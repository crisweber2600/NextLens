# Discovery Next Steps

Use this after a top-down discovery pass so the handoff is action-oriented instead of a loose list of files.

## Current Gate

- Status: `not_ready|needs_review|ready_for_bmad_packet`
- Reason:
- Blocking decisions:
- Blocking questions:

## Review Order

1. Stakeholder status: `_bmad-output/lens/auspex/stakeholder-summary.md`
2. Topology checks: `_bmad-output/lens/graph/doctor-report.md` and `_bmad-output/lens/graph/warnings.yaml`
3. Selected slice: `_bmad-output/lens/slices/<slice-id>/slice.md` and `slice.yaml`
4. Impact map: `_bmad-output/lens/slices/<slice-id>/impact-map.yaml`
5. Context gate: `_bmad-output/lens/gates/context-sufficiency-*.md` and `context-score.yaml`
6. Journey: `_bmad-output/lens/journeys/<journey-id>/journey.md` and `journey.yaml`
7. System intent: `_bmad-output/lens/intent/<system-id>.yaml`
8. Extraction source: `_bmad-output/lens/archive/extractions/<extraction-id>.yaml`

## Candidate Slice Overview

| Candidate slice | Why it matters now | Starts with | Ends with | Required action | Next skill |
| --- | --- | --- | --- | --- | --- |
| `slice.example_first_path` | | | | review / narrow / defer / promote | `bmad-lens-slice-scope` |

Call these LENS slices in source truth. In human-facing text, describe them as "candidate slices" or "thin work options" when the term slice is still unfamiliar.

## Action Queue

| Priority | Action | Owner | Evidence needed | Output artifact |
| --- | --- | --- | --- | --- |
| 1 | Review selected slice scope and exclusions | human | accepted / changed scope notes | `slice.yaml` update |
| 2 | Resolve impact-map questions | human + LENS | affected files, contracts, workstreams | `impact-map.yaml` update |
| 3 | Re-run context check | LENS | reviewed slice and impact evidence | `context-score.yaml` |
| 4 | Prepare focused BMAD packet only if ready | LENS + BMAD | ready context gate | `bmad-packet.md`, `bmad-packet.yaml` |

## Deferred Or Adjacent Slices

| Slice | Relationship | Why deferred | Revisit when |
| --- | --- | --- | --- |
| `slice.example_adjacent_path` | adjacent_to | | |
