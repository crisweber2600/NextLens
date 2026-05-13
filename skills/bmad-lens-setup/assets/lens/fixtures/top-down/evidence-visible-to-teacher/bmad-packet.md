# LENS BMAD Packet

## Metadata

- Packet ID: `bmad_packet.evidence_visible_to_teacher`
- Active Slice: `slice.evidence_visible_to_teacher`
- Status: `approved`
- Validity: `current`
- Source Refs: `fixture.top_down.learning_improvement`

## Slice Goal

Teacher can view a student evidence artifact with source metadata.

## Optional Top-Down Context

- System: `system.learning_improvement_platform`
- Role: `role.teacher`
- Outcome: `outcome.teacher_turns_evidence_into_action`
- Journey: `journey.evidence_to_teacher_action`
- Why First: Establish evidence object, visibility rule, and teacher workspace before AI interpretation or coaching rollups.

## Included Scope

- Evidence artifact visibility
- Source metadata
- Timestamp or freshness display
- Role-based visibility check
- Safe missing state

## Explicitly Out Of Scope

- AI interpretation
- Goal alignment
- Next-action guidance
- Coaching dashboards
- District analytics
- Family portal

## Required Capabilities

- `capability.evidence_artifact_model`
- `capability.evidence_source_metadata`
- `capability.teacher_workspace`
- `capability.role_based_visibility`

## Required Decisions

- `decision.teacher_access_policy`

## Risks

- `risk.student_privacy`
- `risk.teacher_surveillance`

## Acceptance Evidence

- Permitted teacher can open evidence artifact.
- Artifact source is visible.
- Artifact timestamp is visible.
- Unauthorized teacher cannot access artifact.
- Missing artifact renders safe empty state.

## Recommended BMAD Next Step

- `bmad-create-prd`
