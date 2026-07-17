# ADR-0011: Python-plus-C side-by-side runtime evidence

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

ADR-0010 requires all six framing-bakeoff axes to be evaluated with a
pre-registered methodology. The reference implementation is Python,
but Paper 1 makes claims about an embedded protocol whose normative
Efficiency Principle names a Cortex-M0 as the constrained reference
target. Python-only timing would be reproducible and useful to package
users, but it would not support claims about decoder cost on the target
device class. C-only timing would be target-relevant, but it would omit
the behaviour and performance of the project's maintained reference
implementation.

The bakeoff therefore needs a cross-cutting rule for relating Python
and C evidence without treating different languages and execution
environments as statistical replicates or allowing one candidate to
receive more optimisation than the other.

## Decision Drivers

- Target validity: embedded-performance claims require measurements
  from code suitable for the Cortex-M0 reference target.
- Reference-implementation relevance: Python remains a supported,
  maintained, and independently useful implementation.
- Fairness: preamble and TLV candidates must receive equivalent
  semantics, workloads, validation, and optimisation effort.
- Interpretability: results from different languages must remain
  separate; a cross-language average has no defensible meaning.
- Reproducibility: toolchains, flags, workloads, seeds, raw samples,
  and environment details must be captured before results are
  interpreted.
- Drift prevention: Python and C implementations must be proven to
  accept, reject, and encode the same wire language before their
  performance results are compared.

## Considered Options

- Option A: Benchmark only the Python reference implementation.
- Option B: Benchmark only a C implementation on the embedded
  reference target.
- Option C: Benchmark both implementations, report results separately,
  and designate C-on-Cortex-M0 evidence as primary for embedded runtime
  claims.
- Option D: Benchmark both implementations and combine their results
  into one aggregate score.

## Decision Outcome

Chosen option: **Option C — measure Python and C side by side, report
them as separate evidence streams, and use C-on-Cortex-M0 measurements
as the primary evidence for embedded runtime claims**.

Python results are secondary evidence describing the maintained
reference implementation. They are not a proxy for microcontroller
performance. C results do not replace Python results, and the two
languages are never pooled, averaged, or counted as independent
replicates of one population.

### Scope

This rule applies directly to the runtime axes:

- Axis 5: worst-case latency impact.
- Axis 6: throughput impact.

Axis 2 (parse complexity) must analyse the Python and C implementations
separately when its per-axis ADR defines implementation-level static
metrics. The other axes may use both implementations for conformance or
diagnostic evidence, but this ADR does not require runtime timing for
axes 1, 3, or 4.

### Primary and secondary evidence

For every runtime endpoint:

1. **Primary embedded result**: cycles or a quantity derived from
   cycles, measured using C code compiled for the Cortex-M0 reference
   target. The per-axis ADR must pre-register the timing backend,
   compiler, version, flags, optimisation level, and target settings.
2. **Secondary reference result**: elapsed time or throughput from the
   Python implementation under a pinned CPython and host environment.
   The per-axis ADR must pre-register the interpreter, version, host
   controls, warm-up policy, and sampling procedure.
3. **No cross-language aggregation**: Python and C results appear in
   separate tables, figures, statistical models, and conclusions.
   Normalised candidate ratios may be shown side by side, but they must
   not be averaged into a synthetic score.
4. **Conflict is a result**: if candidate ordering differs between C
   and Python, the outcome is reported as mixed. The C result governs
   only embedded-runtime claims; the Python reversal remains visible
   and must be investigated, not discarded as an outlier.

### Semantic-equivalence gate

Runtime measurements are admissible only after both languages pass the
same semantic corpus for both framing candidates. The gate requires:

- All normative specification vectors.
- A versioned generated corpus of valid boundary cases.
- A versioned malformed-input corpus covering every specified rejection
  class.
- Within each candidate, byte-for-byte equality between Python and C
  for successful encodes of the same semantic input.
- Record-for-record equality for successful decodes.
- Matching accept/reject classification for invalid inputs. Exception
  text and language-specific error types need not match.

The corpus generator, its seed or exhaustive bounds, and the corpus
digest are experiment inputs. A semantic mismatch blocks the affected
runtime comparison until it is fixed or explicitly scoped out by a
superseding methodology decision.

### Fair-implementation rules

The two framing candidates must be treated symmetrically within each
language:

- Expose equivalent operations and enforce the same normative checks.
- Process the same ordered semantic workload instances and, when
  applicable, the same opaque application-payload bytes.
- Use the same allocation policy within a language. Timed C regions
  must not allocate from the heap; buffers and capacity are supplied by
  the harness.
- Apply an optimisation to both candidates when it is structurally
  available to both. Candidate-specific optimisations are permitted
  only when they arise from the wire format itself and are documented.
- Keep validation checks enabled in timed production paths. A candidate
  may not win by omitting required rejection behaviour.
- Exclude corpus generation, fixture loading, logging, and result
  serialisation from timed regions for both candidates.
- Freeze benchmark code and measurement manifests before collecting
  the result set used for selection. Post-freeze changes require a new
  manifest version and a complete rerun of both candidates.

Shared helper code is allowed when it represents genuinely shared work.
It must not force one format through an unnatural abstraction that
inflates its measured cost.

### Measurement manifests and retained artefacts

Each per-axis runtime ADR must define the exact statistic, sampling
unit, repetition policy, workload strata, and uncertainty treatment.
Every executed benchmark must additionally retain a machine-readable
manifest containing at least:

- Source revision and dirty-tree status.
- Workload/corpus version and digest.
- Python interpreter and dependency versions.
- C compiler, linker, flags, and produced-binary digest.
- Target, simulator, emulator, or hardware identifiers and versions.
- Host operating system and relevant processor information.
- Random seeds and execution order.
- Warm-up, repetition, timeout, and exclusion rules.
- Raw observations before aggregation.

Both candidates must be run under the same manifest version. Derived
tables and figures must be reproducible from retained raw observations,
without rerunning the benchmark.

### Selection discipline

This ADR does not define a single overall winner or weights across the
six axes. Per-axis ADRs define their estimands and decision rules, and a
later selection ADR combines the pre-registered axis outcomes.

For axes 5 and 6, the C-on-Cortex-M0 endpoint is the primary endpoint.
Python endpoints are reported secondary endpoints and cannot overturn
an embedded-runtime conclusion by arithmetic combination. They can,
however, prevent an unqualified claim that one framing strategy is
universally faster.

## Consequences

**Good:**

- Embedded-performance claims are based on target-appropriate evidence.
- Users of the Python reference package also receive relevant results.
- Differential conformance catches language drift before timing data can
  conceal it.
- Separate reporting prevents statistically meaningless
  cross-language averages.
- A disagreement between environments becomes publishable explanatory
  evidence rather than an inconvenient result.

**Bad:**

- Both framing candidates require maintained C implementations in
  addition to the existing Python implementations.
- The conformance corpus and dual harnesses increase implementation and
  review effort.
- C-target and Python-host results require separate experimental
  controls and analysis pipelines.
- The rule can produce mixed outcomes rather than a simple winner,
  increasing the burden on the later selection ADR.

## Pros and Cons of the Options

### Option A: Python only

- Good: Lowest implementation cost and easiest cross-platform
  reproduction.
- Bad: CPython timing cannot substantiate Cortex-M0 cycle or latency
  claims.
- Bad: Interpreter overhead may dominate small framing operations and
  reverse candidate ordering.

### Option B: C only

- Good: Directly aligned with the embedded reference target.
- Good: Smaller experimental matrix than maintaining two evidence
  streams.
- Bad: Omits the performance of the project's maintained Python
  reference implementation.
- Bad: Removes a useful independent implementation for differential
  conformance.

### Option C: Separate Python and C evidence streams

- Good: Provides both target-valid and package-relevant evidence.
- Good: Explicit primary/secondary roles keep conclusions
  interpretable.
- Good: Shared corpora improve semantic confidence across languages.
- Bad: Highest implementation and experimental cost among the
  non-aggregate options.
- Bad: Cross-language disagreements require additional analysis.

### Option D: Combined Python/C score

- Good: Produces one convenient ranking.
- Bad: Requires arbitrary normalisation and weighting across unrelated
  execution environments.
- Bad: Can hide a target-relevant regression behind a host-language
  improvement.
- Bad: Treats languages as replicates when they are distinct systems.

## References

- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — meta-framework requiring all six axes and pre-registered per-axis
  methods.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical semantic model and complete candidate-adapter boundary.
- [`./0017-parse-complexity-measurement.md`](./0017-parse-complexity-measurement.md)
  — separate Python/C complete-decoder static analysis for axis 2.
- [`./0019-worst-case-latency-measurement.md`](./0019-worst-case-latency-measurement.md)
  — pinned target, timing boundary, load profiles, and separate Python
  endpoint for axis 5.
- [`./0020-throughput-impact-measurement.md`](./0020-throughput-impact-measurement.md)
  — separate C/Python endpoint-capacity and system-goodput evidence for
  axis 6.
- [`./0002-framing-comparative-prototyping.md`](./0002-framing-comparative-prototyping.md)
  — parent decision to implement and compare both framing strategies.
- [`./0009-efficiency-principle.md`](./0009-efficiency-principle.md)
  — Cortex-M0 reference target and quantitative-efficiency discipline.
- `../../../GOVERNANCE.md` — reproducibility and publication-ethics
  requirements.
