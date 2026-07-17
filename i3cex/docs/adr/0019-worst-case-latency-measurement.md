# ADR-0019: Worst-case latency measurement

- **Status**: Accepted
- **Date**: 2026-07-17
- **Deciders**: Muntaser Syed
- **Consulted**: Codex (OpenAI)
- **Informed**: Future collaborators, reviewers

## Context and Problem Statement

Specification section 5.3 defines axis 5 of the framing bakeoff as
"additional decode time under load." A single average timing number
would not answer that question. Parser cost changes with sublayer level,
record count, encoded length, rejection path, alignment, decoder state,
and interference phase. Host-Python timing also cannot substantiate a
Cortex-M0 latency claim.

The word *worst-case* creates an additional validity problem. The
largest value in a finite benchmark is an observed maximum, not a proof
of a program's absolute worst-case execution time (WCET). Calling a
sampled maximum WCET would overstate the evidence, while reporting only
means or medians would hide the tail behaviour relevant to constrained
real-time systems.

The bakeoff therefore needs a pre-registered method that measures
complete semantic decoders, searches known slow paths symmetrically,
separates intrinsic decoder service time from scheduling interference,
and states exactly which worst-case claims the evidence can support.

## Decision Drivers

- Construct validity: both candidates must decode the same canonical
  semantics through the complete receiver boundary in ADR-0012.
- Target validity: embedded conclusions require C measurements on the
  Cortex-M0 reference target defined by ADR-0011.
- Tail visibility: means and medians alone are insufficient for a
  worst-case-latency comparison.
- Claim discipline: finite observations must not be presented as a
  formal WCET proof.
- Search symmetry: candidate-specific slow paths must enter a shared
  stress corpus rather than receive unequal exploration budgets.
- Reproducibility: target, toolchain, timing source, load schedules,
  phases, order, repetitions, and raw samples must be retained.
- Separation of concerns: intrinsic decode cycles, loaded response
  latency, wire-transfer time, and steady-state throughput are related
  but distinct estimands.

## Considered Options

- Option A: Compare mean host-Python decode time only.
- Option B: Report the maximum from an ad-hoc target benchmark as WCET.
- Option C: Use static WCET analysis only.
- Option D: Combine target-cycle path search with deterministic load-
  phase sweeps, retain Python as a separate secondary evidence stream,
  and describe the result as a finite experimental bound.

## Decision Outcome

Chosen option: **Option D — measure complete C decoders on a pinned
Cortex-M0 target using intrinsic-cycle and loaded-response experiments,
measure Python separately, and report finite observed bounds rather than
claiming formally proven WCET**.

Axis 5 has two C-on-target confirmatory endpoints:

1. **Intrinsic complete-decode service cycles**, which isolate the
   candidate's receiver work after the input buffer is available.
2. **Loaded response cycles**, which measure time from decoder
   eligibility to completion under frozen, controlled interference
   schedules and arrival-phase sweeps.

The loaded endpoint answers the specification's "under load" criterion.
The intrinsic endpoint explains whether a loaded difference originates
in framing work or in schedule interaction. Both are required; neither
is replaced by Python timing or a bus-transfer calculation.

## Claim vocabulary

Reports and artefact metadata use these terms consistently:

- **Observed maximum**: the largest retained measurement for a stated
  candidate, workload, environment, and finite experiment.
- **Experimental latency bound**: the maximum over the complete frozen
  confirmatory input, state, load, and phase design. It is a bound on
  that experiment, not on every possible execution.
- **WCET estimate**: permitted only for an explicitly named statistical
  or static-analysis model with its assumptions and uncertainty.
- **Proven WCET**: prohibited unless a sound static timing analysis or
  exhaustive hardware argument covers the shipped binary and target.

The Paper 1 bakeoff is expected to produce observed maxima and
experimental latency bounds. It MUST NOT label them `WCET` without the
additional proof obligation above. Absence of an observed overrun is
not proof that no larger latency exists.

## Measurement boundary

### Complete decoder operation

The timed operation begins with a complete encoded extension block in a
caller-supplied input buffer and ends when the decoder has either:

- produced the complete canonical transaction defined by ADR-0012; or
- produced the specified terminal rejection classification without
  partial semantic output.

The region includes:

- framing-header and extension-body parsing;
- bounds, reserved-value, negotiated-cap, and semantic validation;
- unknown-record handling required by the scenario;
- construction or population of the canonical result in caller-
  supplied storage; and
- candidate-specific state updates that are required before the next
  frame can be decoded safely.

The region excludes:

- corpus generation, fixture lookup, logging, assertions used only by
  the harness, and result serialisation;
- physical receipt of I3C wire bits and DMA transfer into the supplied
  buffer;
- application processing after canonical output is complete; and
- one-time EX-Discovery negotiation, which is reported separately.

Both candidates use the same calling convention, destination-capacity
contract, and observable result. The C timed path performs no heap
allocation. A header-only Candidate A decode is inadmissible.

### Intrinsic service time

Intrinsic service timing starts immediately before the complete decoder
call and ends immediately after its result is observable. Unrelated
interrupts are masked. The timing peripheral remains active. Input and
output buffers are resident in SRAM, while production decoder code
executes from on-chip flash under the frozen target configuration.

This endpoint excludes queue wait and preemption. It measures complete
decoder service demand, not an end-to-end transaction deadline.

### Loaded response time

Loaded response timing begins when an already received input becomes
eligible for decoding and ends at the same complete-decoder boundary.
It includes wait and preemption caused by the frozen higher-priority
interference trace. The trace generator itself is outside the semantic
decoder, but its target execution is part of elapsed response time.

Input arrival is synthetic and timer-scheduled so that Candidate A and
Candidate B receive identical semantic transactions at identical phase
positions. Actual bus arrival and transfer are a secondary end-to-end
view described below; they are not allowed to change the primary CPU-
latency ranking.

### Legacy incremental impact

For context, each candidate is also compared with a `LEGACY-CONTROL`
path that accepts the same already-buffered application payload and
performs the common non-extension receiver work without EX decoding.
For workload `w` and condition `q`:

```text
additional_cycles(candidate, w, q)
    = latency_cycles(candidate, w, q)
    - latency_cycles(LEGACY-CONTROL, w, q)
```

Control and candidate observations are interleaved in the same block.
Negative differences caused by measurement variation remain visible;
they are not clamped to zero. The direct A-versus-B latency comparison,
not subtraction of two independently selected maxima, is the axis-5
selection evidence.

## Frozen primary target and toolchain

The primary embedded profile is:

- **Board**: STMicroelectronics `NUCLEO-F072RB`.
- **MCU**: `STM32F072RBT6`, Arm Cortex-M0 at 48 MHz.
- **Memory placement**: decoder text in on-chip flash; input, output,
  timing log, and harness state in on-chip SRAM; no external memory.
- **Cycle source**: 32-bit `TIM2`, clocked at 48 MHz with prescaler zero.
- **Compiler**: Arm GNU Toolchain `13.3.Rel1`, `arm-none-eabi-gcc`.
- **C language and flags**: `-std=c11 -mcpu=cortex-m0 -mthumb -O2
  -ffunction-sections -fdata-sections -fno-common -Wall -Wextra
  -Werror`; link with `-Wl,--gc-sections` and without LTO.
- **Firmware policy**: no operating system, no semihosting, no debug
  logging, and no vendor HAL calls inside timed regions.

The target manifest MUST additionally pin the board revision, MCU
silicon identifier, clock-tree registers, flash latency/prefetch
settings, linker script, startup code, compiler binary digest, firmware
image digest, and environmental power/temperature conditions. Any
change to a pinned item creates a new experiment series and requires
both candidates to be rerun.

Candidate decoders are linked in separate firmware images at the same
linker-defined benchmark text address. The harness and common decoder
dependencies must be byte-identical where feasible; map files and
disassemblies are retained. This prevents incidental link order from
giving one candidate a different flash placement.

TIM2 read overhead is measured with an empty no-inline control region.
Intrinsic batch size is the smallest power of two for which combined
start/stop instrumentation is at most 1% of the batch's median raw
cycles, with a maximum batch size of 4096. Raw and per-operation values
are both retained. Loaded response measurements remain single-operation
measurements because batching would erase preemption phase.

Before confirmatory collection, the timer backend is validated against:

- hand-inspected fixed-instruction calibration loops;
- timer wraparound tests using unsigned modular subtraction; and
- GPIO bracketing observed by an external logic analyser for at least
  10,000 calibration intervals.

Any unexplained disagreement greater than one 48 MHz timer tick blocks
confirmatory use of the backend.

## Workload design

### Admissibility gate

No latency result is admissible until the affected candidate and
language pass:

- ADR-0011's cross-language semantic-equivalence gate;
- ADR-0012's complete-adapter equality requirements;
- ADR-0017's complete-parser scope audit; and
- ADR-0018's critical and major legacy-safety gates.

A timeout, crash, semantic mismatch, buffer overwrite, or partial result
is a correctness failure, not an extremely large latency sample. The
affected stratum is reported `INADMISSIBLE` and cannot support a win.

### Confirmatory semantic strata

The versioned comparable core supplies successful transactions. Each
candidate receives the union of stress instances discovered for either
format. At minimum the confirmatory set contains:

1. EX-0 through EX-6 transactions at the shared minimum, nominal, and
   maximum representable section/record sizes.
2. Encoded-size boundaries at `b-1`, `b`, and `b+1` around every length,
   count, section, negotiated-cap, and buffer-capacity transition that
   is feasible for both candidates.
3. Minimum, nominal, and maximum record/section counts for each active
   level, including zero-length values where semantically valid.
4. Known and valid-unknown semantics whose required handling is
   comparable across candidates.
5. Every successful decoder control-flow edge, loop boundary, parser
   state, transition, and validation predicate inventoried by ADR-0017.
6. Input-buffer alignments modulo four and output capacity at exact-fit
   and one-capacity-unit-above-fit conditions.

Slow rejection paths are a separate confirmatory table. It contains at
least one representative from every rejection class in ADR-0018 and
the same boundary/length bins as valid inputs. Valid and rejected
maxima are never pooled because they answer different operational
questions.

### Exploratory slow-path search

Before the confirmatory set is frozen, each candidate receives the same
search budget. In both languages the budget is:

- 1,000,000 generated valid or invalid complete-decoder invocations per
  seed for 10 fixed seeds.

The C implementation additionally receives 24 hours of target-guided
search per candidate, divided equally
  across successful and rejection paths.

The search objective is lexicographic: new semantic/path coverage
first, then higher measured service cycles within the same length bin.
Mutations operate on the canonical transaction when a valid paired case
is required and on wire bytes for rejection-path exploration.

Any slow input found for one candidate is mapped back to its canonical
transaction or rejection class and added to the **shared union stress
set** for both candidates when representable. Candidate-specific cases
remain visible but cannot be used as paired evidence. Search samples
are exploratory and excluded from the final statistics; the frozen
union set is rebuilt from source and measured in a fresh confirmatory
run.

## Target state and load profiles

### Decoder state profiles

Every semantic instance is measured under:

- `RESET-COLD`: first eligible decode after reset and deterministic
  receiver initialisation;
- `STEADY-WARM`: repeated decode after 32 untimed valid warm-up
  transactions of the same stratum; and
- `RECOVERY`: first valid decode after each stateful rejection/recovery
  prefix required by ADR-0018.

The Cortex-M0 has no data cache or branch predictor, but flash prefetch,
peripheral state, buffer alignment, and receiver state can still affect
timing; the state labels therefore remain explicit.

### Interference profiles

Loaded response uses four versioned target-cycle traces:

1. `LOAD-0`: no unrelated interrupt work; single eligible input.
2. `PERIODIC-10`: a higher-priority 1 kHz interrupt whose calibrated
   body consumes 4,800 target cycles per activation (10% utilisation).
3. `PERIODIC-40`: a higher-priority 2 kHz interrupt whose calibrated
   body consumes 9,600 target cycles per activation (40% utilisation).
4. `BURST-40`: every 480,000 target cycles, four higher-priority
   activations consume a total of 192,000 calibrated body cycles in one
   contiguous burst window (40% of the 10 ms period).

The interrupt body is a retained assembly routine with no data-
dependent branches. Entry/exit and tail-chaining costs are measured and
reported in addition to the named body-cycle budget. The exact priority,
timer, trace, and calibration digest are common to both candidate
images.

`PERIODIC-10` and `PERIODIC-40` enumerate every integer target-cycle
arrival phase in one interference period. `BURST-40` measures every
interrupt transition at offsets -2 through +2 cycles and a frozen
4,096-point stratified phase grid across the full period. `LOAD-0` has
one phase. The phase order is independently permuted in each repetition
block using a retained seed.

A saturated receiver queue is reported only as a secondary diagnostic
at queue-ahead depths 1 and 8. It is excluded from the primary latency
decision because accumulated service demand overlaps axis 6 throughput.

## Repetition and execution order

### Intrinsic target cycles

For every candidate, semantic/rejection instance, alignment, state, and
compiler image:

1. Run 32 untimed warm-up operations where the state profile permits.
2. Collect 1,000 timed batches.
3. Alternate candidate/control blocks and randomise workload order with
   10 fixed seeds.
4. Power-cycle and reinitialise the board between seeds.

`RESET-COLD` reinitialises all receiver state before every operation in
a batch; reinitialisation is outside the timed region. `RECOVERY`
replays its frozen rejection/recovery prefix before every timed valid
decode. These rules preserve the named state while retaining batched
timer calibration.

If all 1,000 batch values are identical, the duplicate observations are
still retained. No timing outlier is deleted. A hardware fault may
invalidate an entire pre-defined block only when the reason and raw
block remain in the artefact.

### Loaded target response

For each frozen phase design, collect 10 complete phase sweeps, with one
board reset before each sweep. Candidate order alternates by sweep and
semantic workload order is seed-permuted. Every single-operation sample
is retained with its phase, state, interrupt count, and preemption-cycle
total.

A run ends at the pre-registered watchdog limit of 10 times the frozen
legacy-control experimental bound for the same load profile plus the
trace's maximum contiguous interference window. A watchdog event makes
the stratum `INADMISSIBLE`; it is not winsorised or converted to the
timeout value.

## Python secondary evidence

Python timing follows ADR-0011 and remains separate from the target
result. The frozen secondary profile is CPython 3.12.2, 64-bit release
build, on Ubuntu 24.04 x86-64. `PYTHONHASHSEED=0`; processor model,
microcode, kernel, power governor, turbo state, affinity, package lock,
and interpreter binary digest are recorded. The benchmark process is
pinned to one logical CPU and its SMT sibling is left idle.

`time.perf_counter_ns()` brackets the same complete semantic operation.
Intrinsic Python collection uses 1,000 blocks of the automatically
calibrated batch size after 32 warm-ups. Loaded Python collection uses
single operations under retained `IDLE`, `CPU-10`, and `CPU-40` host
interference traces. Host traces are diagnostics, not substitutes for
the deterministic target schedules.

Python is measured with two garbage-collector profiles:

- `GC-CLEAN`: a full collection before each block, default thresholds,
  and collection enabled during timing.
- `GC-PRESSURE`: deterministic cyclic garbage brings generation 0 to
  one allocation below its threshold before the timed operation.

The candidates must use equivalent allocation policies, but real
candidate allocations and any collection they trigger remain inside
the timed region. Python and C samples, maxima, ratios, and conclusions
are never pooled.

## Derived measures and uncertainty

For candidate `c`, workload stratum `s`, and load profile `p`, retain:

```text
M(c, s, p) = max(all confirmatory latency observations)

Q(c, s, p) = {minimum, median, p99, p99.9, observed maximum}

D(A, B, s, p) = M(A, s, p) - M(B, s, p)

R(A, B, s, p) = M(A, s, p) / M(B, s, p)
```

Quantiles use the nearest-rank definition on raw observations. Their
95% intervals use a cluster bootstrap over complete phase sweeps or
intrinsic repetition blocks, with 10,000 resamples and a retained
analysis seed. The observed maximum receives no bootstrap confidence
interval; it is reported with the exact finite design that produced it.

For every maximum, the report identifies the semantic transaction,
encoded length, path/state coverage, alignment, load profile, arrival
phase, preemption count, compiler image, and repetition. Maxima are also
plotted against encoded length and active sublayer level so a single
aggregate value cannot hide scaling behaviour.

Timer resolution and repeated calibration define a comparison tolerance:

```text
tolerance(s, p) = max(
    2 target cycles,
    0.01 * min(M(A, s, p), M(B, s, p)),
)
```

This is a practical-equivalence margin, not a confidence interval.
Unrounded cycle values determine classifications.

## Axis-5 classification

Classification uses the C-on-Cortex-M0 loaded-response maxima for the
successful comparable corpus. Intrinsic and rejection results remain
mandatory explanatory/safety tables.

- `A-LATENCY-SUPERIOR`: Candidate A is lower than Candidate B by more
  than the tolerance in at least one load/semantic stratum and is not
  higher by more than tolerance in any stratum.
- `B-LATENCY-SUPERIOR`: the symmetric condition holds for Candidate B.
- `PRACTICALLY-EQUIVALENT`: every stratum differs by no more than its
  tolerance.
- `MIXED`: each candidate is higher by more than tolerance in at least
  one stratum, or intrinsic and loaded evidence reverse in a way that
  prevents an unqualified conclusion.
- `INCOMPLETE`: either candidate lacks an admissible confirmatory result
  in C or any required method/provenance field is missing.

Python reversal is reported prominently and prevents a claim that one
candidate is universally lower latency, but it does not overturn the
embedded classification. No weighted score combines load profiles,
languages, latency, or other bakeoff axes.

## Secondary end-to-end view

The pinned simulator or RTL environment may measure time from the first
extension bit on the bus to complete canonical output. That view reports
separately:

```text
end_to_end = bus_transfer + buffer_delivery + loaded_decode_response
```

Transport mode, bus rate, framing expansion, payload length, DMA/PIO
policy, and simulator/RTL revision are retained. Wire expansion must
reconcile with ADR-0016. Because bus-transfer differences can dominate
decoder cycles, the end-to-end view is never substituted for the
primary CPU-latency table. Steady-state completions per unit time belong
to axis 6.

## Required artefacts

Each confirmatory series retains:

- Canonical corpus, rejection corpus, union stress set, generators,
  seeds, versions, and cryptographic digests.
- C and Python complete decoder sources and semantic-gate results.
- Board/MCU identifiers, target register dump, timer calibration,
  firmware sources, linker maps, disassemblies, binaries, and digests.
- Exact compiler/interpreter versions, flags, dependencies, host/target
  controls, and dirty-tree state.
- Load traces, phase grids, priorities, calibration data, watchdog
  bound, execution order, and reset log.
- Every raw timing observation, including invalidated blocks with their
  pre-registered invalidation reason.
- Analysis code, derived tables/figures, bootstrap seeds, and a
  machine-readable classification record.

Derived results must be reproducible from retained raw observations
without rerunning hardware. The complete experiment must also be
runnable from the published artefact.

## Consequences

**Good:**

- Embedded latency claims are tied to a real Cortex-M0 binary and a
  one-cycle target timer.
- Complete semantic decoding prevents a header-only comparison from
  favouring Candidate A.
- Shared slow-path search and union-corpus confirmation reduce
  candidate-specific search bias.
- Intrinsic and loaded endpoints expose both parser work and schedule
  interaction.
- Explicit vocabulary prevents an empirical maximum from being
  misrepresented as proven WCET.
- Separate Python evidence remains useful to package users without
  contaminating the embedded result.

**Bad:**

- Hardware, toolchain, calibration, and phase sweeps add substantial
  artefact and execution cost.
- A finite experimental bound can still miss a slower unmeasured
  hardware or input state.
- Candidate-specific binaries require careful link-layout auditing.
- Strict dominance may produce a `MIXED` result rather than a simple
  latency winner.
- Toolchain or target changes require a complete paired rerun.

## Pros and Cons of the Options

### Option A: Mean host-Python time only

- Good: Fast to implement and easy to reproduce on developer machines.
- Bad: Does not measure the Cortex-M0 target or tail latency.
- Bad: Interpreter and allocation effects can reverse candidate order.

### Option B: Ad-hoc observed maximum labelled WCET

- Good: Produces a simple number with little methodological overhead.
- Bad: A finite maximum is not an absolute execution-time proof.
- Bad: Unfrozen inputs, loads, and phases make the number easy to bias.

### Option C: Static WCET analysis only

- Good: Can support a true upper-bound claim when the binary and target
  model satisfy the analyser's assumptions.
- Bad: Requires a qualified timing model for the selected MCU, compiler,
  binary, flash system, and all decoder loops.
- Bad: Does not directly describe Python or measured schedule
  interaction and may be infeasible for Paper 1.

### Option D: Target path search plus deterministic load sweeps

- Good: Directly answers the under-load comparison on the reference
  target while retaining interpretable intrinsic cycles.
- Good: Frozen phase enumeration catches schedule interactions that
  random timing alone may miss.
- Good: Honest claim vocabulary matches the strength of empirical
  evidence.
- Bad: More expensive than average-only microbenchmarks and still not a
  formal WCET proof.

## References

- [`./0009-efficiency-principle.md`](./0009-efficiency-principle.md)
  — required constrained-target cycle analysis.
- [`./0010-bakeoff-evaluation-methodology.md`](./0010-bakeoff-evaluation-methodology.md)
  — six-axis methodology framework.
- [`./0011-python-c-runtime-evidence.md`](./0011-python-c-runtime-evidence.md)
  — separate Python/C evidence and Cortex-M0 primary endpoint.
- [`./0012-semantic-equivalence-and-preamble-body.md`](./0012-semantic-equivalence-and-preamble-body.md)
  — canonical model and complete timed receiver boundary.
- [`./0016-wire-overhead-measurement.md`](./0016-wire-overhead-measurement.md)
  — complete-extension bytes and separate physical transport view.
- [`./0017-parse-complexity-measurement.md`](./0017-parse-complexity-measurement.md)
  — parser path and structural inventory feeding the stress corpus.
- [`./0018-legacy-safety-measurement.md`](./0018-legacy-safety-measurement.md)
  — rejection classes, recovery prefixes, and safety admissibility.
- `../../../specs/I3CEX-0.1.0-draft.md` section 5.3 — worst-case
  latency comparison criterion.
- [ST NUCLEO-F072RB product page](https://www.st.com/en/evaluation-tools/nucleo-f072rb.html)
  — selected reference board.
- [STM32F072x8/xB data sheet](https://www.st.com/resource/en/datasheet/stm32f072r8.pdf)
  — Cortex-M0 frequency and 32-bit TIM2 capabilities.
- [Arm GNU Toolchain 13.3.Rel1](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads/13-3-rel1)
  — frozen bare-metal compiler release.
