# I3C-EX Hardware and Production Release Plan

- **Plan version**: 1.0
- **Updated**: 2026-07-17
- **Current verdict**: **NO-GO for hardware or production use**
- **Machine-readable status**: [`../../release/readiness-v0.1.0.json`](../../release/readiness-v0.1.0.json)

## 1. Purpose and claim boundary

This plan defines the evidence required to move I3C-EX from the published
`0.1.0.dev0` Python research scaffold to a hardware-validated release and,
later, a production-supported release. It is deliberately stricter than
"the tests pass": a package build does not demonstrate I3C interoperability,
embedded safety, bounded resource use, or electrical correctness.

The present repository implements and tests the Python codecs for the two
framing candidates. It does **not** yet implement a complete I3C-EX stack,
the EX-1 through EX-6 sublayers, C firmware, a behavioral integration
simulator, an active RTL cosimulation, or a physical-hardware harness.
Accordingly:

- `0.1.0.dev1` may be released as a **host-only development preview** after
  gates G00 through G02 pass. It MUST state that it carries no hardware or
  production claim.
- `0.1.0rc1` is the first **hardware release candidate**. It MUST NOT be cut
  until gates G00 through G12 pass and all RC hardware is validated.
- `0.1.0` may be described as a **hardware-validated research release** on
  the named reference boards. Pre-1.0 APIs remain unstable under the project
  governance rules.
- `1.0.0` is the first version that may be described as **production-ready**.
  It requires all gates, the RC soak, a frozen specification, and an explicit
  supported-hardware statement. Reference-board evidence does not certify a
  derived commercial product for EMC, ESD, safety, or regulatory compliance.

No milestone may be promoted by changing the manifest status alone. A gate
can become `passed` only when its retained evidence is linked from the
manifest and independently reproducible.

## 2. Compatible reference hardware

### 2.1 Required matrix

| Lane | Hardware | Qty | Purpose | Release requirement |
|---|---|---:|---|---|
| Programmable I3C link | `NUCLEO-H563ZI` | 2 | One controller and one target, both running project firmware | RC and production |
| Commercial target | `NUCLEO-H503RB` plus `X-NUCLEO-IKS01A3` | 1 set | Dynamic-address assignment and private transfers with vendor I3C sensors | RC and production |
| Constrained CPU benchmark | `NUCLEO-F072RB` | 1 | ADR-0019/ADR-0020 Cortex-M0 latency and throughput evidence | RC and production |
| Bus instrumentation | Calibrated scope or logic analyzer suitable for 12.5 MHz I3C | 1 | Electrical timing, protocol decoding, and retained traces | RC and production |
| Recovery fixture | Scriptable USB power switch or relay | 1 | Cold boots, brownouts, interrupted transactions, and recovery | Production |

The STM32H562/H563 I3C peripheral supports both controller and target roles
against I3C v1.1, and ST publishes a two-`NUCLEO-H563ZI` controller/target
private-command procedure. See the
[STM32H562/H563 data sheet](https://www.st.com/resource/en/datasheet/stm32h562ri.pdf)
and ST's
[paired controller/target walkthrough](https://community.st.com/t5/stm32-mcus/how-to-set-up-and-run-the-i3c-private-command-it-controller-and/ta-p/49397).
ST also documents the `NUCLEO-H503RB` plus `X-NUCLEO-IKS01A3` sensor setup in
its [I3C getting-started guide](https://wiki.st.com/stm32mcu/wiki/Getting_started_with_I3C).

The `NUCLEO-F072RB` is **not an I3C endpoint**. It remains required because
ADR-0019 and ADR-0020 pre-register its 48 MHz Cortex-M0 as the constrained
runtime profile. Its results measure codec cost, not physical I3C
interoperability. The board is an active ST product with integrated ST-LINK;
see the [official product page](https://www.st.com/en/evaluation-tools/nucleo-f072rb.html).

### 2.2 Substitution policy

A board may be substituted only when all of the following are recorded:

1. The MCU implements the required I3C role and required SDR/CCC behavior.
2. Voltage, pull-up, pin, clock, DMA/interrupt, and errata differences are
   documented.
3. The complete affected gate set is rerun; old evidence is not relabeled.
4. The manifest names the new board, MCU revision, firmware digest, and
   toolchain digest.

The Cortex-M0 benchmark target is frozen by ADR-0019. Substituting it creates
a new experiment series and does not replace the pre-registered evidence.

## 3. Frozen software and tool profiles

Every evidence bundle records exact versions and SHA-256 digests. The initial
profiles are:

- Host reference: CPython 3.11, 3.12, and 3.13 with the locked release-test
  environment. CPython 3.12.2 remains the secondary performance profile from
  ADR-0019/ADR-0020.
- Cortex-M firmware: Arm GNU Toolchain `13.3.Rel1`, using the flags and linker
  policy in ADR-0019. Arm retains that release in its
  [official GNU toolchain archive](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads).
- STM32 firmware: one frozen STM32CubeH5 release and one frozen
  STM32CubeProgrammer/ST-LINK release, selected before evidence collection.
  Vendor HAL code is prohibited inside timed regions.
- RTL: CHIPS Alliance `i3c-core` tag
  [`i3c-v1.5.0`](https://github.com/chipsalliance/i3c-core/releases/tag/i3c-v1.5.0),
  commit `db4a6f341145e05a5b7002a21d1cd5cc31147f35`, unless an ADR approves a
  later pin before the first confirmatory run.
- RTL host: Debian 12 or Ubuntu 22.04, Python 3.11, Verilator 5.024,
  Icarus Verilog 12.0 or later, and Verible
  `v0.0-3624-gd256d779`. These match the upstream core's documented tested
  environment more closely than the currently available Ubuntu 24.04 WSL
  installation.

Dependencies used for a release are frozen with hashes. Open lower bounds in
`pyproject.toml` remain useful for development but are not a release lock.

## 4. Release gates

### G00 — Plan and manifest

**Exit criteria**

- This plan exists and is linked from the package README.
- `release/readiness-v0.1.0.json` validates in CI.
- Every required gate has an owner-neutral evidence definition.
- `hatch run release-status` reports the current verdict without treating
  missing evidence as success.

### G01 — Host reference quality

**Exit criteria**

- Ruff lint and format checks pass.
- Strict mypy passes.
- Unit and property suites pass on Python 3.11, 3.12, and 3.13 on Linux,
  Windows, and macOS.
- Core framing modules retain 100% line and branch coverage; overall coverage
  remains at least 90% until the stubs are implemented, then ratchets to the
  governance targets.
- Warnings are errors and CI has zero annotations.

### G02 — Development artifact reproducibility

**Exit criteria**

- Sdist and wheel build from a clean tree.
- `twine check --strict` passes.
- Wheel and sdist each install into a fresh environment without using the
  source tree.
- Installed import, version, encode/decode smoke tests, and `py.typed`
  presence pass.
- Two builds from the same commit and `SOURCE_DATE_EPOCH` produce identical
  SHA-256 hashes.
- The artifact file list contains no credentials, caches, coverage data, or
  undeclared generated files.

Passing G00-G02 permits `0.1.0.dev1`; it does not permit an RC.

### G03 — Specification freeze and framing selection

**Exit criteria**

- The six-axis bakeoff is executed exactly as ADR-0010 through ADR-0020
  require, and one framing strategy is selected in a new ADR.
- The losing candidate remains documented as a negative result.
- The production wire grammar, negotiation behavior, CCC allocation, EX-1
  through EX-6 layouts, bounds, error behavior, and overhead analyses contain
  no normative `[TBD]` markers.
- `I3CEX-0.1.0-rc1.md` is created, internally reviewed, and then immutable.
- Every normative statement has a conformance-test mapping.

### G04 — Independent normative vectors

Vectors are authored from the specification, not generated by an encoder.

**Required coverage**

- Capability levels 0 through 6 and all reserved preamble patterns.
- TLV value lengths 0, 1, 126, and 127; empty and 4096-byte blocks; block
  maximum plus one; reserved types and lengths; every truncation boundary.
- Selected framing format plus legacy/no-extension detection.
- Every EX sublayer's minimum, typical, maximum, invalid, and unknown-field
  behavior after its format is frozen.
- Canonical JSON form with vector ID, spec section, inputs, exact wire bytes,
  expected semantic output or rejection class, and independent review record.

Python and C MUST consume the same immutable vector set with zero mismatch.

### G05 — Behavioral integration

**Required scenarios**

- Controller discovery, negotiation, transfer, reset, and renegotiation.
- EX-aware controller/target at every common capability level.
- EX-aware controller with legacy I3C and legacy I2C targets on a mixed bus.
- Unknown optional records, malformed records, incomplete transfers, bus
  reset, hot join, target reset, and in-band interrupt interactions.
- Fragmentation and reassembly at all registered boundaries.
- Deterministic replay from recorded seeds and traces.

No integration test may be an empty marker or a unit test under another name.

### G06 — C implementation and differential conformance

**Implementation constraints**

- C11, caller-owned buffers, explicit lengths, no heap allocation, no hidden
  global mutable state, and bounded loops for production decode paths.
- Complete candidate adapters with identical semantics during the bakeoff.
- Host builds with GCC and Clang using `-Wall -Wextra -Wpedantic -Werror`.
- AddressSanitizer and UndefinedBehaviorSanitizer runs are clean.
- Arm GNU 13.3.Rel1 Cortex-M0 and Cortex-M33 builds are warning-free.
- Public return codes distinguish success, incomplete data, unsupported
  version/feature, malformed input, and insufficient output capacity.

**Differential exit criteria**

- All normative vectors match in Python and C.
- At least 1,000,000 deterministic generated valid/invalid operations produce
  identical semantic results and rejection classes.
- Corpus digests, seeds, binaries, compiler flags, maps, and disassemblies are
  retained.

### G07 — RTL cosimulation

The disabled placeholder job is replaced by a pinned, runnable cocotb suite.

**Exit criteria**

- The upstream core and submodules are pinned by commit and license recorded.
- Controller and target paths exercise DAA, relevant CCCs, private SDR reads
  and writes, IBI, reset/recovery, and mixed-bus behavior needed by I3C-EX.
- Every normative selected-framing vector crosses the RTL transaction
  boundary in both directions where applicable.
- Backpressure, NACK, parity/CRC errors exposed by the selected mode,
  truncation, and reset-at-boundary tests pass.
- CI executes cosim on the pinned Linux image; it is no longer `if: false`.
- Waveforms and logs are retained for failed and confirmatory runs.

### G08 — Physical I3C interoperability

**Programmable pair procedure**

1. Record both board revisions, MCU device/revision IDs, ST-LINK serials,
   firmware SHA-256 values, clock registers, and pin wiring.
2. Run controller and target roles in both board assignments.
3. Complete DAA and negotiated I3C-EX discovery after cold boot, warm reset,
   target reset, controller reset, and interrupted transfer.
4. Run every normative vector in both transfer directions at 1.0, 4.0, 8.0,
   and 12.5 MHz where supported by the frozen firmware profile.
5. Run at least 100,000 ordered transfers per frequency/profile with zero
   unexplained mismatch, drop, lockup, or unbounded queue growth.
6. Retain raw serial logs, bus captures, firmware manifests, and analysis.

**Commercial-sensor lane**

- Complete DAA and repeated private reads from each enabled I3C sensor.
- Verify coexistence with an I2C target where the board configuration permits.
- Demonstrate that legacy traffic is unchanged when I3C-EX is disabled.

All unexplained analyzer violations, recovery failures, or silicon errata
interactions block the RC.

### G09 — Cortex-M0 performance evidence

- Execute ADR-0019 latency and ADR-0020 throughput methods without changing
  the target, flags, workload selection, sample counts, or exclusion rules.
- Retain target manifests, timer calibration, maps, disassemblies, binaries,
  register dumps, raw samples, bootstrap seeds, and classifications.
- Reconcile wire-goodput results with ADR-0016 physical traces.
- Do not pool Python, Cortex-M0, Cortex-M33, or bus-only measurements.
- A `MIXED`, `INCOMPLETE`, or `INADMISSIBLE` result blocks framing selection
  until the governing ADR's resolution rule is satisfied.

### G10 — Robustness and recovery

**Exit criteria**

- Each C decode entry point completes at least 24 cumulative hours of
  coverage-guided fuzzing under ASan/UBSan with no crash, leak, undefined
  behavior, timeout, or unbounded allocation.
- The target consumes at least 1,000,000 malformed/recovery frames with a
  watchdog enabled and no memory corruption, unrecovered lockup, or stack
  overflow.
- Maximum stack use, static RAM, flash, and bounded work per input are
  measured for both targets.
- Power interruption, reset during every parser phase, repeated NACK, and
  invalid negotiation transitions recover to a documented safe state.
- Dependency and secret scans pass; all release dependencies receive a
  vulnerability review with accepted-risk records where needed.

### G11 — Release supply chain

**Exit criteria**

- Clean source commit, annotated signed tag, immutable changelog entry, and
  GitHub release notes agree on version and artifact hashes.
- CycloneDX or SPDX SBOMs exist for Python, firmware, and RTL dependencies.
- SLSA-style build provenance or an equivalent signed build manifest records
  source commit, builders, inputs, tool digests, and outputs.
- Wheel, sdist, firmware ELF/BIN/HEX, maps, disassemblies, vector corpus, raw
  evidence, and documentation are retained.
- TestPyPI installation succeeds before the production PyPI upload.
- PyPI publishing is performed by the approved **local Twine process**, not a
  GitHub publishing workflow.
- A previous compatible artifact and documented rollback procedure remain
  available.

### G12 — User and operations documentation

Required documents include:

- Supported boards, MCU revisions, toolchains, Python versions, and exact
  scope of the hardware claim.
- Wiring, build, flash, self-test, upgrade, downgrade, and recovery guides.
- API reference, vector format, compatibility table, known limitations,
  security-reporting route, support policy, and end-of-life policy.
- Explicit statement that reference-board testing does not confer end-product
  regulatory approval.

### G13 — Review and soak

- All RC gates remain green for at least seven consecutive days.
- Scheduled clean builds run from a fresh environment.
- At least one reviewer reproduces host and artifact gates from the published
  RC; a second person or independent setup reproduces the physical I3C smoke
  suite.
- There are no unresolved severity-1/2 defects, security-critical findings,
  unexplained hardware errors, or release-manifest contradictions.

## 5. Execution order

| Phase | Work | Exit |
|---|---|---|
| P0 — readiness infrastructure | Plan, manifest, checker, CI validation, host evidence | `0.1.0.dev1` gate can be evaluated |
| P1 — protocol closure | Complete bakeoff, select framing, finish normative specification | G03 passes |
| P2 — conformance implementation | Vectors, simulator, C library, differential and fuzz harnesses | G04-G06 and host portion of G10 pass |
| P3 — RTL | Pin/build i3c-core, activate cocotb CI, retain waves | G07 passes |
| P4 — hardware | Procure fixtures, port firmware, run H563/H503/F072 campaigns | G08-G10 pass |
| P5 — RC | Complete docs, SBOM/provenance, publish `0.1.0rc1`, seven-day soak | G11-G13 pass |
| P6 — releases | Publish hardware-validated `0.1.0`; continue EX-1..EX-6 and support work to `1.0.0` | Explicit GO decision |

Phases are sequential at their exit gates, but implementation, procurement,
and lab-fixture preparation may overlap. Confirmatory benchmark data MUST NOT
be collected before the relevant corpus and method are frozen.

## 6. Evidence layout and retention

Release evidence belongs under a versioned external artifact bundle; small
manifests and summaries may live in this repository:

```text
evidence/<version>/
├── manifest.json
├── host/
├── packages/
├── vectors/
├── c-builds/
├── cosim/
├── hardware/
│   ├── h563-controller-target/
│   ├── h503-sensors/
│   └── f072-benchmarks/
├── fuzz/
├── sbom/
└── review/
```

Every directory contains a SHA-256 manifest. Raw evidence is immutable;
derived reports identify their input digests and generation command. Secrets,
PyPI tokens, device credentials, and personally identifying host data MUST NOT
be included.

## 7. Promotion and rollback

Promotion requires a clean manifest, all milestone gates passed, required
hardware marked `validated`, and the release decision changed to `GO` in the
same reviewed commit as the evidence links.

Rollback is mandatory when any of the following occurs after promotion:

- A wire incompatibility or normative-vector defect is discovered.
- A memory-safety, authentication/provenance, or unbounded-work defect affects
  the released scope.
- A supported board cannot recover from reset or malformed traffic as
  documented.
- Artifact hashes, signatures, provenance, or PyPI contents disagree.

Rollback actions are: stop promotion, mark the release affected, restore the
last compatible package/firmware, publish a security or compatibility notice,
and create a patch or new pre-release. Published files and tags are not
silently replaced.

## 8. Current execution state

As of 2026-07-17:

- G00 is implemented.
- G01 and G02 passed for the `0.1.0.dev1` milestone in
  [hosted run 29614745610](https://github.com/jemsbhai/i3cex-i4c/actions/runs/29614745610).
  The development preview is ready; this does not change the hardware or
  production verdict.
- G03-G10 are blocked by implementation, tool, or hardware prerequisites.
- The host has Ubuntu 24.04 WSL but lacks the pinned RTL tools.
- No ST-LINK/I3C board is connected, and the Arm GNU 13.3.Rel1/ST flashing
  tools are not installed.
- The repository MUST remain `NO-GO` for hardware and production claims until
  the manifest evidence changes under review.

Run:

```bash
cd i3cex
hatch run release-status
hatch run release-status --require dev
hatch run release-status --require rc
hatch run release-status --require production
```

The latter commands intentionally fail while their milestone is blocked.
