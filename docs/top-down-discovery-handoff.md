# Top-Down Discovery Handoff

This guide exists to prevent the common failure mode where a top-down discovery pass creates many files but leaves the user unsure what to review next.

## Required Handoff Shape

Every top-down discovery pass should end with four human-readable sections.

1. Current gate: state whether the work is `not_ready`, `needs_review`, or `ready_for_bmad_packet`, and name the reason.
2. Review order: list the exact artifacts to review in the order that will answer the next decision.
3. Candidate slice overview: show the selected slice and adjacent slices as thin work options, with why each exists.
4. Action queue: list the next actions, owner, evidence needed, and output artifact.

Use `skills/bmad-lens-setup/assets/lens/templates/discovery-next-steps.md` as the handoff template.

## Review Order

Start with generated status, then move toward source truth.

1. Read `_bmad-output/lens/auspex/stakeholder-summary.md` for the short state of the Lens.
2. Read `_bmad-output/lens/graph/doctor-report.md` and `_bmad-output/lens/graph/warnings.yaml` for gates, topology issues, and unresolved decisions.
3. Read the selected slice `slice.md` and `slice.yaml` for scope, exclusions, acceptance evidence, and risks.
4. Read `impact-map.yaml` to confirm affected workstreams, files, contracts, tests, and decisions.
5. Read `context-sufficiency-*.md` and `context-score.yaml` to see whether BMAD packet preparation is allowed.
6. Read `journey.md` and `journey.yaml` to confirm the end-to-end path.
7. Read the system intent file and extraction file only when the slice or journey needs source context.

## Candidate Slice Overview

Use the term `slice` in source truth. When the user is still learning LENS, describe slices as thin work options.

Each candidate should answer:

- What starts the slice?
- What ends the slice?
- What acceptance evidence proves it?
- Why is this first, deferred, or adjacent?
- Which LENS skill should run next?

## Action Queue Examples

Common next actions after top-down discovery:

| Situation | Next action | Skill |
| --- | --- | --- |
| Scope is too broad | Move adjacent work to exclusions | `bmad-lens-slice-scope` |
| Review decision is pending | Human accepts, edits, or rejects the selected slice | `bmad-lens-context-check` after review |
| Impact is unclear | Map files, contracts, workstreams, and tests | `bmad-lens-analyze-impact` |
| Context gate blocks PRD | Capture more source material or run research | `bmad-lens-capture` or `bmad-lens-research-plan` |
| Slice is ready | Prepare focused BMAD input | `bmad-lens-prepare-bmad` |
