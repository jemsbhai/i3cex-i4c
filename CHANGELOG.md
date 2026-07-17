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
    nesting policy, TLV max block size, the Efficiency Principle,
    six-axis bakeoff methodology, and separate Python/C runtime
    evidence, the cross-candidate semantic-equivalence contract, and the
    framing-neutral extensibility taxonomy, coverage strategy, and
    per-scenario measurement contract, plus complete-encoding wire-
    overhead, complete-decoder parse-complexity, zero-tolerance legacy-
    safety, target-cycle worst-case-latency, and sustainable throughput-
    impact methodologies.

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
  - Section 5.1.5 now defines Candidate A's extension body as one
    schema-delimited section per active sublayer in ascending EX order.
  - Section 5.3.1 now requires canonical semantic workloads, complete
    candidate adapters, a paired comparable corpus, and a separate
    extensibility stress corpus.
  - Section 5.3's extensibility criterion now uses ADR-0013's semantic
    scenario families rather than only new-sublayer/new-record examples.
    Confirmatory scenario selection follows ADR-0014's anchor, boundary,
    extension-path, and pairwise-coverage rules; measurement follows
    ADR-0015's quality-gated multidimensional record.
  - Section 5.3's wire-overhead criterion now follows ADR-0016's
    complete-encoding octet accounting, with negotiation and physical
    transport reported separately.
  - Section 5.3's parse-complexity criterion now follows ADR-0017's
    complete-decoder cyclomatic and structural inventory, with C and
    Python reported separately.
  - Section 5.3's legacy-safety criterion now follows ADR-0018's
    oracle-labelled malformed, recovery, valid-unknown, negotiation, and
    fixed-budget fuzzing methodology.
  - Section 5.3's worst-case-latency criterion now follows ADR-0019's
    pinned Cortex-M0 intrinsic-cycle and deterministic loaded-response
    methodology, with empirical bounds distinguished from proven WCET.
  - Section 5.3's throughput-impact criterion now follows ADR-0020's
    exact wire, complete endpoint, and sustainable lossless combined-
    goodput methodology with explicit bottleneck attribution.
  - Section 6 sublayer skeletons now include placeholder Overhead
    Analysis subsections per the Efficiency Principle.
  - Appendix A expanded with TLV wire examples A.5 through A.8
    (single-record, multi-record, rejected reserved Type, rejected
    reserved Length range).
  - Appendix A.9 illustrates Candidate A's canonical section order.
  - Appendix B tracks resolved vs open questions. Five questions
    resolved by this round of ADRs.
- `specs/I4C-0.0.1-placeholder.md`: placeholder reserving the I4C
  specification namespace.

#### i3cex package (Track 1)

- Package scaffold under `i3cex/` with Hatch build backend, strict
  ruff / strict mypy / pytest+hypothesis tooling, pre-commit
  configuration, and Hatch environment scripts.
- PyPI distribution metadata and package README links target the public
  `jemsbhai/i3cex-i4c` repository.
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
  - ADR-0010: Six-axis bakeoff evaluation methodology and ADR split.
  - ADR-0011: Separate Python/C runtime evidence, with C-on-Cortex-M0
    primary for embedded claims.
  - ADR-0012: Canonical semantic equivalence, complete candidate
    adapters, and Candidate A's ordered extension-body contract.
  - ADR-0013: Framing-neutral extensibility scenario taxonomy with
    semantic families and orthogonal compatibility/pressure facets.
  - ADR-0014: Confirmatory extensibility coverage using mandatory family
    anchors, shared boundary/path inventories, and constrained pairwise
    facet coverage.
  - ADR-0015: Per-scenario extensibility measurement bundle covering
    categorical conformance, specification, Python/C changes,
    complexity, resources, wire context, and provenance.
  - ADR-0016: Wire-overhead measurement from actual complete encodings,
    with stratified corpus, negotiation, fragmentation, and payload-
    efficiency accounting.
  - ADR-0017: Parse-complexity measurement using complete receivers,
    cyclomatic/decision-surplus metrics, and structural parser
    inventories in separate C and Python evidence streams.
  - ADR-0018: Legacy-safety measurement using independent oracles,
    deterministic/exhaustive/stateful corpora, fixed-budget fuzzing, and
    zero-tolerance severity gates.
  - ADR-0019: Worst-case latency measurement using a pinned Cortex-M0
    target, shared slow-path search, deterministic interference-phase
    sweeps, and separate Python evidence.
  - ADR-0020: Throughput-impact measurement using exact physical traces,
    complete Cortex-M0 encoder/decoder capacity, bounded lossless
    pipeline replay, and separate Python evidence.
  - ADR `README.md` index and `TEMPLATE.md`.
- CI: `.github/workflows/ci.yml` at the repo root (workflow path-
  filtered to run only on changes under `i3cex/**` or the workflow
  itself). Quality, cross-OS test matrix (Linux/Windows/macOS x
  Python 3.11/3.12/3.13), cosim (gated placeholder), and build
  jobs. Checkout, Python setup, coverage upload, and artefact upload use
  their Node.js 24-backed v6 action releases.

#### i4c package placeholder (Track 2)

- `i4c/README.md` reserving the directory.
- `i4c/CHANGELOG.md` placeholder.
