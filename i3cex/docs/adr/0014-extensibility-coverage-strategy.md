# ADR-0014: Extensibility scenario coverage strategy

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

ADR-0013 defines eight primary extensibility families and four
orthogonal facets. Their full Cartesian product is neither meaningful
nor feasible: many combinations are semantically invalid, while an
exhaustive product would create hundreds of repetitive scenarios.
Selecting one convenient example per family would be inexpensive but
would miss interactions among compatibility requirements, allowable
version changes, negotiation, and representation boundaries.

The project needs a pre-registered coverage strategy that is broad
enough to support a top-tier publication, bounded enough to implement,
and resistant to cherry-picking after either candidate's weaknesses are
known.

## Decision Drivers

- Every primary semantic family must receive more than token coverage.
- Known hard boundaries and documented future-extension paths for both
  candidates must be tested symmetrically.
- Important interactions among compatibility, evolution budget, and
  negotiation must be covered without taking their exhaustive product.
- Candidate limitations must remain in the confirmatory set as
  `UNREPRESENTABLE` outcomes rather than causing scenario deletion.
- Scenario volume must be controlled through parameterised templates,
  not by omitting difficult taxonomy regions.
- Confirmatory evidence used for winner selection must be frozen before
  candidate-specific accommodation work and measurement.
- Additional observations should remain possible as explicitly
  exploratory evidence.

## Considered Options

- Option A: Select one representative scenario per primary family.
- Option B: Evaluate the exhaustive Cartesian product of all taxonomy
  facets.
- Option C: Hand-pick a small risk-based scenario list.
- Option D: Use a hybrid design with mandatory family anchors,
  boundary and reserved-path sweeps, constrained pairwise facet
  coverage, and separate confirmatory/exploratory sets.

## Decision Outcome

Chosen option: **Option D — build the confirmatory portfolio from two
mandatory anchors per primary family, add shared boundary and
documented-extension-path variants, then fill all feasible pairwise
coverage gaps across compatibility contract, evolution budget, and
negotiation allowance**.

The final confirmatory manifest is generated and frozen before
candidate-specific accommodation implementations or measurements. The
strategy defines coverage requirements; ADR-0015 defines the
observations collected from every selected scenario.

## Coverage units

The coverage process distinguishes three units:

- **Scenario template**: one semantic extension request with fixed
  taxonomy facets and parameter definitions.
- **Scenario case**: one concrete parameter assignment within a
  template, such as value size 126, 127, or 128 bytes.
- **Candidate outcome**: one framing candidate's accommodation and
  measurements for one case.

Family and facet coverage are counted by template. Boundary coverage is
counted by concrete case. Multiple parameter values from one template
must not be presented as independent taxonomy-family coverage.

Every template contains a canonical baseline instance and one or more
canonical extended instances per ADR-0012. The baseline/extended pair
is the unit of change; a standalone extended encoding without a
baseline is inadmissible for extensibility effort measurement.

## Mandatory family anchors

The confirmatory portfolio contains at least two distinct templates for
each ADR-0013 primary family. The anchors below define semantic roles,
not candidate wire mechanisms.

| Family | Anchor A | Anchor B |
|--------|----------|----------|
| `EXT-FIELD` | Add an optional field to an existing record kind. | Expand the domain, enum, width, or precision of an existing field. |
| `EXT-RECORD` | Add a valid record kind whose semantics an old peer may safely skip. | Add a valid semantics-critical record kind for which an unaware peer must reject rather than partially process. |
| `EXT-CARDINALITY` | Increase repeated instances of one existing record kind. | Increase items inside an existing semantic collection without changing item meaning. |
| `EXT-SIZE` | Grow one unchanged semantic value across value-length boundaries. | Grow a transaction's unchanged semantic content across aggregate block/cap boundaries. |
| `EXT-SUBLAYER` | Add an independently negotiated sublayer while identifier capacity remains. | Add a sublayer after the baseline global capability/namespace is exhausted. |
| `EXT-COMPOSITION` | Make a previously mandatory tail capability optional while retaining a valid lower prefix. | Request a non-prefix sparse combination with an omitted interior sublayer. |
| `EXT-RELATION` | Add a flat cross-record or cross-sublayer reference. | Add grouping, atomic-set, or parent/child semantics requiring explicit structure. |
| `EXT-SPACE` | Exhaust and extend an existing sublayer-local identifier space. | Exhaust and extend global framing/version space through an explicit escape or new version. |

The two anchors for a family must use different compatibility contracts
unless a pre-registered feasibility constraint demonstrates that only
one contract is semantically coherent. A single template cannot satisfy
both mandatory anchors, even if it contains several parameter cases.

This rule establishes a minimum of 16 confirmatory templates before
pairwise or inventory-driven additions.

## Representation-pressure coverage

Every ADR-0013 pressure label, including `PRESSURE-NONE`, must appear in
at least one confirmatory template.

For non-numeric pressures, the label must appear under two different
primary families when a documented feasibility analysis identifies two
coherent families. If only one family is coherent, the manifest records
that constraint and uses two semantically distinct templates within the
family.

The following labels trigger parameter or inventory rules in addition
to template coverage:

- `PRESSURE-VALUE-LENGTH` and `PRESSURE-BLOCK-LENGTH` trigger numeric
  boundary sweeps.
- `PRESSURE-LOCAL-NAMESPACE` and `PRESSURE-GLOBAL-NAMESPACE` trigger
  identifier-space boundary sweeps.
- `PRESSURE-UNKNOWN-VALID` requires at least one safe-skip/preserve case
  and at least one explicit-reject case.
- `PRESSURE-NEGOTIATION` requires cases using existing and newly allowed
  negotiation, subject to the scenario budget.
- `PRESSURE-VERSION-SIGNAL` requires both an old-reader encounter and a
  version-aware-reader success case.

## Shared boundary-sweep rule

Every finite numeric or ordinal boundary documented by either
candidate, a sublayer grammar, or a negotiated cap is entered into a
versioned boundary inventory. Examples include maximum value length,
block cap, record count, local identifier exhaustion, capability-level
exhaustion, and version/escape thresholds.

For a boundary `b`, the owning template includes at least:

```text
b - 1, b, b + 1
```

All values are included when valid in the canonical semantic domain. At
a lower boundary where `b - 1` is invalid, use `b`, `b + 1`, and `b + 2`.
At a non-numeric namespace boundary, use the penultimate available
identifier, last available identifier, and first request beyond the
baseline namespace.

Boundary cases use the same canonical values for both candidates. When
their encoded boundaries occur at different semantic parameter values,
the shared sweep is the sorted union of both candidates' relevant
values, and both candidates run every case. Candidate-specific values
selected solely to make encoded sizes match are forbidden.

Aggregate encoded-size transitions may not be known until candidate
size functions exist. A structural dry run may locate those transitions
before manifest freeze, but it must not collect timing, code-effort, or
winner-related results. The discovered semantic parameter values and
the size-function revision are retained in the boundary inventory.

## Documented extension-path union

Before scenario generation, the project creates a versioned inventory
of every reserved, escape, continuation, table, bitmap, negotiation, or
version path documented for either candidate. The confirmatory set must
contain at least one semantic template capable of exercising each path
within its declared evolution budget.

This is a **union rule**: paths from both candidates are included. A
scenario is not removed because the other candidate lacks an analogous
mechanism. Both candidates receive the same semantic request; the
result may use a different accommodation mechanism or be
`UNREPRESENTABLE`.

The path inventory is based only on specifications and accepted ADRs,
not on benchmark results or ease of implementation. Adding a new path
after freeze creates exploratory evidence unless a superseding ADR
regenerates and reruns the complete confirmatory portfolio.

## Constrained pairwise facet coverage

After mandatory anchors and inventory-driven templates are assigned
their facets, the portfolio must cover every feasible pair among these
three facets:

- Compatibility contract: 4 values.
- Evolution budget: 3 values.
- Negotiation allowance: 3 values.

Pairwise coverage is evaluated across facet pairs, not across the
primary family or pressure labels. Requiring every family-pressure
combination would recreate an infeasible near-Cartesian design; family
and pressure coverage are governed by their explicit rules above.

A machine-readable feasibility matrix lists every excluded facet pair
and its semantic justification. At minimum, `BUDGET-V01` with
`NEGOTIATION-NEW` is infeasible because `BUDGET-V01` permits only
already-defined state. A tool must not silently infer or discard other
combinations.

Coverage is complete only when the audit reports:

```text
covered feasible pairs / total feasible pairs = 100%
```

Mandatory templates are reused to cover pairs. If gaps remain, the
generator adds the fewest admissible templates it can establish, with
a deterministic lexicographic scenario-ID tie-break. The generator,
solver or algorithm version, constraint input, and output digest are
retained. If global minimality is not proven, the report must say so;
scenario count is an engineering property, not a research outcome.

## Sublayer distribution

Once the EX-1 through EX-6 semantic schemas exist, each existing
sublayer must appear as the owner or direct subject of at least one
confirmatory template. Context-only presence does not satisfy this
requirement.

Assignments should rotate families across sublayers rather than using
EX-1 for every easy case and a complex sublayer for every stress case.
The final manifest reports counts by primary family and owning
sublayer. If a family is semantically impossible for a particular
sublayer, no forced combination is required, but the exclusion must be
recorded before measurement.

## Candidate-blind selection discipline

Scenario semantics, facets, boundary inventory, extension-path
inventory, and feasibility exclusions are fixed without using timing,
complexity, code-diff, or preliminary winner data.

Known published format limits are valid design inputs and must be used
symmetrically through the boundary and path union rules. Observing that
a candidate is likely to struggle is not grounds for deletion,
substitution, or relaxation. `UNREPRESENTABLE` is a valid confirmatory
outcome.

Structural dry runs are limited to validating canonical instances,
candidate-independent scenario schemas, and locating encoded-size
transitions. They must not be used to tune semantic values away from a
candidate disadvantage.

## Confirmatory freeze and exploratory additions

The confirmatory manifest is frozen before candidate-specific
accommodation work for the selected scenarios and before any
extensibility measurements. The freeze artefact contains at least:

- Taxonomy and canonical-schema versions.
- All templates, parameter cases, and stable identifiers.
- Compatibility, pressure, budget, and negotiation facets.
- Boundary and documented-extension-path inventories.
- Feasibility matrix and pairwise coverage audit.
- Sublayer distribution audit.
- Generator/tool versions, deterministic settings, and manifest digest.
- Source revision and dirty-tree status.

After freeze, new scenarios are labelled **exploratory** and cannot
change the primary extensibility ranking or overall framing selection.
They are still reported. Moving, replacing, or deleting a confirmatory
scenario requires a superseding methodology ADR, a new manifest
version, justification independent of observed candidate performance,
and a complete rerun for both candidates.

If a confirmatory scenario is discovered to be semantically invalid,
its invalidity and prior identifier remain in the audit trail. It is
not silently replaced by a more convenient case.

## Stopping rule

The confirmatory coverage set is complete only when all of the following
are true:

1. Both mandatory anchors exist for all eight primary families.
2. Every pressure label satisfies its template and special-case rules.
3. Every boundary-inventory item has the required shared sweep.
4. Every documented extension-path inventory item has a semantic
   exercise template.
5. Every feasible compatibility/budget/negotiation pair is covered.
6. EX-1 through EX-6 each own or are directly changed by at least one
   template once their schemas are available.
7. Every template passes ADR-0012 canonical validity requirements.
8. The machine-readable manifest and all coverage audits are frozen and
   digest-addressed.

There is no arbitrary maximum scenario count. If the stopping rule is
infeasible for Paper 1, the project must supersede this ADR with an
explicitly justified reduction rather than quietly truncating coverage.

## Consequences

**Good:**

- Every taxonomy family receives nominal and stressed coverage.
- Both candidates' documented limits and future paths contribute to one
  symmetric confirmatory portfolio.
- Pairwise coverage captures secondary-facet interactions without a
  Cartesian explosion.
- Parameterised boundary sweeps provide strong edge coverage without
  inflating family counts.
- Frozen confirmatory and separate exploratory sets prevent post-hoc
  scenario selection.
- The stopping rule is auditable and independent of which candidate
  performs better.

**Bad:**

- At least 16 templates are required before pairwise and inventory-
  driven additions.
- Boundary and path inventories require maintenance as sublayer schemas
  become concrete.
- A machine-readable feasibility model and coverage generator add
  tooling work before measurement.
- Some confirmatory templates may be unimplementable for one candidate,
  producing asymmetric engineering effort and mixed outcomes.
- Full reruns are required after a confirmatory-set methodology change.

## Pros and Cons of the Options

### Option A: One scenario per family

- Good: Only eight templates and simple reporting.
- Bad: Token coverage can select the easiest example for each family.
- Bad: Does not cover compatibility, negotiation, or boundary
  interactions.

### Option B: Exhaustive Cartesian product

- Good: Maximum nominal combination coverage.
- Bad: Produces many invalid and redundant combinations.
- Bad: Experimental and implementation cost is infeasible and obscures
  the primary semantic families.

### Option C: Hand-picked risk list

- Good: Experts can focus on plausible protocol failures.
- Good: Scenario count can be controlled directly.
- Bad: Coverage completeness is difficult to audit.
- Bad: Post-hoc rationalisation and candidate-specific selection remain
  possible.

### Option D: Anchors, sweeps, and constrained pairwise coverage

- Good: Combines guaranteed family depth, edge coverage, and secondary-
  facet interactions.
- Good: Candidate symmetry follows from union inventories and shared
  semantic values.
- Good: Deterministic coverage audits make omissions visible.
- Bad: More complex than a fixed list and requires generation tooling.
- Bad: Does not cover every family-pressure combination.

## References

- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical semantic workload and admissibility rules.
- [`./0013-extensibility-scenario-taxonomy.md`](./0013-extensibility-scenario-taxonomy.md)
  — primary families and orthogonal extensibility facets.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — framing
  comparison criteria.
- [`./0015-extensibility-per-scenario-measurements.md`](./0015-extensibility-per-scenario-measurements.md)
  — per-scenario measurement set.
