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
  - Normative **Efficiency Principle** requiring every sublayer to
    include an Overhead Analysis documenting worst-case bytes, parse
    complexity delta, a documented bit-packing or amortisation
    technique, and an explicit trade-off statement.
  - Sanctioned and unsanctioned optimisation technique lists.
  - Decision log with entries for dual-track architecture, framing
    comparison, sublayer order, MIT licensing, simulation strategy,
    Hatch packaging, preamble wire format, TLV length encoding, TLV
    nesting policy, TLV max block size, and the Efficiency Principle.

#### Specifications

- `specs/README.md` establishing naming conventions, versioning rules,
  immutability policy, and pre-registration requirements.
- `specs/I3CEX-0.1.0-draft.md`: draft of the I3C-EX specification with:
  - Section 5.1 (preamble-byte framing) finalised with concrete
    Option A bit layout, semantic constraints, detection rules, and
    forward-compatibility mechanism.
  - Section 5.2 (TLV framing) finalised with: record layout
    (Type 1B + Length 1B + Value), Type-range allocation per sublayer,
    Type 0xFE reservation, Length-byte high-bit reservation
    (0x80-0xFF), flat-only nesting policy, device-negotiated max
    block size with 4096-byte default, three documented forward-
    compatibility paths (α reserved Type, β high-bit Length, γ
    continuation records).
  - Section 6 sublayer skeletons now include placeholder Overhead
    Analysis subsections per the Efficiency Principle.
  - Appendix A expanded with TLV wire examples A.5 through A.8
    (single-record, multi-record, rejected reserved Type, rejected
    reserved Length range).
  - Appendix B tracks resolved vs open questions. Four questions
    resolved by this round of ADRs.
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
    100% line and branch coverage.
- Test tree under `tests/`:
  - `tests/unit/test_package.py`: 3 scaffolding sanity tests.
  - `tests/unit/framing/test_preamble.py`: 19 parametrised unit
    tests covering all 7 valid capability levels and all spec
    Appendix A vectors.
  - `tests/unit/framing/test_preamble_rejections.py`: 9 tests
    covering all encoder and decoder rejection branches.
  - `tests/property/framing/test_preamble.py`: 9 Hypothesis-based
    property tests covering roundtrip, byte-count, bit-discipline,
    and rejection invariants.
  - `tests/vectors/README.md` establishing the normative JSON
    test-vector format and conformance policy.
- Documentation under `docs/adr/`:
  - ADR-0001: Dual-track architecture.
  - ADR-0002: Comparative prototyping of framing strategies.
  - ADR-0003: Hybrid simulation stack.
  - ADR-0004: Hatch over Poetry for packaging.
  - ADR-0005: Preamble wire format (Option A) with forward-
    compatibility paths.
  - ADR-0006: TLV length encoding — fixed 1-byte with documented
    extension paths.
  - ADR-0007: TLV nesting deferred, Type 0xFE reserved for future
    container semantics.
  - ADR-0008: TLV maximum block size — negotiated with 4096-byte
    default.
  - ADR-0009: Efficiency Principle — every feature must offset its
    cost.
  - ADR `README.md` index and `TEMPLATE.md`.
- CI: `.github/workflows/ci.yml` at the repo root (workflow path-
  filtered to run only on changes under `i3cex/**` or the workflow
  itself). Quality, cross-OS test matrix (Linux/Windows/macOS x
  Python 3.11/3.12/3.13), cosim (gated placeholder), and build
  jobs.

#### i4c package placeholder (Track 2)

- `i4c/README.md` reserving the directory.
- `i4c/CHANGELOG.md` placeholder.
