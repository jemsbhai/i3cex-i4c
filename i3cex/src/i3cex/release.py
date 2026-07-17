"""Machine-checkable release-readiness manifests for I3C-EX.

The project deliberately separates a development package being buildable
from a protocol release being ready for hardware or production use.  This
module validates the release manifest and exposes the blockers for each
milestone without silently treating missing evidence as success.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "Gate",
    "HardwareRequirement",
    "ManifestError",
    "ReadinessReport",
    "load_readiness_manifest",
]

_MILESTONES: Final[frozenset[str]] = frozenset({"dev", "rc", "production"})
_GATE_STATUSES: Final[frozenset[str]] = frozenset(
    {"blocked", "not_applicable", "passed", "pending"}
)
_HARDWARE_STATUSES: Final[frozenset[str]] = frozenset(
    {"available", "connected", "needed", "optional", "validated"}
)
_DECISIONS: Final[frozenset[str]] = frozenset({"GO", "NO-GO"})


class ManifestError(ValueError):
    """Raised when a release-readiness manifest is invalid or contradictory."""


@dataclass(frozen=True)
class Gate:
    """One evidence-backed release gate."""

    id: str
    name: str
    status: str
    required_for: tuple[str, ...]
    evidence: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class HardwareRequirement:
    """One physical item required by a release milestone."""

    id: str
    model: str
    quantity: int
    role: str
    required_for: tuple[str, ...]
    availability: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class ReadinessReport:
    """Validated readiness state for the planned release train."""

    schema_version: int
    updated: str
    decision: str
    decision_reason: str
    development_version: str
    hardware_candidate_version: str
    hardware_validated_version: str
    production_version: str
    gates: tuple[Gate, ...]
    hardware: tuple[HardwareRequirement, ...]

    def blocking_gates(self, milestone: str) -> tuple[Gate, ...]:
        """Return required gates that have not passed for ``milestone``."""
        _validate_milestone(milestone)
        return tuple(
            gate
            for gate in self.gates
            if milestone in gate.required_for and gate.status != "passed"
        )

    def blocking_hardware(self, milestone: str) -> tuple[HardwareRequirement, ...]:
        """Return required hardware that lacks retained validation evidence."""
        _validate_milestone(milestone)
        return tuple(
            item
            for item in self.hardware
            if milestone in item.required_for and item.availability != "validated"
        )

    def is_ready(self, milestone: str) -> bool:
        """Return whether every gate and hardware item for a milestone passed."""
        return not self.blocking_gates(milestone) and not self.blocking_hardware(milestone)

    def version_for(self, milestone: str) -> str:
        """Return the planned version corresponding to a milestone."""
        _validate_milestone(milestone)
        if milestone == "dev":
            return self.development_version
        if milestone == "rc":
            return self.hardware_candidate_version
        return self.production_version


def _validate_milestone(milestone: str) -> None:
    if milestone not in _MILESTONES:
        allowed = ", ".join(sorted(_MILESTONES))
        raise ManifestError(f"Unknown milestone {milestone!r}; expected one of: {allowed}")


def _require_mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ManifestError(f"{field} MUST be an object")
    return cast("dict[str, object]", value)


def _require_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ManifestError(f"{field} MUST be an array")
    return cast("list[object]", value)


def _require_str(mapping: dict[str, object], field: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field} MUST be a non-empty string")
    return value


def _require_int(mapping: dict[str, object], field: str) -> int:
    value = mapping.get(field)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ManifestError(f"{field} MUST be an integer")
    return value


def _require_str_tuple(mapping: dict[str, object], field: str) -> tuple[str, ...]:
    values = _require_list(mapping.get(field), field)
    result: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ManifestError(f"{field}[{index}] MUST be a non-empty string")
        result.append(value)
    return tuple(result)


def _validate_milestones(values: tuple[str, ...], field: str) -> None:
    unknown = set(values) - _MILESTONES
    if unknown:
        rendered = ", ".join(sorted(unknown))
        raise ManifestError(f"{field} contains unknown milestones: {rendered}")
    if len(values) != len(set(values)):
        raise ManifestError(f"{field} MUST NOT contain duplicates")


def _validate_evidence_reference(reference: str, package_root: Path, field: str) -> None:
    if reference.startswith(("https://", "http://")):
        return
    evidence_path = package_root / reference
    if not evidence_path.is_file():
        raise ManifestError(f"{field} references missing evidence file: {reference}")


def _parse_gate(raw: object, package_root: Path, index: int) -> Gate:
    data = _require_mapping(raw, f"gates[{index}]")
    prefix = f"gates[{index}]"
    gate_id = _require_str(data, "id")
    name = _require_str(data, "name")
    status = _require_str(data, "status")
    if status not in _GATE_STATUSES:
        raise ManifestError(f"{prefix}.status has unsupported value {status!r}")

    required_for = _require_str_tuple(data, "required_for")
    _validate_milestones(required_for, f"{prefix}.required_for")
    evidence = _require_str_tuple(data, "evidence")
    blockers = _require_str_tuple(data, "blockers")

    if status == "passed" and not evidence:
        raise ManifestError(f"{prefix} is passed but has no evidence")
    if status == "blocked" and not blockers:
        raise ManifestError(f"{prefix} is blocked but names no blockers")
    if status == "not_applicable" and required_for:
        raise ManifestError(f"{prefix} is not_applicable but is required by a milestone")

    for evidence_index, reference in enumerate(evidence):
        _validate_evidence_reference(
            reference,
            package_root,
            f"{prefix}.evidence[{evidence_index}]",
        )

    return Gate(
        id=gate_id,
        name=name,
        status=status,
        required_for=required_for,
        evidence=evidence,
        blockers=blockers,
    )


def _parse_hardware(raw: object, package_root: Path, index: int) -> HardwareRequirement:
    data = _require_mapping(raw, f"hardware[{index}]")
    prefix = f"hardware[{index}]"
    item_id = _require_str(data, "id")
    model = _require_str(data, "model")
    quantity = _require_int(data, "quantity")
    if quantity < 1:
        raise ManifestError(f"{prefix}.quantity MUST be at least 1")
    role = _require_str(data, "role")
    required_for = _require_str_tuple(data, "required_for")
    _validate_milestones(required_for, f"{prefix}.required_for")
    availability = _require_str(data, "availability")
    if availability not in _HARDWARE_STATUSES:
        raise ManifestError(f"{prefix}.availability has unsupported value {availability!r}")
    if availability == "optional" and required_for:
        raise ManifestError(f"{prefix} is optional but is required by a milestone")
    evidence = _require_str_tuple(data, "evidence")
    if availability == "validated" and not evidence:
        raise ManifestError(f"{prefix} is validated but has no evidence")
    for evidence_index, reference in enumerate(evidence):
        _validate_evidence_reference(
            reference,
            package_root,
            f"{prefix}.evidence[{evidence_index}]",
        )
    return HardwareRequirement(
        id=item_id,
        model=model,
        quantity=quantity,
        role=role,
        required_for=required_for,
        availability=availability,
        evidence=evidence,
    )


def _reject_duplicate_ids(
    items: tuple[Gate, ...] | tuple[HardwareRequirement, ...],
    field: str,
) -> None:
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ManifestError(f"{field} IDs MUST be unique")


def load_readiness_manifest(path: Path) -> ReadinessReport:
    """Load and validate a release-readiness JSON manifest.

    Local evidence paths are resolved relative to the package root, which
    is the parent directory of the manifest's ``release/`` directory.
    """
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"Release manifest does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Release manifest is not valid JSON: {exc}") from exc

    data = _require_mapping(raw, "manifest")
    schema_version = _require_int(data, "schema_version")
    if schema_version != 1:
        raise ManifestError(f"Unsupported schema_version {schema_version}; expected 1")

    updated = _require_str(data, "updated")
    decision = _require_str(data, "decision")
    if decision not in _DECISIONS:
        raise ManifestError(f"decision has unsupported value {decision!r}")
    decision_reason = _require_str(data, "decision_reason")

    release = _require_mapping(data.get("release"), "release")
    package_root = path.parent.parent
    gates = tuple(
        _parse_gate(item, package_root, index)
        for index, item in enumerate(_require_list(data.get("gates"), "gates"))
    )
    hardware = tuple(
        _parse_hardware(item, package_root, index)
        for index, item in enumerate(_require_list(data.get("hardware"), "hardware"))
    )
    if not gates:
        raise ManifestError("gates MUST contain at least one release gate")
    _reject_duplicate_ids(gates, "gate")
    _reject_duplicate_ids(hardware, "hardware")

    report = ReadinessReport(
        schema_version=schema_version,
        updated=updated,
        decision=decision,
        decision_reason=decision_reason,
        development_version=_require_str(release, "development"),
        hardware_candidate_version=_require_str(release, "hardware_candidate"),
        hardware_validated_version=_require_str(release, "hardware_validated"),
        production_version=_require_str(release, "production"),
        gates=gates,
        hardware=hardware,
    )
    if decision == "GO" and not report.is_ready("production"):
        raise ManifestError("decision is GO while production gates or hardware remain blocked")
    return report
