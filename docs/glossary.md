# LENS Glossary

## Slice

A small, useful, testable, end-to-end unit of work. A slice may be a utility, workflow step, journey segment, integration path, proof of concept, or feature-sized implementation. It can remain a slice forever.

When the term feels unfamiliar, use "thin work option" in explanations, but keep `slice` in source-truth IDs and artifacts.

## Top-Down

A LENS mode for a large ambiguous system idea. It starts with discovery and narrows toward one selected vertical slice before BMAD planning.

## Bottom-Up

A LENS mode for one useful thing. It starts with `slice.yaml` and grows only when repeated pressure justifies adjacency or promotion.

## Discovery Epoch

A bounded discovery pass that captures raw material, extracts hypotheses, challenges assumptions, and identifies what must be reviewed next.

## Candidate Slice Overview

A short list of possible slices from a top-down journey. It should identify the selected first slice, adjacent slices, deferred slices, and the next action for each.

## Discovery Next-Step Map

The handoff artifact created after top-down discovery. It explains the current gate, review order, candidate slice overview, and action queue.

## Journey

An end-to-end path across roles, evidence, decisions, system surfaces, and state changes. A journey can contain multiple candidate slices.

## Impact Map

A slice-specific map of affected workstreams, files, contracts, tests, observability, rollout controls, data or policy boundaries, and decisions.

## Context Gate

The readiness check before BMAD handoff. It can block PRD or architecture work when the slice, journey, decisions, or evidence are still weak.

## BMAD Packet

A focused handoff from LENS to BMAD. It includes only the active slice context needed for BMAD planning and excludes adjacent future slices or speculative architecture.

## Work Archive

The historical record of captures, extractions, sessions, validation results, BMAD packets, and Salmon signals.

## Living Landscape

The curated current understanding of systems, programs, domains, capabilities, services, journeys, workstreams, decisions, and risks.

## Derived Map

The generated graph projection rebuilt from source truth. It is not source truth and should not be hand-edited.

## Salmon

The upstream correction mechanism used when implementation reveals that an assumption, slice, journey, or BMAD plan no longer matches reality.
