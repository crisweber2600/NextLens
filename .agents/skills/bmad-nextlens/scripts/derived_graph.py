"""Canonical derived graph schema for NextLens landscape projections."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


DERIVED_GRAPH_SCHEMA_VERSION = "1.0"
DERIVED_GRAPH_NODE_TYPES = (
    "system",
    "role",
    "outcome",
    "journey",
    "operating_loop",
    "capability",
    "decision",
    "risk",
    "feature",
)
DERIVED_GRAPH_NODE_PROPERTIES = ("id", "type", "label", "metadata")
DERIVED_GRAPH_EDGE_PROPERTIES = ("source", "target", "type", "label", "metadata")


@dataclass(frozen=True)
class DerivedGraphEdgeType:
    type: str
    source_type: str
    target_type: str
    label: str

    def to_payload(self) -> dict[str, str]:
        return {
            "type": self.type,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "label": self.label,
        }


DERIVED_GRAPH_EDGE_TYPES = (
    DerivedGraphEdgeType(
        type="system_role",
        source_type="system",
        target_type="role",
        label="system requires role participation",
    ),
    DerivedGraphEdgeType(
        type="role_outcome",
        source_type="role",
        target_type="outcome",
        label="role achieves outcome",
    ),
    DerivedGraphEdgeType(
        type="outcome_journey",
        source_type="outcome",
        target_type="journey",
        label="outcome fulfilled by journey",
    ),
    DerivedGraphEdgeType(
        type="journey_operating_loop",
        source_type="journey",
        target_type="operating_loop",
        label="journey contains operating loop",
    ),
    DerivedGraphEdgeType(
        type="operating_loop_capability",
        source_type="operating_loop",
        target_type="capability",
        label="operating loop uses capability",
    ),
    DerivedGraphEdgeType(
        type="capability_decision",
        source_type="capability",
        target_type="decision",
        label="decision governs capability",
    ),
    DerivedGraphEdgeType(
        type="feature_journey",
        source_type="feature",
        target_type="journey",
        label="feature proves journey",
    ),
    DerivedGraphEdgeType(
        type="feature_outcome",
        source_type="feature",
        target_type="outcome",
        label="feature proves outcome",
    ),
)


@dataclass(frozen=True)
class DerivedGraphNode:
    id: str
    type: str
    label: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DerivedGraphEdge:
    source: str
    target: str
    type: str
    label: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "label": self.label,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DerivedGraphSchema:
    version: str = DERIVED_GRAPH_SCHEMA_VERSION

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "nodes": {
                "types": list(DERIVED_GRAPH_NODE_TYPES),
                "properties": list(DERIVED_GRAPH_NODE_PROPERTIES),
            },
            "edges": {
                "types": [edge_type.to_payload() for edge_type in DERIVED_GRAPH_EDGE_TYPES],
                "properties": list(DERIVED_GRAPH_EDGE_PROPERTIES),
            },
        }


def build_graph_schema() -> DerivedGraphSchema:
    return DerivedGraphSchema()


def make_graph_node(
    node_id: str,
    node_type: str,
    label: str,
    metadata: Mapping[str, Any] | None = None,
) -> DerivedGraphNode:
    if node_type not in DERIVED_GRAPH_NODE_TYPES:
        raise ValueError(f"Unsupported derived graph node type '{node_type}'.")
    return DerivedGraphNode(id=node_id, type=node_type, label=label, metadata=metadata or {})


def make_graph_edge(
    source: str,
    target: str,
    edge_type: str,
    metadata: Mapping[str, Any] | None = None,
) -> DerivedGraphEdge:
    edge_definition = next((item for item in DERIVED_GRAPH_EDGE_TYPES if item.type == edge_type), None)
    if edge_definition is None:
        raise ValueError(f"Unsupported derived graph edge type '{edge_type}'.")
    return DerivedGraphEdge(
        source=source,
        target=target,
        type=edge_definition.type,
        label=edge_definition.label,
        metadata=metadata or {},
    )