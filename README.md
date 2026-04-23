# I3C-EX and I4C

A dual-track research project developing the next generation of two-wire
serial communication protocols for edge AI and edge ML workloads, building
on MIPI I3C.

## Motivation

I2C (1982) and I3C (2018) are the dominant short-distance serial protocols
for embedded systems, but both have fundamental gaps for modern edge AI and
edge ML use cases:

- No wire-level provenance, confidence, or quality metadata
- No native Byzantine-resilient sensor fusion primitives
- No quality-of-service negotiation or priority scheduling
- Clock-stretching removal creates brittle real-time behaviour
- HDR mode fragmentation breaks interoperability
- Skeletal error detection, zero native security or attestation
- Loose timestamping semantics for multi-sensor fusion
- Request-response model poorly suited to continuous inference streams

This project addresses these gaps through two complementary tracks.

## Tracks

### Track 1: I3C-EX (Extension Layer)

A backward-compatible extension layer that runs on existing I3C hardware
with firmware updates only. Adds metadata envelopes, QoS negotiation,
Byzantine fusion signals, confidence propagation, and distributed
timestamping as optional layered sublayers.

- **Location**: [`i3cex/`](./i3cex/)
- **Spec**: [`specs/I3CEX-0.1.0-draft.md`](./specs/)
- **Hardware impact**: None (firmware only)
- **Adoption friction**: Low
- **Target paper**: Paper 1 (embedded systems / IoT venue)

### Track 2: I4C (Clean Redesign)

A wholesale redesigned logical protocol sharing I3C's physical layer and
electrical signalling, but with unified semantics for timestamping,
Byzantine fusion, QoS, and provenance designed in from day one. Dual-mode
hardware coexists with legacy I3C on the same bus.

- **Location**: [`i4c/`](./i4c/)
- **Spec**: [`specs/I4C-0.0.1-placeholder.md`](./specs/)
- **Hardware impact**: New controller/target silicon or FPGA
- **Adoption friction**: High
- **Target paper**: Paper 2 (networking / systems / protocols venue)

## Publication Strategy

Sequential, evidence-building:

1. **Paper 1 (Year 1)**: I3C-EX demonstrates pragmatic evolution, metadata
   envelope framing comparison (preamble vs TLV), modular sublayer adoption,
   and quantitative benchmarks on simulated I3C bus.
2. **Paper 2 (Year 2)**: I4C demonstrates principled redesign, informed by
   I3C-EX limitations discovered in Paper 1, with dual-mode hardware
   validation and Byzantine failure benchmarks.

See [`GOVERNANCE.md`](./GOVERNANCE.md) for full project governance,
versioning, and development standards.

## Repository Layout

```
.
├── README.md                       This file
├── GOVERNANCE.md                   Governance, versioning, standards
├── LICENSE                         MIT
├── CHANGELOG.md                    Top-level changelog
├── specs/                          All specification documents
│   ├── README.md
│   ├── I3CEX-0.1.0-draft.md       I3C-EX v0.1 draft spec
│   └── I4C-0.0.1-placeholder.md   I4C placeholder
├── i3cex/                          I3C-EX Python package (Track 1)
└── i4c/                            I4C project (Track 2, placeholder)
```

## Status

- **I3C-EX**: Pre-alpha, specification in draft, reference implementation
  scaffolding in progress.
- **I4C**: Placeholder. Design work begins after Paper 1 submission.

## License

MIT. See [`LICENSE`](./LICENSE).
