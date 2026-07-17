# ADR-0018: Legacy-safety measurement

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

Specification section 5.3 defines legacy safety as the behaviour of an
EX-aware receiver when a misbehaving peer sends malformed EX data. The
framing candidates have different malformed surfaces: Candidate A has a
preamble, ordered sublayer sections, and candidate-specific section
boundaries; Candidate B has Type/Length records, reserved values, and
block boundaries. Counting raw rejection tests would therefore reward
the candidate with the smaller test corpus rather than the safer design.

Legacy safety also extends beyond returning an error. A receiver can
reject but first emit partial semantics, corrupt negotiated state, retain
fragment data, allocate unbounded memory, or leave the next valid frame
misparsed. At the system boundary, EX bytes must not be interpreted for
a peer that never negotiated EX support.

The project needs an oracle-driven, zero-tolerance methodology covering
deterministic malformed cases, state recovery, exhaustive short inputs,
property generation, sanitised C fuzzing, and legacy negotiation gates
in both maintained languages.

## Decision Drivers

- Safety is a conformance threshold, not a contest to minimise an
  arbitrary failure rate.
- Common semantic violations and candidate-specific grammar violations
  both require coverage.
- Invalid input must not produce partial canonical output or persistent
  state corruption.
- A valid corpus is required so a decoder cannot appear safe by rejecting
  everything.
- Independent expected outcomes are required; candidate agreement is not
  an oracle.
- Python and C must be tested separately and differentially.
- C memory safety and undefined behaviour require sanitised host builds
  plus constrained-target checks.
- Stateful recovery after malformed fragments and negotiation mismatch
  must be explicit.
- Fixed execution budgets and retained seeds are required for
  reproducible generated testing.

## Considered Options

- Option A: Test only normative malformed examples in the specification.
- Option B: Use random fuzzing and compare crash counts.
- Option C: Use a layered, oracle-labelled corpus with deterministic
  mutations, state sequences, exhaustive short inputs, fixed-budget
  generation/fuzzing, and zero-tolerance severity gates.
- Option D: Treat any explicit rejection as safe without checking state,
  partial output, or subsequent recovery.

## Decision Outcome

Chosen option: **Option C — evaluate both candidates against a layered,
independently labelled safety corpus and require zero critical or major
violations for safety conformance**.

Raw failure counts are reported with class denominators but are not
interpreted as real-world probabilities. Candidate-specific corpus size
does not become a ranking advantage.

## Scope and strata

The methodology separates three strata:

1. `MALFORMED-EX`: primary axis-4 stratum containing invalid encodings,
   contradictory state, and malformed fragment sequences.
2. `VALID-UNKNOWN`: conforming new-version or unknown semantics from the
   ADR-0013 extension corpus. Compatibility behaviour comes from axis 3;
   axis 4 checks only for unsafe misinterpretation, crashes, partial
   delivery, or state corruption.
3. `NEGOTIATION-GATE`: system-level cases ensuring non-negotiated peers
   and legacy payloads are not dispatched into an EX decoder.

Valid baseline/core cases form a mandatory control corpus but are not
counted as malformed safety cases. They detect reject-everything
implementations and establish recovery targets.

This ADR evaluates robustness under the protocol's declared caps and
state model. It is not a cryptographic security proof and does not claim
resistance to physical-layer fault injection or unbounded denial-of-
service outside those caps.

## Independent safety oracle

Every deterministic case has a manifest entry containing:

- Stable case ID and corpus version.
- Candidate and canonical valid seed, when mutation-derived.
- Raw bytes or sequence events.
- Grammar requirements and negotiation state.
- Valid, malformed, or valid-unknown classification.
- Allowed receiver outcome set.
- Required structured error class when normative.
- Required post-case state and recovery behaviour.

Expected outcomes come from a declarative grammar/constraint oracle
reviewed against the specification and accepted ADRs. The oracle is not
implemented by calling either production candidate decoder. Python/C
agreement and Candidate A/B agreement are diagnostics only.

When the specification permits more than one safe policy—such as
explicit rejection or legacy fallback under a `SHOULD`—the manifest
lists the allowed set and each implementation freezes its documented
policy before execution. A result inside the allowed set is not a
mismatch merely because another implementation chose differently.

## Receiver outcomes

Allowed outcome labels are:

- `ACCEPT-CANONICAL`: return the oracle's valid canonical transaction.
- `REJECT-EXPLICIT`: return a documented structured protocol error and
  no canonical output.
- `FALLBACK-LEGACY`: dispatch the original unconsumed bytes to the
  matched legacy path when the oracle permits fallback.
- `SKIP-UNKNOWN`: skip a valid unknown extension while preserving all
  required known semantics.
- `PRESERVE-OPAQUE`: retain a valid unknown extension without
  interpreting or corrupting it when the contract permits.

Unsafe or incorrect labels are:

- `SILENT-ACCEPT-INVALID`.
- `SILENT-MISINTERPRETATION`.
- `PARTIAL-SEMANTIC-DELIVERY` before later rejection.
- `WRONG-FALLBACK` or `WRONG-SKIP`.
- `FALSE-REJECT-VALID`.
- `CRASH` or unexpected process termination.
- `HANG-TIMEOUT`.
- `MEMORY-SAFETY-FAULT` or undefined behaviour.
- `RESOURCE-BOUND-BYPASS`.
- `STATE-CORRUPTION`.
- `CROSS-FRAME-CONTAMINATION` affecting a later valid case.
- `WRONG-ERROR-CLASS` with otherwise safe explicit rejection.

Python may expose only documented protocol exception/error types at its
public receiver boundary. Unexpected `IndexError`, `MemoryError`,
assertion failure, recursion failure, or implementation exception is a
`CRASH` or resource violation, not an explicit protocol rejection.

## Severity model

### Critical

- Crash, hang, memory-safety fault, or undefined behaviour.
- Silent semantic misinterpretation.
- Partial semantic delivery from a transaction ultimately rejected.
- Persistent state corruption or cross-frame contamination.
- Resource-bound bypass capable of unbounded read, allocation, recursion,
  or work inside the declared input cap.

### Major

- Malformed input accepted as canonical.
- Valid input falsely rejected.
- Fallback, skip, or preserve behaviour outside the oracle's allowed
  outcome set.
- Cap, version, negotiation, or peer-association checks bypassed without
  an observed critical consequence.
- Python/C disagreement where one side accepts or semantically
  interprets bytes the other rejects.

### Minor

- Both implementations safely reject with no output or state change, but
  one reports the wrong structured error class.
- Diagnostic location or consumed-byte count differs from the frozen
  contract without changing safety behaviour.

Error-message wording is not a safety metric.

## Deterministic confirmatory corpus

### Normative rejection vectors

Include every malformed/rejection example and every normative rejection
rule from the specification and framing ADRs. Each independent rule has
at least one isolated case and one interaction case when a second
violation can mask or precede it.

Stable violation families include:

- `MAL-TRUNCATION`.
- `MAL-RESERVED`.
- `MAL-LENGTH`.
- `MAL-CAP`.
- `MAL-ORDER`.
- `MAL-DUPLICATE`.
- `MAL-MISSING`.
- `MAL-SEMANTIC`.
- `MAL-FRAGMENT`.
- `MAL-NEGOTIATION`.
- `MAL-VERSION`.
- `MAL-TRAILING`.
- `MAL-RESOURCE`.

A family is instantiated only where the candidate grammar or shared
semantic contract defines the corresponding invalid condition. Missing
inapplicable families are recorded as `NOT-APPLICABLE`, not silently
omitted.

### Exhaustive short-input space

For each candidate and complete receiver configuration, classify and
execute every raw byte string of lengths 0, 1, and 2:

```text
1 + 256 + 65536 = 65793 cases
```

The oracle may classify some short strings as valid under a future
minimal sublayer grammar; those cases must accept canonically. The
exhaustive set therefore tests both false acceptance and false rejection.

### Systematic mutation set

For every valid confirmatory seed encoding, generate:

- Every proper truncation prefix, including empty input.
- Every single-bit flip at every encoded bit position.
- Structural-field substitutions using zero, one, minimum, maximum,
  maximum-minus-one, maximum-plus-one where representable, all reserved
  classes, and the original value.
- Single-byte deletion, duplication, and insertion at every structural
  field boundary.
- Record/section duplication, omission, and reordering where order or
  cardinality is normative.
- Appended zero, `0xFF`, valid-header, and valid-record suffixes.
- Declared-length versus available-length mismatches.
- Block/cap cases immediately below, at, and above every frozen limit.
- Capability-level, active-section, schema, and version contradictions.
- Fragment loss, duplication, reordering, overlap, stale continuation,
  and wrong-peer completion.

Mutation operators are shared across candidates where semantically
meaningful. Candidate-specific structural fields receive the same
operator classes, not necessarily the same byte offsets.

### Stateful recovery sequences

For every stateful mechanism and each representative violation family,
execute at least:

```text
valid -> malformed -> valid
malformed -> valid
valid-fragment-prefix -> malformed-fragment -> valid-complete-frame
peer-A-prefix -> peer-B-malformed -> peer-A-valid-completion
negotiated -> malformed-version -> valid-negotiated
reset/hot-join -> prior-session bytes -> valid-new-session
```

Before each sequence, retain a canonical state snapshot. After a
rejection, state must equal the specified rollback snapshot or a
documented safe reset state. The trailing valid case must produce the
same canonical result as a fresh decoder under the expected state.

No semantic callback, queue insertion, application-visible mutation, or
negotiated-state commit may occur before the complete transaction passes
validation unless the API provides an atomic rollback proven by the
state snapshot.

## Legacy negotiation-gate corpus

System-level dispatch tests cover:

- A legacy/non-EX peer that never completed EX discovery.
- Loss of negotiated state after reset, hot-join, or peer identity
  change.
- EX state associated with the wrong dynamic address or peer.
- Candidate A EX-present flag clear under negotiated and non-negotiated
  contexts.
- Candidate A reserved or extension-follows bits under the frozen policy.
- Candidate B-shaped bytes delivered without negotiated TLV framing.
- Malformed EX input followed by an ordinary legacy transaction.

Absent negotiation, ordinary I3C payload bytes must follow the legacy
path without speculative EX parsing. Conversely, malformed data on a
negotiated EX path must not silently downgrade unless the oracle
explicitly permits fallback. The original byte sequence must remain
unconsumed when legacy fallback is selected.

## Generated and fuzz testing

### Python budget

For each candidate, run 1,000,000 completed generated/mutated receiver
invocations across 10 fixed seeds (100,000 per seed) in addition to the
deterministic corpus. Generators preserve a labelled mixture of valid,
malformed, valid-unknown, and stateful sequence cases. Seed values,
generator version, strategy definitions, and every failing/minimised
example are retained.

### C budget

For each candidate, run 10,000,000 completed coverage-guided harness
invocations across 10 fixed seeds (1,000,000 per seed) using host builds
with AddressSanitizer, UndefinedBehaviorSanitizer, stack protection, and
the strictest supported compiler warnings. The seed corpus and mutation
dictionary derive from the same canonical and structural cases used by
Python.

Execution count, not wall time, is the fixed comparison budget. Elapsed
time, executions per second, discovered edges, corpus size, and peak
memory are reported as diagnostics. A safety fault is minimised and the
campaign resumes in a clean process until the fixed budget completes;
an infrastructure failure is `INCOMPLETE`, not a candidate safety
result.

The deterministic corpus and all minimised C failures are also run on
the pinned Cortex-M0 build or simulator with watchdog, stack/heap
canaries, declared scratch limits, and peer-state snapshots. Coverage-
guided fuzzing itself may remain on the sanitised host build.

Fuzzing can discover violations but cannot prove their absence. Zero
fuzz findings does not replace deterministic class and branch coverage.

## Resource and termination gates

Before malformed testing, valid-only calibration freezes per-length-bin
receiver time limits:

```text
timeout[c,l,bin] = min(1 second,
                       max(10 milliseconds,
                           100 * worst valid time[c,l,bin]))
```

Calibration uses only valid corpus cases and cannot be changed after
malformed outcomes are observed. A timeout is a critical
`HANG-TIMEOUT`. The manifest also records consumed octets, parser steps
when instrumentable, allocations, scratch high-water mark, and state
size for every failing or boundary case.

Input caps must be checked before candidate-controlled lengths can cause
out-of-bounds access or unbounded allocation. C timed/production paths
must not newly allocate from the heap; caller-provided buffers and
declared capacities remain enforced. Python memory growth must remain
within the frozen bound derived from valid inputs of the same length bin.

Latency and cycle counts belong to axis 5. They are retained here only
to classify termination/resource violations and are not used to rank
safe candidates.

## Per-case record

Every executed deterministic case and every retained generated failure
records:

- Case, candidate, language, binary/source, oracle, and seed digests.
- Raw bytes or event sequence.
- Negotiation, peer, cap, fragment, and reset context.
- Allowed and observed outcome labels.
- Structured error class and consumed-byte count.
- Canonical output or proof that no output was committed.
- State hashes/snapshots before and after.
- Recovery-case result.
- Elapsed time or step count and timeout threshold.
- Allocation/scratch high-water marks.
- Sanitizer, canary, watchdog, and process-exit status.
- Severity and root-cause identifier for every violation.

Duplicate fuzz symptoms are grouped only after retaining raw cases. A
root-cause group links all triggering inputs and the minimised reproducer.

## Coverage and admissibility gates

A candidate/language safety result is admissible only when:

- Every applicable normative rejection rule and violation family has a
  passing deterministic case.
- Every allowed outcome is exercised where constructible.
- The exhaustive short-input set is complete.
- Every systematic mutation operator completed for every valid seed.
- Every required stateful and negotiation sequence completed.
- The fixed generated/fuzz execution budget completed.
- Candidate-specific receiver files reach 100% line and branch coverage,
  with only proven unreachable defensive paths explicitly listed.
- Python and C agree on semantic accept/reject/fallback outcomes for the
  same candidate, except for allowed error-representation differences.
- All valid canonical controls pass.
- All raw results, coverage reports, and minimised failures are retained.

A missing gate yields `INCOMPLETE`; it does not reduce the denominator or
become a passing zero.

## Safety acceptance and candidate comparison

For one candidate/language:

- `PASS`: zero critical, major, and minor violations; all gates complete.
- `SAFE-BUT-IMPRECISE`: zero critical and major violations, at least one
  minor diagnostic mismatch; all gates complete.
- `FAIL`: at least one critical or major violation.
- `INCOMPLETE`: at least one required gate or evidence set is missing.

`PASS` and `SAFE-BUT-IMPRECISE` are both
`SAFETY-CONFORMING` for the primary safety threshold. Error precision is
reported separately.

C is primary for embedded safety and Python is a required independent
result. A candidate's cross-language status is safety-conforming only if
both its C and Python results are safety-conforming. A language reversal
is reported explicitly and blocks an unqualified safety claim.

Candidate comparison uses threshold labels:

- `BOTH-SAFETY-CONFORMING`: both candidates meet the primary threshold;
  axis 4 is a primary safety tie, with minor diagnostics reported.
- `ONLY-A-SAFETY-CONFORMING` or `ONLY-B-SAFETY-CONFORMING`: exactly one
  candidate meets the threshold.
- `BOTH-FAIL`: both have a critical or major violation; no winner is
  declared by counting failures.
- `COMPARISON-INCOMPLETE`: either candidate lacks required evidence.

Violation counts are reported by severity, root cause, violation family,
language, and stratum with exact denominators. They are not treated as
independent samples, converted into population failure probabilities, or
weighted against wire/complexity benefits. A single critical violation
cannot be offset by many passing cases.

## Reproducibility manifest

Retain at least:

- Specification, oracle, candidate, corpus, and canonical-schema
  revisions.
- Every deterministic case and expected-outcome manifest.
- Applicability matrix for violation families.
- Mutation operators, valid seeds, generated strategies, dictionaries,
  and fixed random seeds.
- Python and C execution budgets and completed invocation counts.
- Compiler, sanitizer, warning, watchdog, simulator, and target settings.
- Valid-only timeout calibration inputs and frozen thresholds.
- Per-case outcomes, state snapshots, resource records, and coverage.
- All raw and minimised failures with root-cause grouping.
- Every `NOT-APPLICABLE`, `INCOMPLETE`, and unreachable-path
  justification.

Derived safety tables must be reproducible from retained case records
without rerunning decoders or fuzzers.

## Consequences

**Good:**

- Safety claims depend on explicit conformance thresholds rather than
  arbitrary failure rates.
- Deterministic, exhaustive-short, stateful, and generated layers cover
  different defect classes.
- Candidate-specific grammars receive appropriate cases without making
  corpus size a ranking advantage.
- Partial output and post-error state are treated as first-class safety
  properties.
- Valid controls prevent reject-everything decoders from passing.
- Sanitised host fuzzing and target replay cover both memory safety and
  deployment behaviour.

**Bad:**

- Corpus/oracle construction and state snapshotting require substantial
  infrastructure.
- Fixed million-case budgets add compute time for both languages and
  candidates.
- Zero-tolerance thresholds can leave both candidates failing because of
  one reproducible defect.
- Complete C and Python semantic receivers are prerequisites.
- Fuzzing remains evidence of tested robustness, not proof of universal
  safety.

## Pros and Cons of the Options

### Option A: Normative examples only

- Good: Small, clear, and directly traceable to the specification.
- Bad: Misses mutation interactions, state recovery, short-input space,
  and memory-safety faults.

### Option B: Random fuzzing and crash counts

- Good: Finds unexpected implementation defects with little manual case
  design.
- Bad: Candidate speed and corpus shape distort raw crash counts.
- Bad: No independent classification of false acceptance, fallback, or
  state corruption.

### Option C: Layered oracle-labelled safety corpus

- Good: Combines specification traceability, systematic coverage,
  stateful recovery, and implementation hardening.
- Good: Supports zero-tolerance, independently reproducible acceptance.
- Good: Preserves valid-unknown and legacy-dispatch distinctions.
- Bad: Highest corpus, oracle, execution, and retention cost.

### Option D: Any explicit rejection is safe

- Good: Very simple receiver contract and measurement.
- Bad: Ignores partial delivery, incorrect downgrade, corrupted state,
  resource abuse, and later-frame contamination.
- Bad: Allows reject-everything implementations to appear ideal.

## References

- [`./0002-framing-comparative-prototyping.md`](./0002-framing-comparative-prototyping.md)
  — parent framing-bakeoff decision.
- [`./0005-preamble-wire-format.md`](./0005-preamble-wire-format.md)
  — Candidate A reserved-bit, detection, and fallback rules.
- [`./0006-tlv-length-encoding.md`](./0006-tlv-length-encoding.md)
  — Candidate B reserved-length rejection rules.
- [`./0007-tlv-nesting-deferred.md`](./0007-tlv-nesting-deferred.md)
  — reserved Type and flat-only rejection rules.
- [`./0008-tlv-max-block-size.md`](./0008-tlv-max-block-size.md)
  — negotiated cap behaviour.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical output and complete-adapter boundary.
- [`./0013-extensibility-scenario-taxonomy.md`](./0013-extensibility-scenario-taxonomy.md)
  — valid-unknown compatibility distinction.
- [`./0017-parse-complexity-measurement.md`](./0017-parse-complexity-measurement.md)
  — rejection-branch inventory and coverage gate.
- [`./0019-worst-case-latency-measurement.md`](./0019-worst-case-latency-measurement.md)
  — separate ranking of bounded rejection and successful-path latency.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — legacy-safety
  comparison criterion.
