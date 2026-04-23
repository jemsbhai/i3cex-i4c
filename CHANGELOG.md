# Changelog

All notable top-level project-wide changes are recorded here. Individual
package changelogs live under `i3cex/CHANGELOG.md` and `i4c/CHANGELOG.md`.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

#### Repository foundation

- Top-level `README.md` describing the dual-track strategy (I3C-EX
  extension layer + I4C clean-redesign), motivation, and layout.
- Top-level `LICENSE` (MIT).
- Top-level `.gitignore` covering Python, Hatch, testing tooling, IDE
  artefacts, OS junk, hardware/simulation artefacts, and secrets.
- Top-level `GOVERNANCE.md` establishing:
  - Semantic Versioning 2.0.0 rules for both specifications and software.
  - Strict TDD with coverage targets (95%+ line / 90%+ branch for
    core protocol logic).
  - Four-layer test organisation (unit, property, integration, cosim).
  - Conventional Commits.
  - Keep-a-Changelog discipline.
  - Google-style docstrings.
  - Pre-registration policy for specifications.
  - Decision log with eight recorded decisions.

#### Specifications

- `specs/README.md` establishing naming conventions, versioning rules,
  immutability policy, and pre-registration requirements.
- `specs/I3CEX-0.1.0-draft.md`: draft of the I3C-EX specification.
  - v0.1 section 5.1 (preamble-byte framing) finalised with concrete
    Option A bit layout, semantic constraints, detection rules, and
    forward-compatibility mechanism.
  - Appendix A with non-normative wire examples (0x90 for EX-1, 0xC0
    for EX-6, 0x91 rejected as malformed).
  - Other sublayers, CCC allocation, timestamp width, TLV framing,
    and HDR path remain marked `[TBD]`.
- `specs/I4C-0.0.1-placeholder.md`: placeholder reserving the I4C
  specification namespace.

#### i3cex package (Track 1)

- Package scaffold under `i3cex/` with Hatch build backend, strict
  ruff / strict mypy / pytest+hypothesis tooling, pre-commit
  configuration, and Hatch environment scripts.
- Cross-platform pytest runner at `scripts/run_pytest.py` bypassing
  PowerShell quoting issues with marker expressions.
- Source tree under `src/i3cex/`:
  - Root `__init__.py` exposing `__version__ = "0.1.0.dev0"`.
  - PEP 561 `py.typed` marker.
  - Sublayer stubs for envelope, qos, fusion, timesync, provenance,
    confidence, and sim.
  - **First real implementation**: `framing/preamble.py` with
    Option A encoder/decoder, `Preamble` dataclass,
    `PreambleEncodeError` and `PreambleDecodeError` exceptions.
    Full invariant enforcement per spec section 5.1.2.
- Test tree under `tests/` with comprehensive coverage of Option A:
  - `tests/unit/test_package.py`: 3 scaffolding sanity tests.
  - `tests/unit/framing/test_preamble.py`: 19 parametrised unit
    tests including all 7 valid capability levels and all three
    spec Appendix A vectors.
  - `tests/property/framing/test_preamble.py`: 9 Hypothesis-based
    property tests covering roundtrip invariants, byte-count
    invariants, bit-discipline invariants, and rejection invariants.
  - `tests/vectors/README.md` establishing the normative JSON
    test-vector format and conformance policy.
- Documentation:
  - `docs/adr/README.md` with ADR index.
  - `docs/adr/TEMPLATE.md`.
  - ADR-0001 through ADR-0005.
- CI: `.github/workflows/ci.yml` with quality, cross-OS test matrix,
  cosim (gated), and build jobs.

#### i4c package placeholder (Track 2)

- `i4c/README.md` reserving the directory.
- `i4c/CHANGELOG.md` placeholder.
