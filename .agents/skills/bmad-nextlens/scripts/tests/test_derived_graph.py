from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).resolve().parent.parent / "derived_graph.py"
SPEC = importlib.util.spec_from_file_location("nextlens_derived_graph", MODULE_PATH)
DERIVED_GRAPH = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = DERIVED_GRAPH
SPEC.loader.exec_module(DERIVED_GRAPH)


def test_build_graph_schema_exposes_required_node_types_and_properties() -> None:
    schema = DERIVED_GRAPH.build_graph_schema().to_payload()

    assert schema["version"] == "1.0"
    assert set(
        [
            "system",
            "role",
            "outcome",
            "journey",
            "operating_loop",
            "capability",
            "decision",
            "risk",
        ]
    ).issubset(set(schema["nodes"]["types"]))
    assert schema["nodes"]["properties"] == ["id", "type", "label", "metadata"]


def test_build_graph_schema_exposes_required_edge_types_and_properties() -> None:
    schema = DERIVED_GRAPH.build_graph_schema().to_payload()
    edge_types = {item["type"]: item for item in schema["edges"]["types"]}

    assert edge_types["system_role"] == {
        "type": "system_role",
        "source_type": "system",
        "target_type": "role",
        "label": "system requires role participation",
    }
    assert edge_types["role_outcome"]["target_type"] == "outcome"
    assert edge_types["outcome_journey"]["target_type"] == "journey"
    assert edge_types["journey_operating_loop"]["target_type"] == "operating_loop"
    assert edge_types["operating_loop_capability"]["target_type"] == "capability"
    assert edge_types["capability_decision"]["target_type"] == "decision"
    assert edge_types["feature_journey"]["target_type"] == "journey"
    assert edge_types["feature_outcome"]["target_type"] == "outcome"
    assert schema["edges"]["properties"] == ["source", "target", "type", "label", "metadata"]


def test_make_graph_node_returns_required_node_shape() -> None:
    node = DERIVED_GRAPH.make_graph_node(
        "role-system-architect",
        "role",
        "System Architect",
        {"source": "landscape", "status": "active"},
    )

    assert node.to_payload() == {
        "id": "role-system-architect",
        "type": "role",
        "label": "System Architect",
        "metadata": {"source": "landscape", "status": "active"},
    }


def test_make_graph_edge_returns_required_edge_shape() -> None:
    edge = DERIVED_GRAPH.make_graph_edge(
        "system-nextlens",
        "role-system-architect",
        "system_role",
        {"source_relationship": "systemId"},
    )

    assert edge.to_payload() == {
        "source": "system-nextlens",
        "target": "role-system-architect",
        "type": "system_role",
        "label": "system requires role participation",
        "metadata": {"source_relationship": "systemId"},
    }


def test_make_graph_node_rejects_unknown_node_type() -> None:
    try:
        DERIVED_GRAPH.make_graph_node("unknown-1", "unknown", "Unknown")
    except ValueError as exc:
        assert "Unsupported derived graph node type" in str(exc)
    else:  # pragma: no cover - defensive check in direct module test
        raise AssertionError("expected ValueError for unsupported node type")


def test_make_graph_edge_rejects_unknown_edge_type() -> None:
    try:
        DERIVED_GRAPH.make_graph_edge("source", "target", "unknown_edge")
    except ValueError as exc:
        assert "Unsupported derived graph edge type" in str(exc)
    else:  # pragma: no cover - defensive check in direct module test
        raise AssertionError("expected ValueError for unsupported edge type")