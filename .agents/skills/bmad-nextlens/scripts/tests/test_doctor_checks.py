from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).resolve().parent.parent / "doctor_checks.py"
SPEC = importlib.util.spec_from_file_location("nextlens_doctor_checks", MODULE_PATH)
DOCTOR = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = DOCTOR
SPEC.loader.exec_module(DOCTOR)


def test_registers_check_with_required_metadata() -> None:
    registry = DOCTOR.DoctorCheckRegistry()
    check = _check("schema.entities")

    registry.register(check)

    assert registry.list_checks() == (check,)
    assert check.check_id == "schema.entities"
    assert check.category == "schema"
    assert check.severity == "blocking"
    assert check.description
    assert check.remediation


def test_rejects_duplicate_check_registration() -> None:
    registry = DOCTOR.DoctorCheckRegistry()
    registry.register(_check("schema.entities"))

    try:
        registry.register(_check("schema.entities"))
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("expected duplicate check registration to fail")


def test_executes_checks_with_read_only_context_and_collects_by_severity() -> None:
    registry = DOCTOR.DoctorCheckRegistry()
    calls: list[DOCTOR.DoctorCheckContext] = []

    def execute(context: DOCTOR.DoctorCheckContext) -> DOCTOR.DoctorCheckResult:
        calls.append(context)
        try:
            context.derived_graph["nodes"] = []
        except TypeError:
            pass
        else:
            raise AssertionError("derived graph context must be read-only")
        return DOCTOR.DoctorCheckResult(
            status="fail",
            severity="blocking",
            message="Graph is missing required nodes.",
            references=("graph.json",),
            remediation="Rebuild graph.",
        )

    registry.register(
        DOCTOR.DoctorCheck(
            check_id="schema.graph_nodes",
            name="Graph nodes exist",
            category="schema",
            severity="blocking",
            description="Validates graph node presence.",
            remediation="Rebuild graph.",
            execute=execute,
        )
    )
    context = DOCTOR.DoctorCheckContext(
        landscape_state=object(),
        derived_graph={"nodes": [{"id": "system-nextlens"}]},
        packet_candidate={"featureId": "feature-1"},
        selected_feature={"id": "feature-1"},
    )

    result = registry.run_all(context)

    assert len(calls) == 1
    assert result.blocking_results[0].status == "fail"
    assert result.advisory_results == ()
    assert result.informational_results == ()
    assert result.execution_log[0].check_id == "schema.graph_nodes"
    assert result.execution_log[0].started_at
    assert result.execution_log[0].completed_at


def test_result_payload_uses_standard_shape() -> None:
    result = DOCTOR.DoctorCheckResult(
        status="warning",
        severity="advisory",
        message="Orphaned node found.",
        references=("risk-unused",),
        remediation="Connect or remove the orphaned entity.",
    )

    assert result.to_payload() == {
        "status": "warning",
        "severity": "advisory",
        "message": "Orphaned node found.",
        "references": ["risk-unused"],
        "remediation": "Connect or remove the orphaned entity.",
    }


def _check(check_id: str) -> DOCTOR.DoctorCheck:
    return DOCTOR.DoctorCheck(
        check_id=check_id,
        name="Entity schema",
        category="schema",
        severity="blocking",
        description="Validates entity schema.",
        remediation="Fix entity schema.",
        execute=lambda _context: DOCTOR.DoctorCheckResult(
            status="pass",
            severity="blocking",
            message="Entity schema is valid.",
            references=(),
            remediation="",
        ),
    )
