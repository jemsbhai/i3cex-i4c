"""Validate and summarize the I3C-EX release-readiness manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from i3cex.release import ManifestError, ReadinessReport, load_readiness_manifest

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_MANIFEST = _PACKAGE_ROOT / "release" / "readiness-v0.1.0.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=_DEFAULT_MANIFEST,
        help="Path to the release-readiness JSON manifest.",
    )
    parser.add_argument(
        "--require",
        choices=("dev", "rc", "production"),
        help="Exit non-zero unless the selected milestone is ready.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable summary.")
    return parser


def _as_json(report: ReadinessReport) -> str:
    milestones = {}
    for milestone in ("dev", "rc", "production"):
        milestones[milestone] = {
            "version": report.version_for(milestone),
            "ready": report.is_ready(milestone),
            "blocking_gates": [gate.id for gate in report.blocking_gates(milestone)],
            "blocking_hardware": [item.id for item in report.blocking_hardware(milestone)],
        }
    return json.dumps(
        {
            "decision": report.decision,
            "decision_reason": report.decision_reason,
            "updated": report.updated,
            "milestones": milestones,
        },
        indent=2,
        sort_keys=True,
    )


def _as_text(report: ReadinessReport) -> str:
    lines = [
        f"Release decision: {report.decision}",
        f"Reason: {report.decision_reason}",
        f"Manifest updated: {report.updated}",
    ]
    for milestone in ("dev", "rc", "production"):
        readiness = "READY" if report.is_ready(milestone) else "BLOCKED"
        lines.append(f"{milestone}: {report.version_for(milestone)} — {readiness}")
        for gate in report.blocking_gates(milestone):
            lines.append(f"  gate {gate.id}: {gate.name} [{gate.status}]")
        for item in report.blocking_hardware(milestone):
            lines.append(
                f"  hardware {item.id}: {item.quantity} x {item.model} "
                f"for {item.role} [{item.availability}]"
            )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the readiness checker and return a process exit code."""
    args = _parser().parse_args(argv)
    try:
        report = load_readiness_manifest(args.manifest)
    except ManifestError as exc:
        print(f"invalid release manifest: {exc}")
        return 2

    print(_as_json(report) if args.json else _as_text(report))
    if args.require and not report.is_ready(args.require):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
