# ADR-0016: Wire-overhead measurement

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

Specification section 5.3 defines wire overhead as bytes added per
transaction for EX-1 through EX-6. The current prototypes make a naive
comparison tempting: Candidate A has a one-byte preamble, while
Candidate B has a two-byte Type/Length header per record. That comparison
is invalid because Candidate A's sublayer sections still require
boundaries, subtype signalling, and complete semantic payloads, while
Candidate B already exposes some of those costs in its framing.

ADR-0012 requires both candidates to encode and recover the same
canonical meaning and requires every encoded extension byte to count.
This ADR must turn that rule into exact estimands, workload strata,
negotiation and fragmentation accounting, and deterministic reporting.

## Decision Drivers

- Count complete candidate representations, not framing headers in
  isolation.
- Present both candidates with identical canonical semantic instances,
  application payloads, caps, and negotiation context.
- Separate recurring per-transaction bytes from one-time negotiation
  bytes.
- Retain fragmentation, repeated headers, padding, and escape bytes.
- Use actual encoder output as the primary source of truth, with analytic
  formulas only as cross-checks.
- Keep protocol-layer octets distinct from physical bus bits and timing.
- Report deterministic exact results without meaningless repetitions or
  significance tests.
- Avoid a workload-weighted universal winner when no empirical workload
  distribution has been established.

## Considered Options

- Option A: Compare only the one-byte preamble and two-byte TLV headers.
- Option B: Compare analytic size formulas without executing encoders.
- Option C: Count every byte in actual complete extension blocks for a
  frozen canonical corpus, with negotiation and transport effects
  reported separately.
- Option D: Measure only physical I3C bus bits or elapsed bus time.

## Decision Outcome

Chosen option: **Option C — the primary wire-overhead endpoint is the
number of 8-bit octets in the complete candidate-specific extension
representation produced for the same canonical semantic transaction**.

One-time negotiation, recurring extension blocks, fragmentation,
application-payload efficiency, and physical bus expansion are separate
reported views. They are never silently pooled into a single byte count.

## Units and primary estimand

In this ADR, one **byte** is exactly one 8-bit octet. For candidate `c`
and canonical transaction case `i`:

```text
E[c,i] = total octets in every recurring extension block or fragment
         required to carry case i once
```

`E[c,i]` includes all candidate-specific framing, section, record,
semantic-value, delimiter, length, count, subtype, padding, escape,
continuation, fragmentation, and version bytes. It excludes:

- The unchanged opaque application payload.
- I3C address, arbitration, start/stop, and other transport fields that
  would exist in the matched non-EX transaction.
- One-time discovery or negotiation bytes, which are measured
  separately.
- Test-harness, simulator, or host representation bytes.

The primary paired difference is:

```text
delta[i] = E[A,i] - E[B,i]
```

A negative value means Candidate A uses fewer recurring extension
octets; a positive value means Candidate B uses fewer. Also report the
ratio `E[A,i] / E[B,i]` when the denominator is non-zero. A zero
denominator produces `NOT-DEFINED`, not infinity.

## Complete-adapter accounting boundary

Candidate A accounting begins with its preamble and ends after every
ordered active sublayer section from spec section 5.1.5. Candidate B
accounting begins with its first TLV byte and ends after its final record
or required block/continuation signal.

Both encoded forms must pass ADR-0012's complete-adapter semantic gate.
The Candidate A preamble header alone and Candidate B Type/Length bytes
alone are secondary breakdowns, never admissible totals.

No out-of-band state is free. If a decoder needs a schema table,
negotiated length, version mapping, or cached template, the bytes needed
to establish or update that state are recorded under negotiation. If
state must be signalled per transaction, its bytes are part of
`E[c,i]`.

## Byte-attribution map

Each encoder emits or is paired with a machine-readable attribution map
that assigns every encoded extension octet to exactly one category:

- `FRAMING-CONTROL`: preamble, Type, Length, block, continuation, or
  version-control bytes.
- `SUBLAYER-STRUCTURE`: section-internal subtype, count, delimiter,
  reference, or length bytes required by the candidate mapping.
- `SEMANTIC-VALUE`: bytes directly carrying canonical semantic field
  values.
- `PADDING-ALIGNMENT`: padding or alignment bytes.
- `ESCAPE-RESERVED`: escape, reserved-path, or future-version selector
  bytes not already classified as framing control.

Category totals must sum exactly to `E[c,i]`. Attribution is secondary:
the primary result remains the total even when reviewers disagree about
whether a structural byte is framing or semantic. Category values are
compared within a candidate and shown side by side; no category may be
excluded from the total.

## Confirmatory workload corpus

### Comparable core corpus

The primary axis-1 corpus uses ADR-0012's comparable core semantics.
For every capability level EX-1 through EX-6, it contains active-
sublayer prefixes and three semantic profiles:

- `MINIMUM`: the smallest valid canonical instance for every active
  sublayer, including required default values.
- `NOMINAL`: a frozen deployment or trace-derived profile selected
  before candidate encoding. If no empirical trace supports the profile,
  it is labelled `DESIGN-NOMINAL`, not "typical."
- `STRESS`: the largest or densest valid canonical instance in the
  pre-registered common baseline domain, without invoking malformed
  data.

If semantic dimensions are only partially ordered and no unique largest
instance exists, `STRESS` is a pre-registered parameter set covering the
dimension maxima and their required interactions. A convenient single
"large" instance must not replace that set.

Each profile defines semantic fields, record cardinalities, and ordering
independently of framing. Candidate A and Candidate B receive the same
canonical instance digest. EX-0 is retained as a discovery/no-sublayer
control but is reported outside the EX-1 through EX-6 primary summary.

The corpus is stratified by capability level and semantic profile.
Levels and profiles are not assigned artificial population weights.
Every stratum is reported separately before any corpus-wide descriptive
summary.

### Boundary and extensibility cases

ADR-0014 boundary sweeps and confirmatory extensibility scenarios also
record wire metrics using this ADR. Their results are a separate
`EXTENSION-STRESS` stratum and do not alter the primary comparable-core
distribution.

The same shared boundary values are used for both candidates. Cases one
candidate cannot represent remain categorical `UNREPRESENTABLE` results
and are not dropped, assigned zero bytes, or assigned infinite bytes.

### Empirical sequence corpus

If versioned transaction traces become available, the project may add a
pre-registered empirical sequence stratum. Trace selection, filtering,
frequency weights, reset points, and missing-data rules must be frozen
before encoding.

Empirical frequency-weighted totals are reported only for that trace
population and always alongside unweighted stratified results. A trace
added after confirmatory freeze is exploratory unless a superseding ADR
regenerates both candidates' complete result set.

## Application-payload efficiency view

The opaque application payload does not change `E[c,i]`, but it changes
the fraction of transmitted content consumed by extension data. For
application payload length `P`:

```text
extension_fraction[c,i,P] = E[c,i] / (P + E[c,i])
payload_efficiency[c,i,P] = P / (P + E[c,i])
```

When `P + E[c,i]` is zero, both ratios are `NOT-DEFINED`. Report the
complete curve over the configured payload domain and tabulate:

```text
P = 0, every power of two <= Pmax, and Pmax
```

`Pmax` is the frozen application-transport profile limit, identical for
both candidates. Duplicate values are removed. These payload points are
derived views of one extension case, not additional independent corpus
observations.

## Negotiation and session amortisation

For candidate `c`, record candidate-specific one-time negotiation octets
`N[c]` separately from recurring `E[c,i]`. Common discovery fields and
transport overhead that are byte-identical for both candidates are
reported once but excluded from `N[c]`.

For a session of `T` transactions with cases `i_1 ... i_T`:

```text
session_octets[c,T] = N[c] + sum(E[c,i_t], t=1..T)
amortised_octets[c,T] = session_octets[c,T] / T
```

Report session views for `T = 1, 10, 100, 1000, 10000` using a frozen
case sequence or explicitly repeated case. If renegotiation occurs
during a session, its bytes are placed at the actual sequence position,
not hidden inside the one-time term.

Also report candidate break-even session lengths where one candidate's
higher negotiation cost is offset by lower recurring cost. If no finite
break-even exists for a stratum, report `NONE`.

## Fragmentation and multiple transactions

When one canonical case requires several extension fragments or I3C
transactions under the frozen cap profile, `E[c,i]` is the sum of all
candidate extension octets across those fragments. Every repeated
preamble, Type/Length header, fragment identifier, continuation marker,
padding byte, and candidate-specific transaction control byte counts.

Record alongside `E[c,i]`:

- Extension fragment count.
- Added I3C transaction count relative to the matched non-EX transfer.
- Per-fragment extension octets.
- Effective negotiated cap and the peer advertisements producing it.
- Reassembly state bytes, reported under the resource context of the
  relevant methodology ADR.

Common application-payload fragmentation is held identical. A candidate
that cannot carry the case within its allowed extension mechanisms is
`UNREPRESENTABLE`; partial fragments are not counted as successful wire
output.

## Stateless and stateful representations

The primary comparable-core result uses a cold, independently decodable
representation for each transaction unless the baseline specification
normatively requires negotiated state.

Schema caching, table indexes, delta encoding, or other stateful
amortisation is reported in a separate sequence stratum with identical
initial state, reset points, and semantic sequence for both candidates.
Cold-start negotiation and resynchronisation bytes remain visible.
Stateful and stateless totals are not pooled.

## Encoder execution and analytic cross-check

Primary sizes come from retained actual encoder outputs:

```text
E[c,i] = length(concatenate(all successful extension fragments))
```

Every output is stored directly or by content digest with a reproducible
generation command. A separately implemented analytic size function
must agree with actual length for every confirmatory case. A mismatch is
a measurement failure and blocks reporting until resolved.

Wire size is deterministic for a frozen input and configuration.
Repeated encoder executions are correctness checks, not statistical
replicates. Each case is encoded at least twice in clean processes to
detect hidden nondeterminism; differing bytes or lengths fail the
determinism gate.

## Physical bus expansion view

Protocol octets are the primary axis-1 endpoint. A secondary transport
view uses the pinned I3C simulator or RTL environment to record:

- Total bus bits and bus transactions for matched EX and non-EX cases.
- Candidate-attributable added bus bits.
- Address/control/restart overhead caused by candidate-specific extra
  transactions.
- The exact transport mode, bus parameters, simulator revision, and
  trace digest.

Physical bus time belongs primarily to the latency axis. It may be
derived from the bus trace here for context, but it is not converted back
into synthetic "equivalent bytes" or combined with `E[c,i]`.

## Admissibility and fairness gates

A wire-overhead case is admissible only when:

- Both candidates receive the same canonical semantic instance,
  application payload, negotiation state, cap profile, and reset state.
- Successful complete decoders reconstruct equal canonical meaning.
- Python and C produce byte-identical output for the same candidate.
- Every candidate-specific byte needed by the peer is present in the
  counted output or negotiation record.
- No candidate uses a preinstalled schema, hidden length, cached state,
  or fragmentation allowance unavailable to the other under the frozen
  scenario.
- Output is deterministic across clean-process executions.
- Byte-attribution totals equal actual encoded length.
- Analytic and actual sizes agree.

Malformed and rejection-only inputs are excluded from the primary wire
corpus and evaluated under legacy safety. Valid extension cases that are
unknown to an old peer remain admissible extension-stress cases.

## Reporting and comparison

For every case, report actual encoded bytes or digest, `E[A,i]`,
`E[B,i]`, `delta[i]`, ratio, attribution categories, fragment count, and
representability outcome.

For every capability-level/profile stratum, report:

- Case count and categorical exclusions.
- Candidate total octets over the exact stratum.
- Paired win/tie/loss counts.
- Median, interquartile range, minimum, and maximum of paired byte
  differences.
- Empirical cumulative distributions when the stratum contains enough
  cases to make them meaningful.

Across the full unweighted comparable core, report totals and paired
distributions as corpus descriptions, not estimates of a real-world
population. No significance test is applied to deterministic enumerated
sizes.

When both candidates represent every comparable-core case:

- `A-BYTE-DOMINATES` means `E[A,i] <= E[B,i]` for every case and strict
  inequality holds for at least one.
- `B-BYTE-DOMINATES` is the symmetric result.
- `EXACT-TIE` means every paired total is equal.
- Otherwise the result is `MIXED` and reversals are shown by stratum.

If representability differs, report `A-BROADER`, `B-BROADER`, or
`REPRESENTABILITY-MIXED` separately from byte dominance. A candidate's
unrepresentable case is never traded against a byte saving on another
case. The later framing-selection ADR combines axis outcomes.

## Reproducibility manifest

The retained axis-1 manifest contains at least:

- Canonical corpus, schema, trace, and case digests.
- Candidate encoder/decoder and source revisions.
- Capability level, semantic profile, application `Pmax`, cap, and
  negotiation context for every case.
- Exact encoder commands and clean-process environment identifiers.
- Raw encoded outputs or content-addressed artefacts.
- Byte-attribution maps and analytic-size outputs.
- Fragment/transaction records.
- Negotiation/session sequences and amortisation tables.
- Simulator or RTL details for the secondary physical view.
- All exclusions, `NOT-DEFINED`, and `UNREPRESENTABLE` outcomes.

Derived tables and figures must be reproducible from retained outputs
without re-running the encoders.

## Consequences

**Good:**

- Complete semantic representations replace the misleading one-byte-
  versus-two-byte-header comparison.
- Primary totals are mechanically exact and independently reproducible.
- Negotiation, fragmentation, padding, and stateful amortisation remain
  visible rather than being hidden in assumptions.
- Shared semantic and boundary cases make comparisons paired and
  candidate-neutral.
- Deterministic byte data is reported without pseudo-replication or
  unnecessary inferential statistics.
- Stratified results expose workload reversals and payload-size effects.

**Bad:**

- Full sublayer schemas and complete adapters are required before the
  primary corpus can be encoded.
- Byte-attribution maps and analytic cross-checks add implementation
  work beyond simply taking `len(output)`.
- Nominal profiles cannot be called typical without a defensible trace
  or deployment source.
- Fragmentation, negotiation, and stateful sequence views expand the
  experiment matrix.
- The method may produce a mixed outcome instead of one universal byte
  winner.

## Pros and Cons of the Options

### Option A: Header bytes only

- Good: Trivial calculation and easy headline comparison.
- Bad: Compares incomplete Candidate A work with more complete Candidate
  B work.
- Bad: Ignores section delimiters, semantic values, fragmentation, and
  negotiation.

### Option B: Analytic formulas only

- Good: Fast and independent of runtime implementation quality.
- Good: Useful for checking boundary behaviour.
- Bad: Can omit real padding, continuation, or implementation-required
  signalling.
- Bad: Does not prove the representation actually round-trips.

### Option C: Actual complete encodings

- Good: Measures every transmitted extension byte for equal semantics.
- Good: Supports byte-level artefact inspection and analytic validation.
- Good: Integrates naturally with canonical and extensibility corpora.
- Bad: Requires complete production-quality adapters and retained
  outputs.

### Option D: Physical bus bits only

- Good: Closest to actual transport consumption.
- Good: Naturally includes repeated transaction overhead.
- Bad: Conflates framing design with transport mode and simulator
  assumptions.
- Bad: Harder to interpret than protocol-octet differences and overlaps
  latency methodology.

## References

- [`./0002-framing-comparative-prototyping.md`](./0002-framing-comparative-prototyping.md)
  — parent framing-bakeoff decision.
- [`./0009-efficiency-principle.md`](./0009-efficiency-principle.md)
  — mandatory byte-cost accounting discipline.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — complete-adapter equivalence and total-byte rule.
- [`./0014-extensibility-coverage-strategy.md`](./0014-extensibility-coverage-strategy.md)
  — shared boundary and extension-path coverage.
- [`./0015-extensibility-per-scenario-measurements.md`](./0015-extensibility-per-scenario-measurements.md)
  — per-scenario wire context and categorical handling.
- [`./0019-worst-case-latency-measurement.md`](./0019-worst-case-latency-measurement.md)
  — separate CPU-latency and secondary end-to-end timing views.
- [`./0020-throughput-impact-measurement.md`](./0020-throughput-impact-measurement.md)
  — physical-bit reconciliation and effective-payload goodput derived
  from this ADR's complete encodings.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — wire-overhead
  comparison criterion.
