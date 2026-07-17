from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import cast

import pytest

from i3cex.release import ManifestError, load_readiness_manifest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = PACKAGE_ROOT / "release" / "readiness-v0.1.0.json"


def _base_manifest() -> dict[str, object]:
    raw: object = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return cast("dict[str, object]", raw)


def _write_manifest(tmp_path: Path, data: object) -> Path:
    manifest_path = tmp_path / "release" / "readiness.json"
    manifest_path.parent.mkdir(parents=True)
    evidence = tmp_path / "docs" / "release" / "RELEASE_PLAN.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("release plan\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    return manifest_path


def _mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _list(value: object) -> list[object]:
    assert isinstance(value, list)
    return value


def _gate(data: dict[str, object], index: int) -> dict[str, object]:
    return _mapping(_list(data["gates"])[index])


def _hardware(data: dict[str, object], index: int) -> dict[str, object]:
    return _mapping(_list(data["hardware"])[index])


def test_repository_manifest_reports_truthful_blockers() -> None:
    report = load_readiness_manifest(MANIFEST)

    assert report.schema_version == 1
    assert report.decision == "NO-GO"
    assert report.version_for("dev") == "0.1.0.dev1"
    assert report.version_for("rc") == "0.1.0rc1"
    assert report.version_for("production") == "1.0.0"
    assert [gate.id for gate in report.blocking_gates("dev")] == ["G01", "G02"]
    assert "G03" in {gate.id for gate in report.blocking_gates("rc")}
    assert "programmable-i3c-pair" in {item.id for item in report.blocking_hardware("rc")}
    assert not report.is_ready("dev")
    assert not report.is_ready("rc")
    assert not report.is_ready("production")


@pytest.mark.parametrize("method", ["blocking_gates", "blocking_hardware", "version_for"])
def test_unknown_milestone_is_rejected(method: str) -> None:
    report = load_readiness_manifest(MANIFEST)

    with pytest.raises(ManifestError, match="Unknown milestone"):
        getattr(report, method)("beta")


def test_fully_evidenced_manifest_can_be_go(tmp_path: Path) -> None:
    data = copy.deepcopy(_base_manifest())
    data["decision"] = "GO"
    for raw_gate in _list(data["gates"]):
        gate = _mapping(raw_gate)
        gate["status"] = "passed"
        gate["evidence"] = ["https://example.invalid/evidence"]
        gate["blockers"] = []
    for raw_item in _list(data["hardware"]):
        item = _mapping(raw_item)
        item["availability"] = "validated"
        item["evidence"] = ["https://example.invalid/hardware"]

    report = load_readiness_manifest(_write_manifest(tmp_path, data))

    assert report.is_ready("dev")
    assert report.is_ready("rc")
    assert report.is_ready("production")
    assert report.hardware_validated_version == "0.1.0"
    assert not report.blocking_gates("production")
    assert not report.blocking_hardware("production")


def test_missing_manifest_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="does not exist"):
        load_readiness_manifest(tmp_path / "missing.json")


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ManifestError, match="not valid JSON"):
        load_readiness_manifest(path)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data.update(schema_version=2), "Unsupported schema_version"),
        (lambda data: data.update(schema_version=True), "schema_version MUST be an integer"),
        (lambda data: data.update(decision="MAYBE"), "decision has unsupported value"),
        (lambda data: data.update(decision=""), "decision MUST be a non-empty string"),
        (lambda data: data.update(gates="bad"), "gates MUST be an array"),
        (lambda data: data.update(gates=[]), "gates MUST contain at least one"),
        (lambda data: _list(data["gates"]).__setitem__(0, "bad"), "gates[0] MUST be an object"),
        (lambda data: _gate(data, 0).update(status="unknown"), "unsupported value"),
        (lambda data: _gate(data, 0).update(required_for="dev"), "required_for MUST be an array"),
        (lambda data: _gate(data, 0).update(required_for=[1]), "required_for[0] MUST"),
        (lambda data: _gate(data, 0).update(required_for=["dev", "beta"]), "unknown milestones"),
        (
            lambda data: _gate(data, 0).update(required_for=["dev", "dev"]),
            "MUST NOT contain duplicates",
        ),
        (lambda data: _gate(data, 0).update(evidence=[]), "passed but has no evidence"),
        (lambda data: _gate(data, 3).update(blockers=[]), "blocked but names no blockers"),
        (
            lambda data: _gate(data, 3).update(status="not_applicable"),
            "not_applicable but is required",
        ),
        (
            lambda data: _gate(data, 0).update(evidence=["docs/release/missing.md"]),
            "missing evidence file",
        ),
        (lambda data: _gate(data, 1).update(id="G00"), "gate IDs MUST be unique"),
        (
            lambda data: _list(data["hardware"]).__setitem__(0, "bad"),
            "hardware[0] MUST be an object",
        ),
        (lambda data: _hardware(data, 0).update(quantity=True), "quantity MUST be an integer"),
        (lambda data: _hardware(data, 0).update(quantity=0), "quantity MUST be at least 1"),
        (lambda data: _hardware(data, 0).update(availability="lost"), "unsupported value"),
        (
            lambda data: _hardware(data, 0).update(availability="optional"),
            "optional but is required",
        ),
        (
            lambda data: _hardware(data, 0).update(availability="validated"),
            "validated but has no evidence",
        ),
        (
            lambda data: _hardware(data, 1).update(id="programmable-i3c-pair"),
            "hardware IDs MUST be unique",
        ),
        (lambda data: data.update(decision="GO"), "decision is GO"),
    ],
)
def test_invalid_manifest_shapes_are_rejected(
    tmp_path: Path,
    mutation: object,
    message: str,
) -> None:
    data = copy.deepcopy(_base_manifest())
    assert callable(mutation)
    mutation(data)

    with pytest.raises(ManifestError, match=re.escape(message)):
        load_readiness_manifest(_write_manifest(tmp_path, data))


def test_non_object_manifest_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="manifest MUST be an object"):
        load_readiness_manifest(_write_manifest(tmp_path, []))
