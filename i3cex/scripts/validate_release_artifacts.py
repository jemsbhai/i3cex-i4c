"""Build, audit, reproduce, and smoke-test i3cex release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_FORBIDDEN_PARTS = frozenset(
    {
        ".coverage",
        ".env",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "coverage.xml",
        "htmlcov",
    }
)
_SMOKE_CODE = """
from importlib import metadata, resources

import i3cex
from i3cex.framing.preamble import Preamble, decode_option_a, encode_option_a
from i3cex.framing.tlv import TLVRecord, decode_tlv_block, encode_tlv_block

assert metadata.version("i3cex") == i3cex.__version__
assert resources.files("i3cex").joinpath("py.typed").is_file()
preamble = Preamble(capability_level=0, sublayer_bitmap=0, extension_follows=False)
encoded_preamble = encode_option_a(preamble)
assert encoded_preamble == b"\\x80"
assert decode_option_a(encoded_preamble) == (preamble, b"")
records = [TLVRecord(type_=1, value=b"release-smoke")]
assert decode_tlv_block(encode_tlv_block(records)) == records
"""


class ArtifactValidationError(RuntimeError):
    """Raised when a release artifact fails a mandatory validation."""


@dataclass(frozen=True)
class ArtifactSet:
    """One sdist/wheel build and its digests."""

    wheel: Path
    sdist: Path
    digests: dict[str, str]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=_PACKAGE_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        help="Copy the validated first build to this directory.",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Permit a dirty Git worktree for pre-commit development checks.",
    )
    return parser


def _run(command: Sequence[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def _git_output(project: Path, *args: str) -> str:
    return _run(("git", "-C", str(project), *args), project)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_single(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise ArtifactValidationError(
            f"Expected exactly one {pattern} artifact in {directory}, found {len(matches)}"
        )
    return matches[0]


def _build(project: Path, output: Path, source_date_epoch: str) -> ArtifactSet:
    output.mkdir(parents=True)
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = source_date_epoch
    _run(
        (
            sys.executable,
            "-m",
            "build",
            "--sdist",
            "--wheel",
            "--outdir",
            str(output),
            str(project),
        ),
        project,
        env,
    )
    wheel = _find_single(output, "*.whl")
    sdist = _find_single(output, "*.tar.gz")
    return ArtifactSet(
        wheel=wheel,
        sdist=sdist,
        digests={wheel.name: _sha256(wheel), sdist.name: _sha256(sdist)},
    )


def _assert_safe_names(names: Iterable[str], artifact: Path) -> None:
    for name in names:
        path = Path(name)
        lowered_parts = {part.lower() for part in path.parts}
        if lowered_parts & _FORBIDDEN_PARTS or path.suffix.lower() == ".pyc":
            raise ArtifactValidationError(f"Forbidden generated file in {artifact.name}: {name}")
        if path.is_absolute() or ".." in path.parts:
            raise ArtifactValidationError(f"Unsafe path in {artifact.name}: {name}")


def _audit_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    _assert_safe_names(names, path)
    required = {
        "i3cex/__init__.py",
        "i3cex/framing/preamble.py",
        "i3cex/framing/tlv.py",
        "i3cex/py.typed",
        "i3cex/release.py",
    }
    missing = required - set(names)
    if missing:
        raise ArtifactValidationError(
            f"Wheel is missing required files: {', '.join(sorted(missing))}"
        )
    if not any(name.endswith(".dist-info/METADATA") for name in names):
        raise ArtifactValidationError("Wheel is missing dist-info/METADATA")


def _audit_sdist(path: Path) -> None:
    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()
    names = [member.name for member in members]
    _assert_safe_names(names, path)
    if any(member.issym() or member.islnk() for member in members):
        raise ArtifactValidationError("Sdist MUST NOT contain symbolic or hard links")
    required_suffixes = {
        "/docs/release/RELEASE_PLAN.md",
        "/release/readiness-v0.1.0.json",
        "/scripts/check_release_readiness.py",
        "/src/i3cex/release.py",
        "/tests/unit/test_release_readiness.py",
    }
    for suffix in required_suffixes:
        if not any(name.endswith(suffix) for name in names):
            raise ArtifactValidationError(f"Sdist is missing required file: *{suffix}")


def _venv_python(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def _smoke_install(artifact: Path, environment: Path, project: Path) -> None:
    venv.EnvBuilder(with_pip=True, clear=True).create(environment)
    python = _venv_python(environment)
    _run(
        (
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            str(artifact),
        ),
        project,
    )
    _run((str(python), "-c", _SMOKE_CODE), environment)


def _validate_metadata(artifacts: ArtifactSet, project: Path) -> None:
    _run(
        (
            sys.executable,
            "-m",
            "twine",
            "check",
            "--strict",
            str(artifacts.wheel),
            str(artifacts.sdist),
        ),
        project,
    )


def _copy_artifacts(artifacts: ArtifactSet, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for artifact in (artifacts.wheel, artifacts.sdist):
        shutil.copy2(artifact, output / artifact.name)


def _validate_clean_tree(project: Path, allow_dirty: bool) -> None:
    status = _git_output(project, "status", "--porcelain")
    if status and not allow_dirty:
        raise ArtifactValidationError(
            "Git worktree is dirty; commit the release inputs or pass --allow-dirty for development"
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the deterministic build and isolated-install release gate."""
    args = _parser().parse_args(argv)
    project = Path(args.project).resolve()
    output = Path(args.output).resolve() if args.output else None
    try:
        _validate_clean_tree(project, bool(args.allow_dirty))
        source_date_epoch = _git_output(project, "log", "-1", "--format=%ct")
        with tempfile.TemporaryDirectory(prefix="i3cex-release-") as temporary:
            root = Path(temporary)
            first = _build(project, root / "build-1", source_date_epoch)
            second = _build(project, root / "build-2", source_date_epoch)
            if first.digests != second.digests:
                raise ArtifactValidationError(
                    "Repeated builds are not byte-for-byte reproducible: "
                    f"{first.digests!r} != {second.digests!r}"
                )
            _audit_wheel(first.wheel)
            _audit_sdist(first.sdist)
            _validate_metadata(first, project)
            _smoke_install(first.wheel, root / "wheel-venv", project)
            _smoke_install(first.sdist, root / "sdist-venv", project)
            if output is not None:
                _copy_artifacts(first, output)
        print(
            json.dumps(
                {
                    "artifacts": first.digests,
                    "reproducible": True,
                    "source_date_epoch": source_date_epoch,
                    "twine_strict": True,
                    "wheel_install": "passed",
                    "sdist_install": "passed",
                },
                indent=2,
                sort_keys=True,
            )
        )
    except (ArtifactValidationError, OSError, subprocess.CalledProcessError) as exc:
        print(f"artifact validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
