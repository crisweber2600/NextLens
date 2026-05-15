"""Pluggable non-mutating doctor check framework for NextLens."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence


DOCTOR_CATEGORIES = frozenset({"schema", "scope", "traceability", "readiness"})
DOCTOR_SEVERITIES = frozenset({"blocking", "advisory", "informational"})
DOCTOR_STATUSES = frozenset({"pass", "warning", "fail"})


@dataclass(frozen=True)
class DoctorCheckContext:
    landscape_state: Any
    derived_graph: Mapping[str, Any]
    packet_candidate: Mapping[str, Any] | None = None
    selected_feature: Mapping[str, Any] | None = None

    def read_only(self) -> "DoctorCheckContext":
        return DoctorCheckContext(
            landscape_state=self.landscape_state,
            derived_graph=_freeze_mapping(self.derived_graph),
            packet_candidate=_freeze_mapping(self.packet_candidate or {}),
            selected_feature=_freeze_mapping(self.selected_feature or {}),
        )


@dataclass(frozen=True)
class DoctorCheckResult:
    status: str
    severity: str
    message: str
    references: tuple[str, ...] = field(default_factory=tuple)
    remediation: str = ""

    def __post_init__(self) -> None:
        if self.status not in DOCTOR_STATUSES:
            raise ValueError(f"Unsupported doctor status '{self.status}'.")
        if self.severity not in DOCTOR_SEVERITIES:
            raise ValueError(f"Unsupported doctor severity '{self.severity}'.")

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "references": list(self.references),
            "remediation": self.remediation,
        }


@dataclass(frozen=True)
class DoctorCheck:
    check_id: str
    name: str
    category: str
    severity: str
    description: str
    remediation: str
    execute: Callable[[DoctorCheckContext], DoctorCheckResult]

    def __post_init__(self) -> None:
        if not self.check_id.strip():
            raise ValueError("Doctor check requires a stable check_id.")
        if self.category not in DOCTOR_CATEGORIES:
            raise ValueError(f"Unsupported doctor category '{self.category}'.")
        if self.severity not in DOCTOR_SEVERITIES:
            raise ValueError(f"Unsupported doctor severity '{self.severity}'.")
        if not callable(self.execute):
            raise ValueError("Doctor check requires an execute function.")


@dataclass(frozen=True)
class DoctorExecutionLogEntry:
    check_id: str
    started_at: str
    completed_at: str
    status: str

    def to_payload(self) -> dict[str, str]:
        return {
            "checkId": self.check_id,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
            "status": self.status,
        }


@dataclass(frozen=True)
class DoctorRunResult:
    results: tuple[DoctorCheckResult, ...]
    blocking_results: tuple[DoctorCheckResult, ...]
    advisory_results: tuple[DoctorCheckResult, ...]
    informational_results: tuple[DoctorCheckResult, ...]
    execution_log: tuple[DoctorExecutionLogEntry, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "results": [result.to_payload() for result in self.results],
            "blockingResults": [result.to_payload() for result in self.blocking_results],
            "advisoryResults": [result.to_payload() for result in self.advisory_results],
            "informationalResults": [result.to_payload() for result in self.informational_results],
            "executionLog": [entry.to_payload() for entry in self.execution_log],
        }


class DoctorCheckRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, DoctorCheck] = {}

    def register(self, check: DoctorCheck) -> None:
        if check.check_id in self._checks:
            raise ValueError(f"Doctor check '{check.check_id}' is already registered.")
        self._checks[check.check_id] = check

    def list_checks(self) -> tuple[DoctorCheck, ...]:
        return tuple(self._checks[check_id] for check_id in sorted(self._checks))

    def run_all(self, context: DoctorCheckContext) -> DoctorRunResult:
        read_only_context = context.read_only()
        results: list[DoctorCheckResult] = []
        execution_log: list[DoctorExecutionLogEntry] = []

        for check in self.list_checks():
            started_at = _utc_timestamp()
            result = check.execute(read_only_context)
            completed_at = _utc_timestamp()
            if result.severity != check.severity:
                result = DoctorCheckResult(
                    status=result.status,
                    severity=check.severity,
                    message=result.message,
                    references=result.references,
                    remediation=result.remediation or check.remediation,
                )
            results.append(result)
            execution_log.append(
                DoctorExecutionLogEntry(
                    check_id=check.check_id,
                    started_at=started_at,
                    completed_at=completed_at,
                    status=result.status,
                )
            )

        return DoctorRunResult(
            results=tuple(results),
            blocking_results=tuple(result for result in results if result.severity == "blocking"),
            advisory_results=tuple(result for result in results if result.severity == "advisory"),
            informational_results=tuple(result for result in results if result.severity == "informational"),
            execution_log=tuple(execution_log),
        )


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    frozen: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, Mapping):
            frozen[key] = _freeze_mapping(item)
        elif isinstance(item, list):
            frozen[key] = tuple(_freeze_mapping(child) if isinstance(child, Mapping) else child for child in item)
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            frozen[key] = tuple(item)
        else:
            frozen[key] = item
    return MappingProxyType(frozen)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
