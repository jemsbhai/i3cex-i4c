# ADR-0017: Parse-complexity measurement

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

Specification section 5.3 names receiver-decoder cyclomatic complexity
as the parse-complexity criterion. Measuring only the current functions
would be invalid: Candidate A currently parses one preamble byte and
returns the remaining body, while Candidate B parses a complete TLV
block. ADR-0012 therefore requires complete receiver adapters that
recover the same canonical semantic transaction.

Cyclomatic complexity alone is also incomplete. Function splitting adds
baseline cyclomatic units, while table-driven dispatch can move apparent
complexity from branches into state or data tables. A decoder can have a
low source-level score yet require many parser states, transitions,
lookahead bytes, or validation predicates. Conversely, runtime cycles
measure latency rather than structural parse complexity.

The bakeoff needs a deterministic, language-separated methodology that
measures complete decoder structure without allowing required rejection
logic or data-driven dispatch to disappear from the accounting.

## Decision Drivers

- Measure the complete receiver path from candidate bytes to canonical
  semantics or a normative error.
- Preserve the specification's cyclomatic-complexity endpoint while
  exposing function-splitting and table-driven effects.
- Include required validation and rejection logic.
- Keep Python and C results separate; do not compare raw complexity
  numbers across languages.
- Use C as the primary embedded-implementation evidence and Python as a
  separately reported reference-implementation result.
- Measure identical enabled semantics and capability profiles.
- Use deterministic static data and exact inventories, not timing or
  statistical replication.
- Require branch/grammar coverage so unreachable or untested complexity
  cannot distort the result.

## Considered Options

- Option A: Measure cyclomatic complexity of the currently implemented
  header/framing functions only.
- Option B: Measure only total cyclomatic complexity of complete
  decoders.
- Option C: Measure complete decoders with cyclomatic, decision-surplus,
  maximum-function, control-nesting, grammar, dispatch, state,
  transition, lookahead, and rejection metrics.
- Option D: Use decode cycles as a proxy for parse complexity.

## Decision Outcome

Chosen option: **Option C — measure complete semantic receiver adapters
with a code-level cyclomatic profile and a separately audited structural
parser inventory**.

C and Python are analysed independently. The C result is primary for
embedded complexity claims; Python remains a required parallel result.
No cross-language average or synthetic common scale is produced.

## Measured receiver boundary

For candidate `c` and language `l`, the measured receiver begins at the
public production entry point accepting one complete candidate extension
representation and ends when it returns either:

- The canonical semantic transaction required by ADR-0012, or
- A normative structured rejection.

The measured reachable call graph includes:

- Candidate framing/header parsing.
- Section, record, subtype, length, and dispatch logic.
- Sublayer Value/section decoding needed to construct canonical fields.
- Version, negotiation-state, cap, and schema-table interpretation.
- Fragment reassembly and continuation handling when enabled.
- Every normative validation and rejection path.
- Candidate-specific production helpers and generated production parser
  code reached by the entry point.

It excludes:

- I3C transport/address parsing common to matched EX and non-EX paths.
- Encoders.
- Logging, tracing, benchmark instrumentation, and CLI wrappers.
- Test, fixture, fuzzing, and corpus-generation code.
- Dead production code proven unreachable in the frozen configuration.

Shared semantic helpers that are byte-identical and reached by both
candidates are included in both absolute totals and also reported as a
`COMMON-SEMANTIC` component. Candidate-specific totals are shown with and
without that common component. A helper is not declared common merely
because it has a similar name or purpose.

## Frozen configurations

Complexity is measured for these receiver configurations in both
languages:

1. `NO-EX-BASELINE`: matched legacy/application receiver without an
   extension adapter.
2. `LEVEL-1` through `LEVEL-6`: receivers configured to support the
   corresponding monotonic EX-1..EX-N semantic prefix.
3. `FULL-EX6`: the primary v0.1 receiver with all six baseline sublayers
   and strict validation enabled.
4. `EXTENSION-PATCH`: standalone ADR-0015 confirmatory extension patches,
   reported separately from core absolute complexity.

If the production library uses one dynamic `FULL-EX6` binary rather
than compile-time level variants, the per-level profiles are generated
through a documented build/configuration mechanism or reported as
`NOT-SEPARATELY-CONFIGURABLE`. Dead-code editing solely to manufacture a
level result is prohibited.

Candidate A and Candidate B configurations must enable identical
canonical semantics, caps, version rules, and rejection obligations.
Sparse or future-version semantics appear only in their pre-registered
extension scenarios.

## Code-level cyclomatic profile

### Primary extraction tool

A pinned Lizard release and configuration is the primary cyclomatic-
complexity extractor for authored Python and C production source. The
manifest records the exact version, command, language mode, ignore
rules, and raw output. Both candidates use the same tool version within
a language.

Before measurement, the tool configuration is validated against retained
hand-worked fixtures containing straight-line code, single and multiple
decisions, loops, exception/error branches, dispatch cases, and nested
control flow. Expected and observed fixture scores must match the frozen
counting policy.

Authored C parser control flow must not be hidden in preprocessor macros.
If macro- or generator-produced decision logic is unavoidable, retain
the generated project-only expansion and analyse it as a separate
`GENERATED-PARSER` component in addition to authored source. System
headers are excluded.

Primary receiver totals combine reachable authored and generated parser
components without double-counting generator source that is not present
in the production receiver. The two components and their combined total
are all reported.

### Cyclomatic measures

For every reachable production function `f`, record its cyclomatic
complexity `V[f]`. For a measured call graph with `F` functions:

```text
V_sum = sum(V[f])
decision_surplus = sum(V[f] - 1) = V_sum - F
V_max = max(V[f])
```

Record:

- Reachable production function count `F`.
- `V_sum`.
- `decision_surplus`.
- `V_max` and the owning function.
- Full per-function complexity distribution.
- Count of functions above the pre-registered project threshold.
- Candidate increment over `NO-EX-BASELINE`.
- Increment from `LEVEL-(N-1)` to `LEVEL-N` where configurations exist.

`decision_surplus` is the primary aggregate cyclomatic measure because
it removes the automatic `+1` contributed by every function. `V_sum`,
`F`, and `V_max` remain mandatory so function splitting cannot disappear
from review.

### Control-shape context

For reachable candidate production code, also record:

- Maximum lexical control-nesting depth.
- Mean and maximum function length in logical source lines.
- Public receiver/API symbols added relative to `NO-EX-BASELINE`.
- Recursive receiver functions and maximum permitted recursion depth.
- Exception/error exits and early returns.

These are context metrics, not added to cyclomatic values.

## Structural parser inventory

Source-level branching is supplemented by a machine-readable parser
inventory reviewed against the wire grammar and decoder implementation.
For each candidate/configuration, record:

- Wire-grammar productions and alternatives reached.
- Candidate-specific variable-length constructs.
- Type, level, subtype, or schema dispatch entries.
- Independent normative validation/rejection predicates.
- Persistent parser-state values retained across input consumption or
  calls.
- State transitions, including error transitions.
- Maximum required lookahead octets before a parse decision.
- Maximum candidate-specific buffering octets before semantic delivery.
- Maximum supported framing/grouping nesting depth.
- Required parse passes over the same extension bytes.

### Inventory definitions

- A **dispatch entry** is one distinct recognised selector-to-handler
  mapping. Contiguous selector ranges count per semantic handler, not per
  numeric value, unless values have distinct behaviour.
- A **validation predicate** is one independently falsifiable normative
  condition whose failure selects rejection or fallback behaviour.
  Repeated checks of the same invariant in several functions are
  reported as one semantic predicate plus their code locations.
- A **persistent parser state** is a distinguishable control value that
  must survive between octets, fragments, transactions, or calls. Local
  straight-line phases that do not survive an input boundary are not
  counted as persistent states.
- A **state transition** is an allowed ordered pair of persistent states
  under a distinct input/event class. Impossible pairs are excluded and
  documented.
- **Lookahead** is the maximum number of unread extension octets that
  must be available before the decoder can choose the next grammar
  action without rollback.
- **Buffering** is candidate-specific data retained solely because the
  grammar cannot yet deliver canonical semantics; application payload
  and common transport buffers are excluded. The maximum is taken over
  the frozen cap/configuration domain. A receiver without a finite bound
  records `UNBOUNDED` and cannot be treated as numerically smaller.
- A **parse pass** is a complete or partial revisit of already-consumed
  extension bytes. Reading a byte once for framing and once again for
  semantic decoding counts as two passes over that region unless the
  operations occur in one fused traversal.

Every inventory item links to a stable grammar requirement and source
location. Table rows, generated states, and schema entries count even
when they replace `if` or `switch` branches. This prevents a data-driven
implementation from appearing complexity-free.

## Primary per-language complexity vector

For each language, the primary paired vector is:

1. `decision_surplus`.
2. `V_max`.
3. Dispatch-entry count.
4. Validation-predicate count.
5. Persistent parser-state count.
6. State-transition count.
7. Maximum lookahead octets.
8. Maximum candidate-specific buffering octets.
9. Maximum parse passes.

Lower is interpreted as structurally simpler only after semantic,
compatibility, and quality gates pass. Coordinates are not weighted or
summed. Grammar-production and nesting metrics remain required context
but are excluded from the primary vector because sublayer-common grammar
can dominate them without distinguishing framing candidates.

For Pareto comparison, any finite buffering bound is better than
`UNBOUNDED`, and two `UNBOUNDED` values are equal on that coordinate.
A `NOT-APPLICABLE` or missing coordinate blocks a paired dominance result
rather than being converted to zero.

For a language:

- `A-COMPLEXITY-DOMINATES` means Candidate A is no worse on all nine
  coordinates and strictly better on at least one.
- `B-COMPLEXITY-DOMINATES` is symmetric.
- `EXACT-TIE` means all coordinates are equal.
- Otherwise the result is `MIXED`.

The C vector determines the primary embedded-complexity result. The
Python vector is reported independently:

- Matching dominance directions produce `LANGUAGE-CONSISTENT-A` or
  `LANGUAGE-CONSISTENT-B`.
- A reversal or dominance in only one language produces
  `LANGUAGE-MIXED` with both vectors shown.
- Exact ties in both produce `LANGUAGE-EXACT-TIE`.

A C result must not be described as universally simpler when Python
reverses it.

## Coverage and dynamic validation

Static complexity is admissible only when the frozen valid and invalid
corpora exercise the measured receiver adequately:

- Every wire-grammar alternative has at least one valid or normative
  rejection case.
- Every dispatch entry has a retained case.
- Every validation predicate has one passing and, when semantically
  constructible, one failing case.
- Every persistent state and allowed transition is exercised.
- Candidate-specific receiver code reaches 100% line and branch coverage
  in Python and the C host-test build, excluding only proven unreachable
  defensive paths listed in the manifest.
- All canonical comparable-core cases round-trip.
- Python and C agree on output bytes, canonical results, and rejection
  classes for the same candidate.

Coverage does not reduce the static score; it establishes that the
reported structure is real and tested. Missing cases block the
confirmatory result rather than causing unexercised branches to be
deleted from the count.

Malformed-input cases used to exercise rejection predicates remain part
of the complexity coverage gate. Their behavioural safety outcome is
analysed under axis 4, not inferred from branch count.

## Fairness and admissibility rules

- The measured entry points must implement the same canonical semantics
  and normative rejection obligations.
- Strict validation remains enabled. A candidate cannot lower complexity
  by omitting required checks.
- Candidate-specific helpers reachable from the decoder are included,
  even when placed in another module or translation unit.
- Shared helpers must be demonstrably identical and are never subtracted
  from only one candidate.
- Generated and table-driven production logic remains visible through
  generated-code and structural inventories.
- Debug, logging, metrics, and benchmark instrumentation are disabled or
  excluded symmetrically.
- Complexity-reducing refactors after seeing confirmatory metrics create
  a new implementation revision and require complete remeasurement of
  both candidates. Candidate-specific optimisation variants are
  exploratory unless pre-registered.
- Incomplete adapters are `NOT-COMPLETED`, never assigned the complexity
  of their implemented prefix.
- An `UNREPRESENTABLE` extension scenario retains its categorical result
  and receives `NOT-APPLICABLE` numeric complexity deltas.

## Reporting

For Python and C separately, report:

- Absolute `NO-EX-BASELINE`, `LEVEL-1` through `LEVEL-6`, and `FULL-EX6`
  profiles.
- Candidate increments over the no-EX baseline.
- Per-level increments where configurations exist.
- Common-semantic and candidate-specific components.
- Complete per-function cyclomatic tables and distributions.
- Structural parser inventory with source/grammar links.
- Primary nine-coordinate vectors and dominance labels.
- Quality/coverage gate evidence and exclusions.
- Standalone ADR-0015 extension-patch deltas by taxonomy family.

Static measurements are deterministic for a frozen source revision and
tool configuration. Do not run significance tests or treat functions as
independent population samples. Descriptive medians and ranges across
extension patches may be shown with exact denominators, but Python and C
remain in separate tables.

No single cross-language or code-plus-grammar complexity score is
produced. The later framing-selection ADR combines axis outcomes.

## Reproducibility manifest

Retain at least:

- Candidate, baseline, schema, and configuration revisions.
- Measured entry points and complete reachable-call-graph inventories.
- Source inclusion/exclusion and common-helper classifications.
- Lizard version, commands, fixture validation, and raw output.
- Formatting, preprocessing, generation, and macro policies.
- Per-function cyclomatic records.
- Structural parser inventory and stable grammar/source links.
- Valid/invalid corpus digests and coverage reports.
- Python/C differential-conformance results.
- Every `NOT-SEPARATELY-CONFIGURABLE`, `NOT-COMPLETED`,
  `NOT-APPLICABLE`, and unreachable-path justification.

Derived tables must be reproducible from these retained records without
rerunning source analysis.

## Consequences

**Good:**

- Both candidates are measured at the same complete semantic decoder
  depth.
- Decision surplus preserves cyclomatic information while exposing
  function-splitting effects through separate function totals.
- Structural inventories prevent tables, generated parsers, or state
  machines from hiding complexity.
- Required error handling remains inside the measured boundary.
- Capability-level increments show where complexity enters the stack.
- C and Python conclusions remain interpretable in their actual target
  environments.

**Bad:**

- Complete Python and C sublayer decoders are prerequisites.
- Call-graph classification and structural inventory require manual
  review in addition to automated tooling.
- Nine-coordinate Pareto comparisons will frequently produce mixed
  outcomes.
- Requiring exhaustive grammar/branch coverage adds substantial corpus
  work.
- Lizard scores still reflect language syntax, so cross-language numeric
  comparisons remain prohibited.

## Pros and Cons of the Options

### Option A: Current header/framing functions only

- Good: Can be measured immediately with little tooling.
- Bad: Candidate A and Candidate B perform different semantic work.
- Bad: Omits sublayer, dispatch, and full rejection complexity.

### Option B: Total cyclomatic complexity only

- Good: Directly matches the metric named in the specification.
- Good: Simple to automate and communicate.
- Bad: Sensitive to function decomposition.
- Bad: Table entries, parser state, lookahead, and buffering can remain
  invisible.

### Option C: Cyclomatic plus structural parser inventory

- Good: Retains the specified metric and closes its major blind spots.
- Good: Works for branch-driven, table-driven, and generated decoders.
- Good: Supports auditable within-language paired comparisons.
- Bad: Requires more tooling, definitions, and manual verification.

### Option D: Decode cycles as complexity proxy

- Good: Directly relevant to embedded performance.
- Bad: Conflates structural complexity with compiler, hardware, memory,
  and workload effects.
- Bad: Duplicates worst-case latency methodology rather than measuring
  parse structure.

## References

- [`./0002-framing-comparative-prototyping.md`](./0002-framing-comparative-prototyping.md)
  — parent framing-bakeoff decision.
- [`./0009-efficiency-principle.md`](./0009-efficiency-principle.md)
  — mandatory parse-complexity and Cortex-M0 analysis discipline.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0011-python-c-runtime-evidence.md`](./0011-python-c-runtime-evidence.md)
  — Python/C separation rule and axis-2 static-analysis requirement.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — complete semantic receiver boundary.
- [`./0015-extensibility-per-scenario-measurements.md`](./0015-extensibility-per-scenario-measurements.md)
  — standalone extension-patch complexity deltas.
- [`./0018-legacy-safety-measurement.md`](./0018-legacy-safety-measurement.md)
  — behavioural safety outcomes for the rejection paths inventoried
  here.
- [`./0019-worst-case-latency-measurement.md`](./0019-worst-case-latency-measurement.md)
  — runtime slow-path search seeded by this ADR's structural inventory.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — parse-complexity
  comparison criterion.
