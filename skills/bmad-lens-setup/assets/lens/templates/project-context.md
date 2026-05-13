# Project Context for AI Agents

## LENS Module Active

This project uses the LENS module for BMAD-native discovery, slice orchestration, topology management, traceability, validation, upstream correction, and read-only visibility.

## Traceability Rule

Every BMAD story must trace to an active LENS slice.

For top-down work, trace:

system -> role -> outcome -> journey -> slice -> capability -> acceptance evidence

For bottom-up work, trace at minimum:

slice -> artifact -> acceptance evidence

## Scope Rule

Do not expand the active slice into adjacent future work unless a LENS Salmon signal, promotion decision, or BMAD correct-course decision changes the plan.

## Architecture Rule

Architecture decisions must update the relevant LENS capability, domain, service, decision, or risk ledger when those ledgers exist. Do not invent new capability, domain, or service ledgers without repeated pressure.

## Upstream Change Rule

If implementation reveals that an upstream assumption is wrong, raise a LENS Salmon signal before silently changing architecture, scope, or acceptance criteria.

## Source Truth Rule

Archive records history and captured evidence. Landscape records current curated truth. Graph records generated projections and must not be hand-edited.
