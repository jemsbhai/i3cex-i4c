# i4c

**Placeholder.** Active development of I4C (the clean-slate redesign
protocol) begins after Paper 1 (I3C-EX) submission.

See the top-level [`../README.md`](../README.md) for the project
motivation and dual-track strategy, and
[`../GOVERNANCE.md`](../GOVERNANCE.md) for the dual-track decision
rationale.

## What will live here

Once active development begins, this directory will host:

- `pyproject.toml` — Hatch-based package metadata.
- `src/i4c/` — reference implementation.
- `tests/` — unit, property, integration, and cosim tests.
- `docs/adr/` — Architecture Decision Records specific to I4C.
- `CHANGELOG.md` — package changelog.

## Anticipated scope (informative, subject to change)

I4C is anticipated to be a clean-slate **logical** protocol that:

- Shares I3C's physical layer (two-wire SDA/SCL, same electrical
  levels, same timing envelope).
- Supports dual-mode coexistence with legacy I3C on the same bus.
- Redesigns the logical protocol to make timestamping, Byzantine
  fusion, QoS, and provenance first-class primitives rather than
  layered extensions.
- Provides an efficient wire format without the envelope overhead
  that I3C-EX incurs.
- Targets FPGA validation (Digilent Cora Z7 / Terasic DE10-Nano) per
  the MDPI open-source I3C controller precedent.

**None of the above is binding.** The real design follows Paper 1.
The specification placeholder lives at
[`../specs/I4C-0.0.1-placeholder.md`](../specs/I4C-0.0.1-placeholder.md).

## Why a placeholder?

To pre-register the research direction. See the project's
pre-registration policy in [`../GOVERNANCE.md`](../GOVERNANCE.md)
under "Publication Ethics."
