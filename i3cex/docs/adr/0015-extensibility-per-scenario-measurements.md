# ADR-0015: Extensibility per-scenario measurement set

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

ADR-0013 defines what kinds of extensibility changes are evaluated, and
ADR-0014 defines how confirmatory scenarios are selected. Neither
defines what "effort to accommodate" means for one scenario.

Extensibility cannot be represented honestly by one convenient number.
Lines changed omit specification and compatibility burden. Elapsed time
is dominated by implementer familiarity, tooling, and AI assistance.
Wire bytes and cycles matter, but they answer other bakeoff axes. A
categorical statement that a format "supports" an extension hides
whether it requires a new version, negotiation state, substantial
decoder changes, or unsafe old-peer behaviour.

The project needs an exact, auditable measurement bundle for every
confirmatory scenario and candidate, plus rules for paired reporting
that do not collapse unlike evidence into an arbitrary score.

## Decision Drivers

- Representability and compatibility must be reported before change-
  size metrics.
- Specification, Python, and C evidence must remain separable.
- Production, validation, generated, and harness changes must not be
  conflated.
- Every metric needs a frozen baseline and reproducible extraction rule.
- `UNREPRESENTABLE`, incomplete implementation, and zero-change support
  are distinct outcomes.
- Quality gates must prevent a small but incomplete patch from appearing
  more extensible.
- Human/AI implementation time is useful provenance but too confounded
  to be a primary endpoint.
- Scenario and family summaries must retain mixed results rather than
  manufacture a universal ranking.

## Considered Options

- Option A: Use expert ordinal ratings such as easy/medium/hard.
- Option B: Use source lines changed as the sole effort metric.
- Option C: Use active implementation time as the sole effort metric.
- Option D: Use a multidimensional, quality-gated change record with
  categorical outcomes, specification and implementation deltas,
  compatibility, resource context, and provenance.

## Decision Outcome

Chosen option: **Option D — every candidate/scenario result is a
quality-gated measurement bundle containing categorical accommodation
and compatibility outcomes, normative-specification delta, separate
Python and C production/validation changes, static-complexity delta,
state and negotiation requirements, wire context, and implementation
provenance**.

No weighted extensibility score is computed. Scenario-level paired
dominance and family-level descriptive summaries are permitted under
the rules below; the later framing-selection ADR decides how the
extensibility axis contributes to the overall bakeoff.

## Experimental patch protocol

### Frozen standalone baselines

Primary change measurements use **standalone scenario patches**. Each
candidate's patch starts from the same frozen semantic/schema baseline
and includes only the changes required for one scenario template. A
scenario implemented earlier must not make a later scenario appear
cheaper through accumulated helper code.

The baseline contains:

- The canonical semantic schema and instances required by ADR-0012.
- Complete baseline Candidate A and Candidate B adapters in Python and
  C.
- Shared conformance vectors and quality tooling.
- No selected scenario's extension semantics or candidate-specific
  accommodation code.

Candidate A and Candidate B patches may use their existing accepted
extension mechanisms. Shared scenario-independent prerequisites found
after freeze must either be applied identically to both baselines and
excluded from both measurements through a superseding manifest, or
remain charged to the candidate patch that requires them.

Cumulative portfolio implementations may be studied as exploratory
evidence for mechanism reuse, but they do not replace standalone
confirmatory patches.

### Pre-registered implementation plan

Before extracting any change or runtime metric, each candidate receives
one short implementation plan identifying:

- The canonical semantic mapping.
- Proposed ADR-0013 accommodation mechanism labels.
- Expected specification, Python, C, validation, and negotiation touch
  points.
- Any anticipated incompatibility or representability limit.
- Alternatives considered and the candidate-neutral reason for the
  selected design.

Once metric extraction begins, switching to another implementation to
improve observed results is prohibited. Alternative implementations may
be reported as exploratory patches. Correctness fixes to the selected
plan are allowed and remain in the measured change set.

### Patch hygiene

All source is formatted before comparison. Mechanical renaming,
unrelated cleanup, dependency upgrades, and broad refactors are excluded.
If an unavoidable refactor benefits both candidates, it becomes a
separate baseline prerequisite before confirmatory patching.

Renames are detected with content similarity and counted by their
content delta, not as delete-plus-recreate. Generated artefacts are
reported separately and excluded from authored change totals. Tool
versions, ignore rules, and artifact classifications are pinned in the
measurement manifest.

## Required measurement bundle

Every confirmatory scenario template produces one bundle per candidate.
Parameterised boundary cases remain children of that template; they do
not create additional implementation-effort observations.

### 1. Identity and taxonomy

- Scenario template ID and manifest digest.
- All concrete case IDs and canonical-instance digests.
- ADR-0013 primary family and facets.
- Owning or directly affected sublayer.
- Candidate, source revision, baseline revision, and patch digest.
- Python, C, compiler, analysis-tool, and schema versions.

### 2. Accommodation and completion outcome

For every concrete case, record one of:

- `REPRESENTED`: the candidate encodes and decodes the canonical
  extended meaning within the scenario constraints.
- `UNREPRESENTABLE`: no design mapping satisfies the semantic contract,
  evolution budget, and negotiation allowance.
- `NOT-COMPLETED`: a mapping may exist, but the implementation or
  evidence bundle was not completed.
- `INVALID-SCENARIO`: the frozen case is later shown to be semantically
  incoherent; it remains in the audit trail and follows ADR-0014's
  superseding rules.

The template summary is:

- `FULL`: every required case is `REPRESENTED`.
- `PARTIAL`: at least one, but not all, required cases are
  `REPRESENTED`.
- `NONE`: every valid required case is `UNREPRESENTABLE`.
- `INCOMPLETE`: any required valid case is `NOT-COMPLETED`.
- `INVALID`: the template itself is invalid rather than a candidate
  limitation.

`UNREPRESENTABLE` requires a design analysis naming the first violated
scenario constraint and explaining why each allowed mechanism fails.
It is never encoded as zero changed lines, infinite effort, a timeout,
or an implementation failure. `NOT-COMPLETED` blocks the confirmatory
extensibility analysis from reaching completion.

Numeric implementation, resource, and wire fields that do not exist for
an `UNREPRESENTABLE` case are recorded as `NOT-APPLICABLE`, never zero.
Any attempted prototype is retained as exploratory evidence and does not
become a confirmatory patch metric.

Record all actual accommodation mechanisms using ADR-0013's common
labels. Those labels remain non-ordinal.

### 3. Semantic and compatibility result

For every represented case, record:

- Canonical encode/decode roundtrip: `PASS` or `FAIL`.
- Python/C wire equality for the same candidate: `PASS` or `FAIL`.
- Python/C accept/reject equality: `PASS` or `FAIL`.
- Compatibility-contract result: `PASS`, `FAIL`, or
  `NOT-APPLICABLE`.
- Observed old-reader/new-writer outcome: decode, skip, preserve opaque,
  explicit reject, silent misinterpretation, or crash.
- Observed new-reader/old-writer outcome using the same vocabulary.
- Negotiation/version mismatch outcome where applicable.

A template satisfies its compatibility contract only if every required
case passes. Silent misinterpretation or a crash is always a failure,
even if the scenario permitted explicit rejection.

A represented case whose canonical roundtrip or Python/C differential
check fails is reclassified as `NOT-COMPLETED`; semantic failure cannot
be retained as a smaller but admissible patch.

### 4. Normative specification delta

Before patching, relevant baseline normative requirements and wire-
grammar productions receive experiment-local stable identifiers without
changing their semantics. New requirements and productions receive new
identifiers; modified items retain their identifier.

Record separately:

- Normative requirements added, modified, and removed.
- Normative sections touched.
- Wire-grammar productions added, modified, and removed.
- Identifier or reserved-value allocations consumed.
- Negotiation messages, fields, and state transitions added or changed.
- Explicit compatibility exceptions or version gates added.
- Informative specification lines added and deleted.

The primary normative-change count is:

```text
requirements added + requirements modified + requirements removed
```

The wire-grammar production change count is computed analogously from
productions added, modified, and removed. Allocation, negotiation, and
compatibility counts remain separate; they are not folded into either
number. A human-reviewed mapping from each count to stable identifiers
ships with the result.

### 5. Authored patch surface

For each artifact class, record text lines added, text lines deleted,
and churn (`added + deleted`):

- Python production code.
- Python tests.
- C production code.
- C tests.
- Language-neutral conformance vectors.
- Build and configuration files.
- Benchmark/measurement harness.
- Informative documentation outside the normative specification.
- Generated artefacts.

Also record files touched and functions or callable units touched for
Python production, Python tests, C production, and C tests.

Modified text is represented by its added and deleted lines. Formatters
run first, and whitespace-only changes are rejected by patch review.
Generated artefacts and harness changes remain visible but are excluded
from authored production/validation churn. Python and C values are
never added or averaged together.

Language-neutral conformance-vector churn is reported once. For paired
dominance it is one separate coordinate only when the candidate requires
distinct vectors beyond the shared canonical cases; shared scenario
fixtures do not count against either candidate.

### 6. Static implementation complexity

For Python and C separately, record baseline, extended, and delta for:

- Total cyclomatic complexity in changed production units.
- Maximum per-function cyclomatic complexity in changed production
  units.
- Number of production functions above the project's pre-registered
  complexity threshold.
- Public API symbols added, modified, and removed.
- Decoder/parser states or dispatch cases added.
- Validation/rejection branches added.

The manifest pins language-specific analysis tools and configuration.
Raw tool output is retained. Cross-language complexity values are not
compared numerically; candidate comparisons are made within Python and
within C.

### 7. State, negotiation, and binary-resource context

Record:

- New persistent state bytes per device and per peer.
- Maximum additional caller-provided scratch bytes.
- Whether heap allocation is newly required in the C path.
- Negotiation bytes and round trips added at initialisation.
- Additional version or schema identifiers retained at runtime.
- C binary deltas for `.text`, read-only data, initialised data, and
  zero-initialised data under the pinned Cortex-M0 build.

These are extension consequences, not substitutes for engineering-
change metrics. Binary and state values remain separate from Python
source evidence.

### 8. Wire-size context

For every concrete case, record:

- Baseline and extended extension-block bytes.
- Absolute byte delta and ratio where the baseline is non-zero.
- One-time negotiation bytes separately from per-transaction bytes.
- Any padding, delimiter, escape, continuation, or version bytes.
- The unchanged application-payload length used for throughput context.

All extension-block bytes count, consistent with ADR-0012. These values
feed the wire-overhead axis and explain extensibility mechanisms, but
they are not combined with code change into an extensibility score.

### 9. Validation evidence

A represented patch is admissible only when it includes:

- Canonical baseline and extended roundtrip tests.
- Every boundary case required by ADR-0014.
- Old/new compatibility tests matching the scenario contract.
- Python/C differential vectors for the same candidate.
- Candidate-specific malformed-input tests introduced by the new
  mechanism.
- Passing project lint, format, type, warning, and coverage gates.
- Passing C host sanitiser checks and pinned Cortex-M0 build checks once
  the C implementation exists.

Record tests added, tests modified, conformance vectors added, branch
coverage before/after, and all quality-gate commands and results. Fewer
tests are not treated as lower effort unless both patches satisfy the
same quality and semantic coverage requirements.

### 10. Implementation provenance and secondary time data

Record:

- Implementer identity or agent/system identifier.
- Human, AI-assisted, or mixed implementation mode.
- Model/tool versions, relevant prompt or task digest, and tool access.
- Start, pause, resume, and completion events when active time is
  collected.
- Active implementation minutes, review minutes, and correction minutes
  separately.
- Human interventions and automated tool calls when available.

Time and interaction counts are **secondary provenance only**. They are
not used for scenario dominance, family ranking, or framing selection
because a single project cannot adequately control learning effects,
prompt variation, model updates, and implementer familiarity. Missing
time data does not invalidate otherwise complete static measurements,
but missing assistance provenance must be disclosed.

## Primary paired change vector

When both candidates fully represent a template and pass its semantic,
compatibility, and quality gates, report this primary change vector for
each candidate:

1. Normative requirement change count.
2. Wire-grammar production change count.
3. Python production churn.
4. Python test churn.
5. C production churn.
6. C test churn.
7. Candidate-specific language-neutral conformance-vector churn.
8. Python total cyclomatic-complexity delta.
9. C total cyclomatic-complexity delta.

Lower is interpreted as less change only after quality gates pass.
Python and C remain separate vector coordinates; they are not averaged.
Negative complexity deltas are retained rather than clamped.

For this vector only:

- Candidate A **Pareto-dominates** Candidate B when A is no worse on all
  nine coordinates and strictly better on at least one.
- Candidate B Pareto-dominates under the symmetric rule.
- Equal coordinates produce `EXACT-TIE`.
- Otherwise the result is `MIXED`.

Pareto dominance is a descriptive relationship, not a scalar score. It
does not compare accommodation labels or allow a contract failure to be
traded against fewer changed lines.

If exactly one candidate fully represents and satisfies a template, the
result is `ONLY-A-CONFORMING` or `ONLY-B-CONFORMING`. If either candidate
is `INCOMPLETE`, no confirmatory paired result is declared. Partial
representation is reported case by case and is not converted into
numeric infinity.

## Aggregation and reporting

The confirmatory report presents:

- One complete bundle per scenario template and candidate.
- Case-level representability and compatibility matrices.
- Counts of `FULL`, `PARTIAL`, `NONE`, and compatibility-pass outcomes by
  primary family, always with denominators.
- Counts of `ONLY-A-CONFORMING`, `ONLY-B-CONFORMING`, A dominance, B
  dominance, `EXACT-TIE`, and `MIXED` by family.
- Paired candidate deltas for every continuous metric, by family and
  overall, using median, interquartile range, minimum, and maximum, with
  the number of numeric pairs reported for every summary.
- Separate Python and C tables and figures.
- Separate confirmatory and exploratory results.

Scenario cases in a boundary sweep do not inflate the template count.
For case-varying wire metrics, report every case and a within-template
range. For patch-level metrics, report one observation per standalone
patch.

Continuous paired summaries include only templates for which both
candidates have applicable numeric measurements. Excluded categorical
outcomes and their denominators are shown alongside every summary; they
are not silently dropped or imputed.

The confirmatory portfolio is a designed set, not a random sample from a
defined population. Therefore the primary report is descriptive: it
does not attach population p-values or claim that bootstrap intervals
generalise to every possible protocol extension.

No raw metric is summed across taxonomy families, and no weighted
composite extensibility score is produced. `UNREPRESENTABLE` is retained
as a categorical result and is never imputed into continuous summaries.

## Consequences

**Good:**

- Extensibility evidence covers semantic success, compatibility,
  specification burden, both maintained languages, validation, and
  mechanism consequences.
- Frozen standalone patches prevent scenario-order amortisation from
  biasing primary effort measurements.
- Quality gates prevent incomplete small patches from winning on churn.
- Stable requirement identifiers and artifact classes make deltas
  auditable.
- Pareto reporting exposes clear dominance without arbitrary weights.
- Time and AI-assistance provenance remain visible without becoming a
  confounded primary endpoint.

**Bad:**

- Every scenario requires two production-quality standalone patches,
  each with Python and C implementations and tests when representable.
- Stable normative identifiers, patch classifiers, and metric tooling
  add substantial preparation work.
- A nine-coordinate vector will often produce `MIXED` rather than a
  simple winner.
- Standalone patches intentionally do not credit reuse across multiple
  extensions; cumulative reuse needs separate exploratory analysis.
- Binary/state and wire context expand the artefact even though they do
  not enter the primary change vector.

## Pros and Cons of the Options

### Option A: Expert ordinal rating

- Good: Fast and easy to communicate.
- Bad: Reviewer cannot reproduce an unexplained easy/medium/hard label.
- Bad: Strongly vulnerable to candidate and implementer expectations.

### Option B: Source churn only

- Good: Simple, objective, and easy to automate.
- Bad: Omits specification, compatibility, complexity, state, and
  validation burden.
- Bad: Rewards terse or under-tested implementations.

### Option C: Active time only

- Good: Directly resembles ordinary engineering effort.
- Bad: Confounded by learning, implementation order, tool familiarity,
  AI assistance, interruptions, and model/version drift.
- Bad: Difficult for independent reviewers to reproduce.

### Option D: Multidimensional quality-gated record

- Good: Auditable and robust to the limitations of any one metric.
- Good: Preserves categorical failures and language-specific evidence.
- Good: Supports both detailed scenario review and family-level paired
  summaries.
- Bad: Highest instrumentation, implementation, and reporting cost.
- Bad: Does not guarantee one simple extensibility winner.

## References

- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0011-python-c-runtime-evidence.md`](./0011-python-c-runtime-evidence.md)
  — Python/C separation and differential-conformance discipline.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical semantic and complete-adapter boundary.
- [`./0013-extensibility-scenario-taxonomy.md`](./0013-extensibility-scenario-taxonomy.md)
  — extensibility families, facets, and accommodation labels.
- [`./0014-extensibility-coverage-strategy.md`](./0014-extensibility-coverage-strategy.md)
  — confirmatory scenario coverage and freeze rules.
- [`./0016-wire-overhead-measurement.md`](./0016-wire-overhead-measurement.md)
  — complete-encoding wire-overhead accounting for scenario cases.
- [`./0017-parse-complexity-measurement.md`](./0017-parse-complexity-measurement.md)
  — complete-decoder static metrics for extension-patch deltas.
- [`./0018-legacy-safety-measurement.md`](./0018-legacy-safety-measurement.md)
  — malformed-input, compatibility-recovery, and safety quality gates.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — extensibility
  comparison criterion.
