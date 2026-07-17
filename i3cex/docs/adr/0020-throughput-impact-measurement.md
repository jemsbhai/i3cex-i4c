# ADR-0020: Throughput-impact measurement

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

Specification section 5.3 defines axis 6 of the framing bakeoff as
"effective payload bandwidth given envelope overhead." Wire bytes are
part of that question, but ADR-0016 already measures them exactly. A
throughput methodology that merely restates payload efficiency would
duplicate axis 1 and ignore the possibility that encoding or complete
semantic decoding, rather than the bus, is the limiting stage.

Throughput is also easy to inflate accidentally. A benchmark can count
extension bytes as useful payload, time only a framing header, drop work
when a queue fills, omit validation, report a short transient burst, or
compare different semantic streams. Host-Python operations per second
cannot substantiate embedded bandwidth claims, while a bus-only formula
cannot expose a Cortex-M0 processing bottleneck.

The bakeoff therefore needs a pre-registered method that separates wire
capacity, sender/receiver processing capacity, and sustainable combined
goodput; uses complete semantically equivalent operations; and reports
which stage limits each result.

## Decision Drivers

- Count only successfully delivered opaque application bytes as payload
  goodput.
- Present both candidates with identical ordered canonical semantics,
  application payloads, negotiation state, and reset state.
- Reuse ADR-0016's complete encoded outputs and physical-bit accounting
  rather than inventing a second wire-size model.
- Reuse ADR-0019's pinned Cortex-M0 target/toolchain and controlled load
  profiles for embedded runtime validity.
- Measure complete encoding and decoding, including all required
  validation and canonical-result construction.
- Separate exact deterministic wire results from empirical C and Python
  runtime results.
- Require sustained, drop-free operation with bounded queue state; a
  candidate may not improve throughput by discarding transactions.
- Expose payload-size, sublayer-level, direction, fragmentation, and
  bottleneck reversals instead of hiding them in a workload-weighted
  average.
- Keep Python and C evidence separate per ADR-0011.

## Considered Options

- Option A: Reuse only ADR-0016's payload-efficiency ratio.
- Option B: Report only isolated decoder operations per second.
- Option C: Report one end-to-end simulator goodput number.
- Option D: Measure wire, endpoint, and combined-pipeline capacity as
  linked but separate views, with C-on-Cortex-M0 primary and Python
  secondary.

## Decision Outcome

Chosen option: **Option D — measure exact transport-limited goodput,
complete encoder/decoder throughput on the pinned target, and sustained
combined goodput, then classify candidates from the combined C-target
view without pooling its component or Python results**.

Axis 6 has three mandatory views:

1. **Wire capacity**: effective application-payload bits per bus second
   from actual candidate encodings and physical transaction traces.
2. **Endpoint capacity**: complete encode and decode application-payload
   bits per target second under a continuously available work stream.
3. **Sustainable combined goodput**: application-payload bits delivered
   through the sender, bus, and receiver pipeline per second with no
   drop, semantic error, or unbounded backlog.

The combined view is the axis-6 classification endpoint. Wire and
endpoint views identify the bottleneck and remain mandatory even when
they do not change the final classification.

## Units and vocabulary

- A **payload byte** is one successfully delivered opaque application
  octet from the canonical workload. Extension metadata, framing,
  padding, negotiation, retry, and transport bytes are never payload.
- **Goodput** is payload bits delivered per elapsed second.
- **Transaction throughput** is complete canonical transactions
  delivered per elapsed second and is always reported alongside
  goodput.
- **Offered load** is the rate at which canonical transactions are made
  available to the pipeline.
- **Saturated** means the source always has another canonical
  transaction available; it does not permit dropping or overwriting
  queued work.
- **Sustainable** means a frozen stream completes without loss and its
  queue occupancy returns to the same state at each stream-period
  boundary after warm-up. A monotonically growing backlog is not
  sustainable.

Decimal SI units are used in headline rates: `bit/s`, `kbit/s`, and
`Mbit/s` use powers of 1000. Exact byte, bit, cycle, and nanosecond totals
are retained so alternative units can be reproduced.

## Common operation boundary

### Complete encoder

The encoder operation begins with one canonical transaction and
caller-supplied output storage. It ends when all candidate-specific
extension fragments and their lengths are available to the transport
stage or when a terminal error is returned.

The timed region includes:

- framing and complete sublayer-section/record generation;
- length, count, subtype, continuation, and fragmentation generation;
- negotiated-cap and destination-capacity checks; and
- every candidate-specific state update required before the next
  transaction.

It excludes corpus lookup, application-payload generation, logging,
fixture loading, and physical bus transmission.

### Complete decoder

The decoder boundary is identical to ADR-0019: it begins with complete
candidate extension bytes in caller-supplied storage and ends only after
the complete canonical transaction or terminal rejection is observable.
Successful throughput uses only valid transactions. Rejection
throughput is a separate denial-of-service diagnostic and cannot improve
the primary result.

### Common harness work

Both candidates use the same calling convention, preallocated buffers,
capacity checks, semantic sequence, and application-payload bytes. The C
path performs no heap allocation. A common no-inline harness consumes a
fixed canonical-result summary after every operation so the compiler
cannot remove work. Its assembly and cost are retained and measured with
`LEGACY-CONTROL`.

A header-only Candidate A operation, an encoder that omits section
bytes, or a TLV decoder that stops before canonical reconstruction is
inadmissible.

## Frozen execution profiles

### C primary profile

Axis 6 adopts ADR-0019's primary profile without modification:

- `NUCLEO-F072RB` with `STM32F072RBT6` Cortex-M0 at 48 MHz;
- decoder/encoder text in on-chip flash and working buffers in SRAM;
- 32-bit TIM2 at 48 MHz with prescaler zero;
- Arm GNU Toolchain `13.3.Rel1` and the exact C/link flags in ADR-0019;
- no operating system, semihosting, timed logging, vendor HAL calls, or
  heap allocation in benchmark operations; and
- separate candidate firmware images whose measured function begins at
  the same linker-defined address.

The board, silicon, clocks, flash settings, compiler and binary digests,
linker map, disassembly, environmental controls, and dirty-tree state
are retained under ADR-0011 and ADR-0019. A change to any frozen item
requires a complete paired rerun.

Encoder, decoder, and `LEGACY-CONTROL` are measured separately. Complete
pipeline modeling uses their retained C-target service observations; it
does not substitute host timing.

### Python secondary profile

Python uses ADR-0019's frozen CPython 3.12.2 64-bit release profile on
Ubuntu 24.04 x86-64, including CPU affinity, power/turbo controls,
`PYTHONHASHSEED=0`, interpreter/package digests, and separate `GC-CLEAN`
and `GC-PRESSURE` modes.

Python encoder, decoder, and combined in-process pipeline rates are
reported in separate tables from C. They are relevant to the maintained
reference implementation but are not a proxy for embedded goodput and
are never averaged with C.

## Confirmatory workload

### Semantic strata

The successful comparable core from ADR-0012 is the source of truth. At
minimum it includes:

1. EX-0 through EX-6 at shared minimum, nominal, and stress semantic
   profiles.
2. Every feasible `b-1`, `b`, and `b+1` boundary around section length,
   TLV value length, record/section count, negotiated cap, output
   capacity, and fragmentation transitions identified by ADR-0016 and
   ADR-0017.
3. Minimum, nominal, and maximum complete encoded extension sizes for
   every active level.
4. Stateless independently decodable transactions and every permitted
   stateful/amortised sequence from ADR-0016, reported separately.
5. Both controller-to-target and target-to-controller semantic
   directions. If the candidate encoding is direction-independent, the
   duplicated wire bytes remain visible but are not treated as
   independent statistical evidence.

Only cases both candidates represent with equal canonical meaning enter
paired numeric comparisons. `UNREPRESENTABLE` cases remain categorical
extensibility evidence and cannot be assigned zero goodput.

### Application-payload domain

For each semantic case, opaque application-payload length `P` is:

```text
P = 0 and every power of two from 1 through 4096 bytes
```

Duplicate values are removed. The 4096-byte upper bound is an experiment
profile, not a new protocol limit. The exact bytes come from a versioned
deterministic generator and are identical across candidates.

When `P = 0`, payload goodput is exactly zero and goodput ratios are
`NOT-DEFINED`; transaction throughput remains meaningful. Zero-payload
cases never determine the payload-goodput classification.

### Stream shapes

Confirmatory streams are deterministic and versioned:

- `HOMOGENEOUS`: one semantic/payload case repeated.
- `LEVEL-ROUND-ROBIN`: EX-0 through EX-6 in ascending order, using the
  same payload length.
- `SIZE-ALTERNATING`: smallest and largest feasible encoded cases
  alternate to expose boundary and buffer turnover.
- `FRAGMENT-BOUNDARY`: cases immediately below, at, and above each
  shared fragmentation transition repeat in order.
- `STATE-RESET`: the required reset/independent representation precedes
  each permitted stateful sequence.

No synthetic weighted mixture is called typical. A trace-derived
mixture may be added only with published provenance and is reported as a
separate deployment case, not folded into confirmatory totals.

### Session lengths and negotiation

Steady-state primary rates exclude one-time EX-Discovery negotiation.
The end-to-end report also amortises actual negotiation traces from
ADR-0016 over session lengths:

```text
S = 1, 10, 100, 1,000, and 1,000,000 transactions
```

Negotiation time, bytes, and endpoint cycles are shown separately. A
candidate cannot hide recurring state refresh as one-time negotiation.

## Wire-capacity view

### Transport profiles

The pinned simulator or RTL environment emits complete physical traces
for I3C SDR clock profiles:

```text
1.0 MHz, 4.0 MHz, 8.0 MHz, and 12.5 MHz
```

The 12.5 MHz profile is primary; lower rates are sensitivity profiles.
For both private-read and private-write directions, timing begins at the
first bus start condition and ends after the final stop condition needed
to carry the canonical transaction once. The trace includes every
candidate-induced address phase, parity/T bit, turnaround, repeated
start, fragment transaction, padding bit, and idle interval required by
the frozen transport mapping.

The primary profile is error-free and uses identical controller/target
turnaround rules. Retry and fault-injection profiles are secondary and
must apply the same physical error trace and retry policy to both
candidates.

For candidate `c` and stream window `w`:

```text
P[w]      = successfully delivered opaque application octets
B[c,w]    = physical bus bits from retained traces
Tbus[c,w] = elapsed bus seconds from retained traces

wire_goodput[c,w] = 8 * P[w] / Tbus[c,w]
wire_tx_rate[c,w] = transactions[w] / Tbus[c,w]
wire_efficiency[c,w] = 8 * P[w] / B[c,w]
```

`wire_efficiency` is `NOT-DEFINED` when `B[c,w] = 0`. `B[c,w]` and the
protocol-octet attribution must reconcile exactly with ADR-0016.
Analytic rates are cross-checks; retained physical traces are the source
of truth.

Wire results are deterministic design outputs. Replaying identical
traces does not create statistical replicates, and no confidence
interval or significance test is attached to them.

## Endpoint-capacity view

### Target harness

For each candidate, operation, stream, load, state, and seed:

1. Validate every stream transaction outside timing.
2. Execute 4,096 untimed operations to establish the named steady state.
3. Start a window with work continuously available.
4. Complete operations until at least `2^24` target cycles have elapsed;
   finish the operation that crosses the boundary and retain the actual
   elapsed cycles.
5. Record completed transactions, successful payload octets, extension
   octets, actual cycles, common-harness cycles, and final semantic
   digest.
6. Repeat for 30 windows, power-cycling before windows 1, 11, and 21.

Workload order is independently permuted by 10 retained seeds. Candidate
order alternates by seed. No per-operation timer read is inserted into
the sustained window. The 32-bit timer is sampled with unsigned modular
subtraction; each window remains far below one wrap at 48 MHz.

The four ADR-0019 interference traces are mandatory:

- `LOAD-0`;
- `PERIODIC-10`;
- `PERIODIC-40`; and
- `BURST-40`.

Interference work is not payload. Its exact activations and cycles are
retained so rate loss can be attributed to candidate work or scheduled
load.

For candidate `c`, endpoint `e`, and window `w`:

```text
endpoint_goodput[c,e,w]
    = 8 * completed_payload_octets[c,e,w]
      / (elapsed_cycles[c,e,w] / 48,000,000)

endpoint_tx_rate[c,e,w]
    = completed_transactions[c,e,w]
      / (elapsed_cycles[c,e,w] / 48,000,000)
```

Encoder and decoder rates are never pooled. Report application-payload,
extension-octet, and transaction rates together so large payloads do not
hide per-transaction cost and small payloads do not hide byte scaling.

### Legacy control and impact

`LEGACY-CONTROL` processes the same application-payload stream through
the common receiver/sender harness with no EX encoding or decoding. For
each endpoint stratum:

```text
impact_ratio[c,e,w]
    = endpoint_goodput[c,e,w] / legacy_goodput[e,w]

impact_percent[c,e,w] = 100 * (impact_ratio[c,e,w] - 1)
```

Ratios are `NOT-DEFINED` for zero-payload cases; transaction-rate impact
is reported instead. Direct Candidate A/B rates remain the selection
evidence. A ratio of independently selected best windows is prohibited.

### Python harness

Python uses the same ordered canonical streams and complete operation
boundaries. After 4,096 warm-up operations, an automatically calibrated
loop runs for at least one second per window using
`time.perf_counter_ns()`. Collect 30 windows for each `GC-CLEAN` and
`GC-PRESSURE` profile, alternate candidate order, and retain actual
operations, payload bytes, elapsed nanoseconds, allocations, collection
counts, and semantic digest.

Host `IDLE`, `CPU-10`, and `CPU-40` profiles are secondary diagnostics.
The Python combined view composes these endpoint observations with the
same exact transport traces; host wall-clock bus simulation speed is
excluded. Python results do not participate in the C-target classifier.

## Sustainable combined-goodput view

### Pipeline model

The combined view composes three measured stages:

```text
complete C encoder -> physical I3C transport -> complete C decoder
```

It is a versioned deterministic discrete-event replay, not a claim that
the STM32F072 contains an I3C peripheral. Sender and receiver use the
same pinned Cortex-M0 service observations but are separate endpoints,
so their work may overlap transport as it would on distinct devices.

The primary handoff uses one in-service transaction plus one queued
complete transaction (`Q=1`) with lossless backpressure. `Q=0`, `Q=8`,
and an 8 KiB byte-capacity queue are sensitivity views. Queue storage,
descriptor bytes, maximum occupancy, and backpressure duration are
reported; they are not silently assumed free.

The source remains saturated. Each combined run discards 10,000 warm-up
transactions and then delivers:

```text
max(100,000 transactions, 100 complete stream periods)
```

The run is admissible only when all transactions are delivered exactly
once, in order, with equal canonical meaning; the queue remains within
its bound; and queue occupancy has no positive period-to-period drift.
No drop, overwrite, timeout, semantic failure, or partial result is
converted into a low or high numeric rate.

Each combined stratum has 30 replays. Replay `j` uses target encoder
window `j` and a frozen seed-permutation of the 30 decoder windows; the
same pairing rule and seed apply to both candidates. The exact wire trace
does not acquire artificial replicates. Primary replays apply the same
ADR-0019 load profile independently at sender and receiver; crossed
sender/receiver load pairs are sensitivity results.

For replay `r`:

```text
combined_goodput[c,r]
    = 8 * delivered_payload_octets[c,r]
      / steady_state_elapsed_seconds[c,r]

combined_tx_rate[c,r]
    = delivered_transactions[c,r]
      / steady_state_elapsed_seconds[c,r]
```

The replay records encoder-busy, bus-busy, decoder-busy, blocked, and
idle time. Its reported bottleneck is the stage with maximum utilisation.
As an independent check, combined transaction capacity cannot exceed
the minimum encoder, wire, or decoder transaction capacity for the same
stream and profile. Any violation blocks the result.

### Empirical end-to-end confirmation

Where the pinned simulator/RTL and target harness can be coupled without
host scheduling entering the measured interval, a secondary replay of
the same stream confirms transaction ordering, transport duration, and
queue events. Host wall-clock speed is never reported as protocol
goodput. Disagreement with the deterministic pipeline model is retained
as a methodology failure until explained.

## Statistics and reporting

### Exact and empirical summaries

Wire totals are reported exactly. For endpoint and combined C-target
results, report per stratum:

- all 30 raw windows or replays;
- ratio-of-sums aggregate goodput and transaction rate;
- minimum, median, maximum, p5, and p95 window rates;
- Candidate A minus Candidate B absolute difference and A/B ratio;
- `LEGACY-CONTROL` impact;
- encoded extension octets, physical bits, and fragment count;
- encoder, bus, and decoder utilisation; and
- maximum queue occupancy and backpressure time.

The ratio-of-sums aggregate is:

```text
aggregate_goodput[c,s]
    = 8 * sum(delivered_payload_octets[c,s])
      / sum(elapsed_seconds[c,s])
```

It is not the arithmetic mean of per-window ratios. Ninety-five-percent
intervals for empirical rates use a cluster bootstrap over complete
windows with 10,000 resamples and a retained analysis seed. Wire-only
values receive no bootstrap interval.

Results are plotted against payload length, complete extension length,
active level, and offered/achieved rate. Homogeneous and heterogeneous
streams, stateless/stateful modes, directions, load profiles, and
session amortisation remain separate. No workload-weighted universal
average is computed.

### Practical-equivalence margin

For combined C-target stratum `s`, define relative difference:

```text
relative_delta[s]
    = (G[A,s] - G[B,s]) / max(G[A,s], G[B,s])

tolerance[s]
    = max(0.01, 2 / min(total_target_cycles[A,s],
                         total_target_cycles[B,s]))
```

`G` is ratio-of-sums combined goodput. The 1% term is the
pre-registered practical margin; the cycle term prevents a sub-timer-
resolution classification. Unrounded retained values determine labels.

## Axis-6 classification

Classification uses successful comparable-core combined goodput at
12.5 MHz, `Q=1`, all mandatory C-target load profiles, and every nonzero
payload stratum:

- `A-THROUGHPUT-SUPERIOR`: Candidate A exceeds Candidate B by more than
  tolerance in at least one stratum and is not lower by more than
  tolerance in any stratum.
- `B-THROUGHPUT-SUPERIOR`: the symmetric condition holds for Candidate
  B.
- `PRACTICALLY-EQUIVALENT`: every stratum differs by no more than its
  tolerance.
- `MIXED`: each candidate is lower by more than tolerance in at least
  one stratum, or wire and endpoint reversals prevent an unqualified
  system claim.
- `INCOMPLETE`: either candidate lacks admissible C results, required
  provenance, physical-trace reconciliation, or complete pipeline
  replay for any mandatory stratum.

Zero-payload transaction throughput, lower bus rates, alternate queues,
session amortisation, retry profiles, and Python results are mandatory
context but do not arithmetically override the primary classification.
A Python reversal prevents a claim of universal throughput superiority.

No weighted score combines throughput views, languages, or other
bakeoff axes. The later framing-selection ADR consumes the categorical
axis result and complete stratified tables.

## Admissibility and failure handling

A throughput stratum is admissible only when:

- both candidates pass ADR-0011 semantic equivalence and ADR-0018
  critical/major safety gates;
- actual encoded bytes and physical-bit totals reconcile with ADR-0016;
- complete encoders and decoders reconstruct identical canonical
  transactions in both languages;
- all required validation remains enabled;
- every offered transaction is delivered exactly once and in order;
- queue, stack, static, and output-buffer bounds are respected;
- no watchdog, timer, counter, arithmetic, or buffer overflow occurs;
- output digests match independently generated expected digests; and
- source, corpus, manifest, and binary digests match the frozen series.

A crash, timeout, semantic mismatch, silent drop, duplicate, reorder,
partial result, or unbounded queue is `INADMISSIBLE`, not a numeric
penalty and never zero throughput. An inadmissible candidate cannot win
the affected axis.

## Required artefacts

Each confirmatory series retains:

- Canonical transactions, opaque payloads, stream definitions,
  direction, session traces, seeds, versions, and cryptographic digests.
- Actual candidate encodings, byte attribution, physical bus traces,
  bit counts, transport configuration, and ADR-0016 reconciliation.
- Complete C/Python encoder and decoder sources plus semantic and safety
  gate records.
- Target firmware, linker maps, disassemblies, binaries, timer
  calibration, load traces, register state, compiler/interpreter and
  dependency manifests, and dirty-tree state.
- Every endpoint window and combined replay record before aggregation.
- Queue/backpressure events, utilisation traces, semantic digests,
  failure/exclusion records, and bottleneck labels.
- Analysis/replay code, bootstrap seeds, derived tables/figures, and a
  machine-readable axis classification.

Derived results must be reproducible from retained raw artefacts without
rerunning hardware. The published artefact must also provide one command
that rebuilds and executes the complete experiment.

## Consequences

**Good:**

- Axis 6 measures useful application delivery rather than total bytes
  moved or incomplete parser calls.
- Exact wire and measured endpoint rates reveal the actual bottleneck.
- Complete semantic boundaries prevent Candidate A's header codec from
  receiving an artificial throughput advantage.
- Sustained lossless replay prevents short bursts and silent drops from
  appearing as wins.
- Payload and transaction rates expose both per-byte and per-operation
  scaling.
- C and Python remain relevant without statistically meaningless
  pooling.
- The method reuses ADR-0016 and ADR-0019 artefacts instead of building
  inconsistent byte and timing models.

**Bad:**

- The matrix across semantics, payload sizes, directions, loads, bus
  rates, queues, and session lengths is expensive.
- Combined goodput is model-based until a suitable physical I3C target
  can confirm the complete pipeline.
- A strict dominance rule may produce `MIXED` rather than one winner.
- Buffer and backpressure accounting adds implementation and review
  burden.
- Full sublayer schemas and complete C/Python adapters are prerequisites
  for confirmatory measurement.

## Pros and Cons of the Options

### Option A: Payload-efficiency ratio only

- Good: Exact, simple, and already derivable from ADR-0016.
- Bad: Duplicates wire overhead and cannot reveal CPU bottlenecks.
- Bad: A byte-efficient format can still have lower system throughput.

### Option B: Isolated decoder operations per second

- Good: Directly measures implementation capacity.
- Good: Straightforward on the Cortex-M0 target.
- Bad: Omits encoding, physical transfer, fragmentation, and payload
  size.
- Bad: Operations per second can reward tiny or incomplete operations.

### Option C: One simulator goodput number

- Good: Produces a simple end-to-end headline.
- Bad: Hides the limiting stage and depends on one arbitrary workload.
- Bad: Host simulation speed is not embedded protocol throughput.

### Option D: Linked wire, endpoint, and combined views

- Good: Measures the full system while preserving causal attribution.
- Good: Reuses exact wire artefacts and target-valid runtime evidence.
- Good: Supports mixed outcomes without hiding workload reversals.
- Bad: Highest implementation, execution, and reporting cost.

## References

- [`./0009-efficiency-principle.md`](./0009-efficiency-principle.md)
  — constrained-target efficiency discipline.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0011-python-c-runtime-evidence.md`](./0011-python-c-runtime-evidence.md)
  — separate Python/C evidence and Cortex-M0 primary rule.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical semantics and complete operation boundary.
- [`./0014-extensibility-coverage-strategy.md`](./0014-extensibility-coverage-strategy.md)
  — shared boundary and extension-path coverage.
- [`./0016-wire-overhead-measurement.md`](./0016-wire-overhead-measurement.md)
  — complete encoded bytes, fragmentation, and payload-efficiency
  inputs.
- [`./0017-parse-complexity-measurement.md`](./0017-parse-complexity-measurement.md)
  — complete-parser path and boundary inventory.
- [`./0018-legacy-safety-measurement.md`](./0018-legacy-safety-measurement.md)
  — safety admissibility and state-recovery cases.
- [`./0019-worst-case-latency-measurement.md`](./0019-worst-case-latency-measurement.md)
  — pinned target/toolchain, load profiles, and runtime boundaries.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — throughput-impact
  comparison criterion.
