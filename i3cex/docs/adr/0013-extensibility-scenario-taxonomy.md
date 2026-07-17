# ADR-0013: Extensibility scenario taxonomy

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

Specification section 5.3 defines framing extensibility as the effort
required to add a new sublayer or record type. Those are necessary
cases, but they are not a sufficient or neutral experimental taxonomy.
A framing format can accommodate a new record kind yet fail when an
existing value crosses a length boundary, when a deployment needs a
sparse sublayer set, or when new semantics require relationships among
records.

A candidate-specific taxonomy would also bias the comparison. Terms
such as "allocate a TLV Type" or "claim a preamble bit" describe a
solution mechanism, not the semantic extension being requested. The
bakeoff must present both candidates with the same semantic change and
then observe how each accommodates it.

ADR-0012 supplies the canonical semantic model and distinguishes the
paired core corpus from the extensibility stress corpus. A stable,
framing-independent taxonomy is now required before selecting scenario
coverage or measurement fields.

## Decision Drivers

- Framing neutrality: scenario definitions must not assume TLV Types,
  preamble levels, or another candidate mechanism.
- Construct coverage: the taxonomy must cover more than the two easiest
  additive changes while remaining bounded enough to implement.
- Reproducibility: every scenario needs stable labels and explicit
  compatibility constraints.
- Diagnostic value: a failure should identify the kind of evolution
  pressure that caused it.
- Separation of concerns: taxonomy, coverage selection, and metric
  selection belong in different ADRs.
- Cross-axis clarity: valid-but-unknown evolution must not be confused
  with malformed-input legacy safety.

## Considered Options

- Option A: Test only "new record type" and "new sublayer," matching
  the two examples in specification section 5.3.
- Option B: Use a flat list of candidate-specific extension mechanisms.
- Option C: Use a faceted semantic taxonomy with one primary change
  family and orthogonal compatibility, pressure, and evolution-budget
  facets.
- Option D: Test the exhaustive Cartesian product of every conceivable
  extension dimension.

## Decision Outcome

Chosen option: **Option C — classify each scenario by one primary
semantic change family, then tag compatibility direction,
representation pressure, negotiation allowance, and evolution budget
separately**.

This taxonomy defines the space of admissible extensibility scenarios.
ADR-0014 selects coverage from that space. ADR-0015 defines the fields
and measurements collected for each selected scenario.

## Primary change families

Every scenario has exactly one primary family. Stable family identifiers
are normative for experiment manifests and result tables.

| Identifier | Primary semantic change | Includes | Excludes |
|------------|-------------------------|----------|----------|
| `EXT-FIELD` | Evolve fields within an existing record kind | Add an optional field; expand a value domain, precision, or enum | New record kinds; instance-size growth with no schema change |
| `EXT-RECORD` | Add a semantic record kind within an existing sublayer | New event, command, report, or record variant | Extra instances of an existing kind; a wholly new sublayer |
| `EXT-CARDINALITY` | Increase the number of existing semantic items | Repeated records, longer collections, multiple instances per transaction | Larger bytes for one item; new item semantics |
| `EXT-SIZE` | Carry a larger instance under an unchanged semantic schema | Values crossing candidate length or block boundaries | Field-schema changes; adding records solely to introduce new meaning |
| `EXT-SUBLAYER` | Add an independently identifiable capability domain | A new EX capability with its own records and negotiation identity | A record added to an existing sublayer; new combinations of existing sublayers |
| `EXT-COMPOSITION` | Change which existing capabilities may appear together | Sparse activation, optional presence, non-prefix combinations | New sublayer semantics; relationships among records already present |
| `EXT-RELATION` | Add grouping or relationships among semantic items | Hierarchy, parent/child grouping, atomic sets, cross-record or cross-sublayer references | Mere repetition or ordering without relationship semantics |
| `EXT-SPACE` | Expand or revise representation/version space itself | Exhausted identifiers, new framing version, escape or continuation namespace | A semantic addition that merely consumes an available identifier |

### Family precedence rules

The following rules keep classifications reproducible when a scenario
could appear to fit several families:

1. Use `EXT-RELATION` when the new meaning is the relationship itself,
   even if that relationship is encoded as a field or record.
2. Use `EXT-COMPOSITION` when the semantic change is only the permitted
   presence combination of already-defined sublayers.
3. Use `EXT-SUBLAYER` for a new independently negotiated capability,
   even though it will contain new record kinds and fields.
4. Use `EXT-RECORD` for a new kind inside an existing sublayer.
5. Use `EXT-FIELD` when the schema of an existing record kind changes.
6. Use `EXT-CARDINALITY` when the schema and item meanings stay fixed
   but more items are allowed.
7. Use `EXT-SIZE` when only the size of an otherwise unchanged semantic
   instance grows.
8. Use `EXT-SPACE` only when representation-space evolution is itself
   the subject. If another semantic family happens to consume the last
   available identifier, retain that semantic family and add a
   namespace-pressure tag.

Compound scenarios should normally be split into atomic scenarios. A
deliberate interaction scenario may retain one primary family and list
secondary deltas, but its results must not be presented as evidence for
an uncovered primary family.

## Compatibility-contract facet

Every scenario declares one compatibility contract before candidate
analysis. The contract describes required old/new peer interaction; it
does not predict whether either candidate will satisfy it.

| Identifier | Required deployment property |
|------------|------------------------------|
| `COMPAT-NEW-READS-OLD` | A new reader accepts valid baseline-version data from an old writer. |
| `COMPAT-OLD-HANDLES-NEW` | An old reader handles valid extended data using the scenario's specified skip, preserve, or explicit-reject rule without misinterpretation. |
| `COMPAT-MIXED-FLEET` | Both directions above are required during one deployment window. |
| `COMPAT-COORDINATED` | Old/new interoperability is not required; peers upgrade together behind an explicit version boundary. |

For `COMPAT-OLD-HANDLES-NEW`, the scenario must state which outcome is
semantically acceptable. "Safely handles" is not automatically
equivalent to "silently skips": some extension semantics require the old
peer to reject the complete transaction rather than process an unsafe
partial meaning.

This facet covers valid data emitted by a conforming newer writer.
Malformed or adversarial encodings belong to the legacy-safety axis,
even when they use reserved space associated with an extension.

## Representation-pressure facet

Each scenario carries one or more pressure tags. Tags identify the
wire-format property stressed by the semantic change and may differ
from the primary family.

| Identifier | Pressure represented |
|------------|----------------------|
| `PRESSURE-NONE` | No specific representation boundary or evolution pressure is intentionally stressed. |
| `PRESSURE-VALUE-LENGTH` | One semantic value approaches or crosses an encoded value-length boundary. |
| `PRESSURE-BLOCK-LENGTH` | The aggregate extension block approaches or crosses its negotiated or representable cap. |
| `PRESSURE-LOCAL-NAMESPACE` | Identifiers within one existing sublayer or record namespace are scarce or exhausted. |
| `PRESSURE-GLOBAL-NAMESPACE` | Sublayer, capability-level, or global framing identifiers are scarce or exhausted. |
| `PRESSURE-SPARSE` | The requested active set is non-prefix or otherwise has gaps. |
| `PRESSURE-HIERARCHY` | Correct meaning requires grouping depth or parent/child structure. |
| `PRESSURE-UNKNOWN-VALID` | A conforming old reader encounters a valid extension it does not understand. |
| `PRESSURE-NEGOTIATION` | Correct interpretation depends on state established before the transaction. |
| `PRESSURE-VERSION-SIGNAL` | The extension requires an in-band or negotiated version discriminator. |

No-pressure scenarios are tagged `PRESSURE-NONE` explicitly in the
manifest; that tag is mutually exclusive with every specific pressure
tag. A scenario must use the same canonical values for both candidates.
When candidate boundaries differ, a shared size or identifier sweep
must span the union of relevant boundaries; candidate-specific
replacement values are forbidden.

## Evolution-budget facet

Every scenario fixes the design freedom available to each candidate.
The tiers are cumulative and prevent post-hoc use of a more disruptive
mechanism for the candidate that otherwise struggles.

| Identifier | Allowed design changes |
|------------|------------------------|
| `BUDGET-V01` | Use only the current v0.1 grammar, currently valid values, and already-negotiated state. Reserved values remain reserved. |
| `BUDGET-RESERVED-PATH` | `BUDGET-V01` plus documented reserved-bit, reserved-value, escape, continuation, or compatible negotiation paths that do not reinterpret valid v0.1 traffic. |
| `BUDGET-MAJOR-REVISION` | An explicit incompatible framing revision and coordinated migration may be designed. |

The budget limits representation design, not implementation effort. A
candidate may require new encoder, decoder, schema, or negotiation code
within a budget; ADR-0015 will record that work.

## Negotiation-allowance facet

Every scenario declares exactly one negotiation allowance:

| Identifier | Allowed negotiation |
|------------|---------------------|
| `NEGOTIATION-NONE` | The extension must be interpreted from in-band bytes and fixed baseline context. |
| `NEGOTIATION-EXISTING` | Existing EX-Discovery fields or already-defined schema state may be used without adding a new exchange. |
| `NEGOTIATION-NEW` | A new negotiation field or exchange may be introduced and its cost must be retained. |

Negotiation allowance and evolution budget are independent. For
example, a scenario can allow a new compatible negotiation exchange
under `BUDGET-RESERVED-PATH`, or require no negotiation despite allowing
a major revision.

## Candidate accommodation vocabulary

After a scenario is frozen, each candidate records one or more actual
accommodation mechanisms using this common vocabulary:

- `CURRENT-GRAMMAR`: the extension fits the unmodified v0.1 framing
  grammar.
- `RESERVED-EXTENSION`: a documented reserved or escape path is
  standardised.
- `SCHEMA-NEGOTIATION`: negotiated schema or table state is required.
- `NEW-FRAMING-VERSION`: an incompatible or version-gated wire grammar
  is required.
- `UNREPRESENTABLE`: no mapping satisfies the scenario contract within
  its budget and negotiation allowance.

These labels are descriptive, not an ordinal score. A mechanism is not
automatically better because it appears earlier in the list, and a
candidate may use multiple mechanisms. `UNREPRESENTABLE` is mutually
exclusive with all other mechanism labels. ADR-0015 defines how effort
and other observations are recorded.

`UNREPRESENTABLE` describes the design under the scenario constraints,
not missing code. Lack of an implementation is recorded separately and
cannot substitute for a representability analysis.

## Scenario record requirements

Every selected extensibility scenario must be machine-readable and
contain at least:

- Stable scenario identifier and taxonomy version.
- Exactly one primary family.
- Canonical baseline and extended semantic instances or generators.
- A precise semantic delta statement.
- Compatibility contract and acceptable old-peer behaviour.
- One or more representation-pressure tags, using `PRESSURE-NONE` only
  when no specific pressure applies.
- Evolution budget and negotiation allowance.
- Required negotiation or version context.
- Success, explicit-rejection, and `UNREPRESENTABLE` predicates.
- Links to candidate analyses and retained implementation patches once
  those exist.

Scenario definitions must not name a candidate mechanism in the
semantic delta. Mechanisms appear only in candidate outcome fields.

### Illustrative classification examples

These examples demonstrate classification only; they do not constitute
the coverage set selected by ADR-0014.

1. Add a temperature-uncertainty field to an existing confidence
   record: `EXT-FIELD`, `COMPAT-MIXED-FLEET`,
   `PRESSURE-UNKNOWN-VALID`, `BUDGET-V01`,
   `NEGOTIATION-NONE`.
2. Add a new disagreement-detail report to EX-3: `EXT-RECORD`,
   `COMPAT-OLD-HANDLES-NEW`, `PRESSURE-LOCAL-NAMESPACE`,
   `BUDGET-RESERVED-PATH`, `NEGOTIATION-NONE`.
3. Carry the same provenance item at sizes spanning 127 and 128 bytes:
   `EXT-SIZE`, `COMPAT-NEW-READS-OLD`,
   `PRESSURE-VALUE-LENGTH`, `BUDGET-RESERVED-PATH`,
   `NEGOTIATION-NONE`.
4. Activate EX-1 and EX-5 without EX-2 through EX-4:
   `EXT-COMPOSITION`, `COMPAT-MIXED-FLEET`, `PRESSURE-SPARSE`,
   `BUDGET-RESERVED-PATH`, `NEGOTIATION-EXISTING`.

## Scope boundaries

The following are not primary extensibility scenarios:

- Malformed, truncated, contradictory, or adversarial wire input;
  these belong to legacy safety.
- A pure implementation refactor with unchanged wire and canonical
  semantics.
- Runtime optimisation without a new semantic capability.
- Candidate-specific wire bytes chosen before the canonical semantic
  delta is defined.
- Removal or silent reinterpretation of existing valid semantics.
  These may be used as explicit breaking-change controls under
  `BUDGET-MAJOR-REVISION`, but are not evidence of additive
  extensibility.

Wire bytes, code change, parse complexity, latency, and throughput may
be measured for an extensibility scenario, but they remain observations
under their respective axes rather than new taxonomy families.

## Consequences

**Good:**

- Candidate mechanisms are evaluated against neutral semantic changes.
- Stable families and facets support auditable coverage selection and
  stratified reporting.
- Length, namespace, sparse-set, hierarchy, and negotiation pressures
  cannot disappear behind two easy additive examples.
- Compatibility expectations and allowed design freedom are fixed
  before candidate analysis.
- Valid unknown extensions are cleanly separated from malformed-input
  legacy safety.

**Bad:**

- Scenario authoring requires more metadata and review than a flat list.
- Facets create a large potential combination space that ADR-0014 must
  reduce without losing important interactions.
- Primary-family precedence occasionally simplifies a genuinely
  compound evolution request.
- Accommodation labels still require later effort metrics; the taxonomy
  alone cannot rank candidates.

## Pros and Cons of the Options

### Option A: Two specification examples only

- Good: Directly matches the current wording of section 5.3.
- Good: Small and inexpensive scenario set.
- Bad: Misses boundary, composition, hierarchy, and version evolution.
- Bad: A candidate can appear extensible by succeeding only on its
  natural cases.

### Option B: Candidate-specific mechanism list

- Good: Easy to map to concrete implementation tasks.
- Bad: Presents different semantic questions to each candidate.
- Bad: Rewards availability of named mechanisms rather than delivered
  extension meaning.

### Option C: Faceted semantic taxonomy

- Good: Candidate-neutral and compatible with ADR-0012's canonical
  model.
- Good: Separates semantic family from compatibility and boundary
  pressure.
- Good: Supports principled coverage reduction in ADR-0014.
- Bad: More complex than a flat list and requires classification rules.

### Option D: Exhaustive Cartesian product

- Good: Maximum nominal interaction coverage.
- Bad: Most combinations are invalid, redundant, or infeasible.
- Bad: Experimental volume grows combinatorially and obscures the
  primary research question.

## References

- [`./0002-framing-comparative-prototyping.md`](./0002-framing-comparative-prototyping.md)
  — parent decision requiring an empirical framing comparison.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical semantic model and comparable/stress corpus split.
- [`./0018-legacy-safety-measurement.md`](./0018-legacy-safety-measurement.md)
  — malformed-input safety methodology kept separate from valid-unknown
  extensibility.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — extensibility
  comparison criterion.
- [`./0014-extensibility-coverage-strategy.md`](./0014-extensibility-coverage-strategy.md)
  — taxonomy coverage strategy.
- [`./0015-extensibility-per-scenario-measurements.md`](./0015-extensibility-per-scenario-measurements.md)
  — per-scenario measurement set.
