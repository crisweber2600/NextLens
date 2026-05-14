# LENS Flows

LENS supports two entry points: top-down discovery for a large ambiguous system, and bottom-up growth for one useful thing. Both flows should end in reviewable artifacts and an explicit next action, not a vague recommendation to keep exploring.

## Top-Down Discovery

Use top-down discovery when the request starts with a broad system idea, a pile of documents, or a source tree that needs to be understood before BMAD planning.

Expected action chain:

```text
ambiguous request
-> discovery epoch
-> raw capture
-> extracted hypotheses
-> challenged assumptions
-> roles, stakeholders, outcomes, and loops
-> journey map
-> candidate slice overview
-> selected vertical slice
-> impact map
-> context sufficiency gate
-> discovery next-step map
-> focused BMAD packet only when ready
```

The important behavior is the handoff. After discovery, the agent should say what to review, what decisions are blocking, which candidate slices exist, which slice is selected first, and what action should happen next.

Minimum top-down handoff outputs:

- `stakeholder-summary.md`: readable status from Auspex.
- `doctor-report.md` and `warnings.yaml`: topology and gate issues.
- `journey.yaml` and `journey.md`: the path through roles, evidence, decisions, and state changes.
- `slice.yaml` and optional `slice.md`: the selected thin vertical path.
- `impact-map.yaml`: affected workstreams, files, contracts, tests, and decisions.
- `context-score.yaml` and `context-sufficiency-*.md`: readiness for BMAD handoff.
- `discovery-next-steps.md`: review order, action queue, and candidate slice overview.

Top-down discovery must not jump directly to PRD, architecture, or epics. BMAD planning starts only after the active slice is focused, impact is understood, and the context gate is ready or explicitly accepted by the user.

## Bottom-Up Growth

Use bottom-up growth when the request starts with one useful thing. The first artifact is a slice, not a platform.

Expected action chain:

```text
small useful thing
-> slice.yaml
-> optional local artifact
-> optional adjacency to another slice
-> repeated pressure report
-> optional promotion gate
-> BMAD execution only when the slice needs formal planning or implementation
```

A bottom-up slice can remain complete forever. It does not need a system, domain, service, capability, program, initiative, or roadmap. Promotion requires repeated evidence and human review.

Bottom-up outputs usually stay smaller:

- `slice.yaml`: goal, scope, exclusions, acceptance evidence, risks, produced and consumed artifacts.
- `slice.md`: optional human summary.
- `adjacency.yaml`: only when another slice is genuinely related.
- `promotion-gate.yaml`: only when repeated pressure suggests a capability candidate.

## Shared Rule

In both flows, source truth lives in LENS artifacts and generated status lives in the graph or Auspex folders. Do not hand-edit Derived Map outputs. Rebuild them from source truth.
