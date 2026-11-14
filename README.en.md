# ISA executable research artifact

This page is a concise English overview. For the complete, current environment installation and two-part reproduction command, begin at the [canonical README](README.md#start-here--full-research-reproduction). The dedicated Chinese research and reproducibility materials are linked below.

This is a deterministic research implementation of the frozen ISA v1.2 FINAL paper: actual formation, evidence production, evidence-only checking, research-only ground truth, and finite formal counterexamples.

**Original v0.1.0 archive status (historical): `VALIDATION_INCOMPLETE`.** At the first delivery checkpoint, Rust compilation and Cargo tests had not been executed, and the recorded outputs were Python reference and Z3 formal results. That archive and its original machine status are intentionally immutable.

**Current official release status:** The identified [TrantorLabs/ISA-Artifact v1.0.0 release](https://github.com/TrantorLabs/ISA-Artifact/releases/tag/v1.0.0) completed its actual Rust/Python/Z3 and independent LangGraph CI on [the publication commit](https://github.com/TrantorLabs/ISA-Artifact/actions/runs/43225205830) (2026-11-12). The historical v0.1.0 archive retains its original incomplete status. Subsequent changes must use their own exact-head CI; the archived report is not current proof.

Run `python3 scripts/verify.py --reference-only` for the reference/formal suite (Python 3.11+, Z3 shared library or executable). Install the pinned Rust 1.85.0 toolchain and run `python3 scripts/verify.py` for full gates, including actual Rust execution and cross-language comparisons. Missing tools fail the full release gate.

The central pair uses the same ordinary outcome and policy results: one controller genuinely gates admission, another only runs shadow checks. Protected formation-bound evidence distinguishes them; missing required evidence yields Unadjudicable. The reference suite includes 22 directed scenarios, separate Oracle checks, checker mutation tests and exact reproduction. Z3 executes 17 queries in eight groups and an independent enumerator visits 2,560 finite worlds.

Collector authenticity and complete observation are explicit synthetic trust assumptions. Checksums are not authentication; a process boundary is not a hostile-host sandbox. The compromised-trust-root counterexample is deliberately retained. No production payments, deployed AI safety guarantees, empirical risk-reduction claims or universal formal proofs are supplied.

See the [canonical English README and first-screen setup](README.md), [Chinese research manuscript](docs/paper/ISA_CN_v1.2_FINAL.md), [Chinese reproducibility notes](docs/REPRODUCIBILITY.md), [traceability](docs/TRACEABILITY.md), [delta ledger](docs/decisions/ARTIFACT_DELTA.md) and [security scope](SECURITY.md). Machine status: `results/validation/verification.json`.
