/goal

Work only in the repository crisweber2600/NextLens.

This repo is a BMAD Builder multi-skill module that implements the reimagined LENS framework. Do not create NorthStarET, do not scaffold an application, and do not assume any PDF, chat attachment, or external design file will be available. Treat this goal as the complete source of truth, supplemented only by the official BMAD docs below.

Authoritative conventions:
- BMAD Builder docs: https://bmad-builder-docs.bmad-method.org/llms-full.txt
- BMAD Method docs: https://docs.bmad-method.org/llms-full.txt

Core LENS model to preserve:
- LENS = Large-system Exploration, Navigation, Slicing, and validation framework.
- The central operating unit is the slice.
- Support two operating modes:
  - top-down discovery for large ambiguous system ideas
  - bottom-up slice growth for one useful thing without forcing platform/domain/capability creation
- LENS owns discovery, topology, traceability, validation, correction, and read-only visibility.
- BMAD owns PRD, UX, architecture, epics/stories, implementation, code review, and correct-course.
- Preserve source-truth separation:
  - archive = history / captured evidence / implementation history
  - landscape = current curated truth
  - graph = generated projection, rebuildable, never hand-edited
- No promotion without repeated pressure and human review.
- Related workstream impact must be explicit.
- Focused BMAD packet generation is required.
- Story guard, slice/journey/outcome validation, Salmon, Doctor, and Auspex are first-class module behavior.
- Keep the repo self-contained. Do not reintroduce any dependency on the original PDF.

Important constraints:
- Preserve the current multi-skill BMAD module shape.
- Preserve module code `lens`.
- Preserve existing user-facing skill directory names unless there is a compelling compatibility reason not to.
- Do not add a new application, service, or product scaffold.
- Do not inject NorthStarET-specific logic beyond generic fixture/example content already in the module.
- Prefer modifying and strengthening existing assets over creating parallel duplicates.
- Follow BMAD Builder packaging, registration, validation, and manifest conventions exactly.
- Follow BMAD Method phase ordering and project-context expectations exactly.

Repo-specific fixes to implement

A. Make the LENS gate behavior real in the help system
1. Update `skills/bmad-lens-setup/assets/module-help.csv`.
2. Make `bmad-lens-context-check` a real blocking gate for premature BMAD planning by using the BMAD Builder help-row semantics correctly.
3. Keep existing LENS sequencing, but also wire the relevant LENS bridge/correction steps into the parent BMAD workflow sequence through verified `before` / `after` references where official BMAD identifiers can be confirmed.
4. Do not guess parent BMAD identifiers. Resolve them from the official docs or from installed help rows if available in the environment.
5. Preserve existing menu codes unless a collision or clear correctness issue forces a change.

B. Reconcile schema, templates, fixtures, and validator rules
1. Normalize `skills/bmad-lens-setup/assets/lens/schemas/lens-entity.schema.json` so it covers the actual major artifact kinds and statuses used by the repo.
2. Ensure the schema and templates agree on kinds and metadata for:
   - discovery_epoch
   - slice
   - journey
   - relationship
   - impact_map
   - promotion_gate
   - validation_result
   - salmon_signal
   - BMAD packet artifacts
3. Reconcile status values so repo fixtures/templates are valid under the schema. If needed, separate base entity states from planning/working states in a clean, explicit way.
4. Add or fix required metadata in templates where it is missing, especially for:
   - `skills/bmad-lens-setup/assets/lens/templates/relationship.yaml`
   - `skills/bmad-lens-setup/assets/lens/templates/promotion-gate.yaml`
   - `skills/bmad-lens-setup/assets/lens/templates/story-guard.yaml`
   - `skills/bmad-lens-setup/assets/lens/templates/impact-map.yaml`
5. Strengthen `skills/bmad-lens-setup/assets/lens/scripts/validate_lens_assets.py` so it verifies semantic consistency, not just file presence. It should catch schema/template/fixture drift cleanly with actionable findings.
6. Prefer deriving skill inventory from the manifest and/or actual skills directory instead of relying only on a static hardcoded list where that improves long-term maintainability.

C. Fix fresh-project bootstrap so it creates the correct project context
1. Add a canonical LENS project-context template at one of these paths:
   - `skills/bmad-lens-setup/assets/lens/templates/project-context.md`
   - or a clearly named equivalent under `references/`
2. Update `skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py` so `init` writes that rich template when `_bmad-output/project-context.md` is absent.
3. The generated context file must include explicit rules for:
   - traceability
   - scope discipline
   - architecture update discipline
   - upstream change / Salmon behavior
   - archive / landscape / graph source-truth boundaries
4. Do not overwrite an existing project-context file unless the existing behavior already prompts or defers correctly.

D. Make related workstream impact visible in the generated graph
1. Extend `skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py` so `map-rebuild` projects `impact_map` artifacts into graph relationships and traceability.
2. Specifically support fields such as:
   - `active_slice`
   - `directly_impacted`
   - `possibly_conflicting`
   - `shared_files`
   - `shared_contracts`
   - `related_workstream_gate`
3. Create graph relationships and/or warnings that make related workstream detection visible to Doctor and Auspex.
4. Handle missing referenced impact targets cleanly by warning, not crashing.

E. Complete the BMAD bridge packet surface
1. Add `skills/bmad-lens-setup/assets/lens/templates/bmad-packet.yaml`.
2. Keep `skills/bmad-lens-setup/assets/lens/templates/bmad-packet.md`.
3. Ensure the markdown and YAML packet forms describe the same focused active-slice context:
   - active slice
   - optional top-down context
   - included scope
   - explicit exclusions
   - required capabilities
   - required decisions
   - risks
   - acceptance evidence
   - recommended BMAD next step
4. Update validator coverage so both packet forms are required.
5. Add at least one canonical top-down fixture packet in both formats.

F. Broaden Doctor so its implementation matches its documented contract
1. Extend Doctor’s deterministic auditing in `skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py`.
2. Add checks for at least:
   - missing or empty `source_refs` on key entities
   - duplicate IDs
   - orphan references
   - stale / needs_review freshness signals
   - missing ledger directories
   - untraced stories
   - unresolved promoted refs
   - obvious relationship anomalies where deterministically detectable
   - unresolved high-severity decision or BMAD-sync gaps where the repo already models those references
3. Keep Doctor deterministic-first. Do not invent vague LLM-only heuristics in the script.
4. Update docs so Doctor’s documented scope matches the implemented behavior exactly.

G. Expand fixtures so the module proves the full reimagined LENS flow
1. Add or enrich fixture files under:
   - `skills/bmad-lens-setup/assets/lens/fixtures/top-down/evidence-visible-to-teacher/`
   - `skills/bmad-lens-setup/assets/lens/fixtures/bottom-up/download-model-images/`
2. The top-down fixture set should include, at minimum:
   - discovery epoch example
   - impact map example
   - BMAD packet in markdown and YAML
   - story guard example
   - validation result example
   - salmon signal example
3. Keep the bottom-up fixture a true slice-first example that does not force system/domain/capability creation by default.
4. Ensure fixtures exercise:
   - repeated-pressure promotion
   - workstream impact
   - traceability
   - Doctor warnings
   - Auspex output
5. Do not add filler fixtures. Every fixture must prove some behavior used by scripts, evaluator inputs, or docs.

H. Add missing tests around registration and strengthened artifact behavior
1. Keep and extend:
   - `skills/bmad-lens-setup/assets/lens/scripts/tests/test_lens_artifact_ops.py`
   - `skills/bmad-lens-setup/assets/lens/scripts/tests/test_validate_lens_assets.py`
2. Add setup-script tests under:
   - `skills/bmad-lens-setup/scripts/tests/test_merge_config.py`
   - `skills/bmad-lens-setup/scripts/tests/test_merge_help_csv.py`
   - `skills/bmad-lens-setup/scripts/tests/test_cleanup_legacy.py`
3. Cover at least:
   - anti-zombie replacement behavior
   - legacy config fallback/default migration
   - module-help merge behavior
   - safe cleanup/idempotency
   - `init` creating the richer project-context scaffold
   - graph rebuild consuming impact-map relationships
   - BMAD packet YAML presence and validity
   - Doctor detecting at least one newly added deterministic audit category

I. Update eval inputs and documentation so the repo explains and proves the improved behavior
1. Update:
   - `skills/bmad-lens-setup/assets/lens/evals/lens-evals.yaml`
   - `evals/lens/evals.json`
   - `evals/lens/triggers.json`
2. Add or refine eval coverage for:
   - context sufficiency as a real gate
   - focused BMAD packet in both formats
   - related workstream impact detection
   - project-context initialization
   - Doctor warnings on richer invalid-topology cases
3. Update docs as needed so the repo stays self-describing:
   - `README.md`
   - `skills/bmad-lens-setup/assets/lens/references/lens-module-guide.md`
   - `skills/bmad-lens-setup/assets/lens/references/skill-contracts.md`

Definition of done
- The repository remains a BMAD Builder multi-skill module with the current LENS skill surface.
- No new app scaffold or NorthStarET implementation is created.
- `validate_lens_assets.py` passes cleanly.
- The repo still validates as a BMAD module under the BMAD Builder validator.
- `lens_artifact_ops.py init` scaffolds a rich `project-context.md` when needed.
- `map-rebuild` projects impact-map/workstream relationships into graph outputs.
- Doctor checks are broader and tested.
- Both BMAD packet formats exist and are validated.
- Fixtures and evals cover the strengthened behavior.
- README and reference docs accurately describe what the repo now does.
- No placeholders, ellipses, or pseudo-templates remain in tracked assets.

Validation commands to run before finishing
- `python3 .agents/skills/bmad-module-builder/scripts/validate-module.py skills`
- `python3 skills/bmad-lens-setup/assets/lens/scripts/validate_lens_assets.py --module-root .`
- `pytest skills/bmad-lens-setup/assets/lens/scripts/tests -q`
- `pytest skills/bmad-lens-setup/scripts/tests -q`
- `python3 skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py init --project-root .`
- `python3 skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py map-rebuild --project-root .`
- `python3 skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py doctor --project-root .`
- `python3 skills/bmad-lens-setup/assets/lens/scripts/lens_artifact_ops.py auspex --project-root .`

Output expectations
- Produce the actual repo changes only.
- Keep changes narrowly scoped to the gaps above.
- If a convention is ambiguous, prefer the official BMAD Builder docs for packaging/registration and the official BMAD Method docs for phase and project-context behavior.
