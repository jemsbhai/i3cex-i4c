# ADR-0012: Semantic equivalence and Candidate A body contract

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

The two framing prototypes do not yet perform equivalent work.
Candidate A's implementation parses a one-byte preamble and returns all
remaining bytes untouched. Candidate B parses a complete sequence of
typed, length-delimited metadata records. Comparing those code paths
directly would credit Candidate A for work deferred to an unspecified
higher-layer parser and charge Candidate B for work it actually
performs.

The specification also states that a Candidate A preamble activates a
monotonic prefix of sublayers, but it does not define the order or
boundaries of those sublayers' data after the preamble. Without that
contract, wire overhead, full parse cost, latency, throughput, and
extensibility cannot be compared on equivalent semantics.

The bakeoff needs a framing-independent semantic workload model and a
minimum Candidate A extension-body contract before any per-axis
methodology can be scientifically defensible.

## Decision Drivers

- Construct validity: both candidates must encode and recover the same
  extension meaning.
- Full-cost accounting: a candidate cannot omit or push required work
  outside the measured path.
- Fairness: candidate-specific strengths and limitations must remain
  visible without forcing identical wire bytes.
- Layering: sublayer field layouts remain the responsibility of
  Sections 6.1 through 6.6, not the framing layer.
- Reproducibility: semantic workloads and representability outcomes
  must be versioned inputs to every per-axis experiment.
- Extensibility validity: inability to represent a requested semantic
  scenario is data, not a reason to silently change the workload.

## Considered Options

- Option A: Compare the currently implemented framing functions as-is.
- Option B: Give both candidates the same opaque bytes after their
  header and measure only header handling.
- Option C: Define a canonical semantic model, require complete
  candidate-specific adapters, and define an ordered Candidate A
  section contract.
- Option D: Fully specify all six sublayers before defining the
  comparison contract.

## Decision Outcome

Chosen option: **Option C — workloads are defined in a canonical
framing-independent semantic model, both candidates must round-trip
that model through complete adapters, and Candidate A carries active
sublayer sections once each in ascending EX order**.

The contract deliberately fixes only what the framing comparison needs.
It does not pre-empt the bit-level field decisions still required for
EX-1 through EX-6.

### Canonical semantic model

Every bakeoff workload instance describes extension meaning rather than
candidate wire bytes. At minimum, an instance contains:

- A workload identifier and schema version.
- The set of active sublayers.
- An ordered sequence of semantic records for each active sublayer,
  including record kind and field values.
- Any state or negotiation context required to interpret the instance.
- The opaque application-payload length and, when content affects the
  experiment, its bytes.
- The expected success value or semantic rejection class.

The application payload is a workload parameter, not extension
metadata. A per-axis methodology may use its length to calculate
effective payload bandwidth, but neither candidate may count those
bytes as metadata delivered. Final EX-1 encapsulation and transport
placement remain sublayer design concerns.

The canonical model is the equality boundary. Successful candidate
decoders must recover the same canonical meaning; their encoded bytes
are expected to differ.

### Candidate A extension-body contract

For a Candidate A preamble declaring capability level `N`, the
extension block has this logical layout:

```text
Preamble(N) || Section(EX-1) || Section(EX-2) || ... || Section(EX-N)
```

The following rules are normative for the v0.1 bakeoff:

1. `N = 0` carries no sublayer sections.
2. For `N > 0`, exactly one section for every sublayer EX-1 through
   EX-N appears in ascending numeric order.
3. A section's grammar is defined by its owning sublayer specification.
   Identity is derived from canonical position, so the framing layer
   does not add a per-section Type byte.
4. Every section boundary must be determinable from in-band bytes and
   the frozen sublayer schema. A section may be fixed-width or may carry
   an internal length, count, or other self-delimiting structure.
5. A non-final section must not consume an unspecified "remainder" of
   the block. No implementation may rely on an out-of-band section
   length unavailable to its peer.
6. All delimiter, length, count, subtype, padding, or default-value
   bytes required by a sublayer grammar are part of Candidate A's wire
   cost and parse cost.
7. The one-byte preamble codec alone is not a complete Candidate A
   benchmark adapter. The measured decode path must parse all sections
   needed to reconstruct the canonical semantic model.

If a sublayer has several semantic record kinds, its section grammar
must identify and delimit them internally. The cost of doing so is not
discarded as "intrinsic" for the primary wire result: every byte in the
encoded Candidate A extension block counts. A per-axis ADR may add a
pre-registered semantic-payload-versus-framing breakdown, but that
breakdown cannot alter the total-byte result.

### Candidate B mapping contract

Candidate B maps canonical semantic records to TLV records using the
owning sublayer's Type range and Value grammar. Type and Length bytes,
continuation or fragmentation bytes if later adopted, and block-level
signalling are charged to Candidate B. As with Candidate A, every byte
in the encoded extension block counts toward the primary total-byte
result regardless of any secondary breakdown.

The measured Candidate B path must parse TLV framing and all sublayer
Values needed to reconstruct the canonical semantic model. Treating
Values as opaque is valid for a framing-only unit test, but not for the
full semantic bakeoff when Candidate A is charged for sublayer parsing.

### Comparable and stress corpora

The experiment suite has two explicit corpus classes:

1. **Comparable core corpus**: semantic instances representable by both
   candidates. Because Candidate A v0.1 is level-monotonic, active
   sublayers in this corpus are prefixes: none, EX-1, EX-1..EX-2, and so
   on through EX-1..EX-6.
2. **Extensibility stress corpus**: scenarios may request sparse
   sublayers, unknown record kinds, additional sublayers, oversized
   values, hierarchy, or other evolution cases. A candidate's inability
   to represent a scenario is recorded as `UNREPRESENTABLE`; it must not
   be replaced by dummy semantics or dropped from the denominator.

Direct paired performance claims use the comparable core corpus.
Representability rates and failure modes from the stress corpus feed
the extensibility and legacy-safety axes. Results from the two corpus
classes must not be pooled.

### Equivalence and admissibility gates

A measurement is admissible only when all of the following hold:

- The workload instance and canonical schema version are retained.
- Both candidate encoders receive the same canonical instance.
- Each successful decode equals that instance after documented
  canonical normalisation.
- Python and C produce identical wire bytes for the same candidate and
  canonical input.
- Python and C agree on semantic success or rejection for the same
  candidate wire input.
- Candidate-specific failures retain a reason and are included in the
  appropriate coverage result.

Canonical normalisation may remove representation-only differences such
as map ordering. It must not erase a semantic field, synthesize missing
data, or convert an unsupported case into a supported one.

### Cost boundary

For paired measurements, the timed and counted operation begins with a
canonical instance or candidate wire block and ends only after the full
candidate representation or canonical decoded result is available.
Common workload construction, transport of unchanged application bytes,
and result logging are outside the framing cost boundary. Candidate-
specific transformation, validation, delimitation, and dispatch are
inside it.

Per-axis ADRs may refine this boundary, but may not return to a
preamble-header-only versus full-TLV comparison.

## Consequences

**Good:**

- Both candidates are compared on delivered meaning rather than unequal
  parser depth.
- Candidate A now has an auditable extension-body ordering and boundary
  rule without prematurely fixing sublayer fields.
- Sparse-set and other representability limitations become explicit
  extensibility evidence.
- Candidate-specific wire encodings can differ while differential
  Python/C conformance remains byte-exact within each candidate.
- The core and stress corpora prevent unsupported cases from distorting
  paired runtime statistics.

**Bad:**

- The existing Candidate A preamble codec is only a header codec; a full
  adapter cannot be completed until relevant sublayer section grammars
  are specified.
- Candidate B needs semantic Value parsing in addition to its current
  framing parser for full-pipeline comparisons.
- Canonical model, adapters, and corpus tooling add work before
  benchmarking.
- Some future sublayer layout choices can change both candidates' costs,
  requiring corpus and manifest version updates.

## Pros and Cons of the Options

### Option A: Compare current functions as-is

- Good: Benchmarking could start immediately.
- Bad: Candidate A parses one header while Candidate B parses a record
  block, so timing and complexity measure different operations.
- Bad: Candidate A body bytes and boundaries remain unspecified.

### Option B: Shared opaque body

- Good: Isolates the minimum framing-header cost.
- Good: Requires little additional implementation.
- Bad: Cannot measure record dispatch, sublayer evolution, sparse
  support, or complete decode latency.
- Bad: Answers a narrower question than specification section 5.3 asks.

### Option C: Canonical model and complete adapters

- Good: Provides an explicit construct-valid comparison boundary.
- Good: Preserves natural candidate-specific encodings and limitations.
- Good: Supports every comparison axis from one versioned workload
  source.
- Bad: Requires section grammars and semantic adapters before runtime
  experiments.

### Option D: Fully specify all sublayers first

- Good: Removes nearly all placeholder semantics before benchmarking.
- Bad: Delays the foundational framing decision until after substantial
  downstream design work depends on it.
- Bad: Conflates a minimum comparison contract with unrelated sublayer
  field decisions.

## References

- [`./0002-framing-comparative-prototyping.md`](./0002-framing-comparative-prototyping.md)
  — parent decision requiring an empirical framing bakeoff.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0011-python-c-runtime-evidence.md`](./0011-python-c-runtime-evidence.md)
  — separate Python and C evidence streams and differential conformance.
- [`./0020-throughput-impact-measurement.md`](./0020-throughput-impact-measurement.md)
  — complete encoder/decoder boundaries and canonical payload goodput.
- `../../../specs/I3CEX-0.1.0-draft.md` sections 5 and 6 — framing and
  sublayer contracts updated by this decision.
