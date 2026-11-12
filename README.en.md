# ISA executable research artifact

This is a deterministic research implementation of the frozen ISA v1.2 FINAL paper: actual formation, evidence production, evidence-only checking, research-only ground truth, and finite formal counterexamples.

**Original v0.1.0 archive status (historical): `VALIDATION_INCOMPLETE`.** At the first delivery checkpoint, Rust compilation and Cargo tests had not been executed, and the recorded outputs were Python reference and Z3 formal results. That archive and its original machine status are intentionally immutable.

**Current independent repository status:** GitHub Actions actually built and tested Rust and ran the reference/formal suite on [main `b812b76f`](https://github.com/RcityHunter/ISA-Artifact/actions/runs/42831891634) (2026-11-10). The separate LangGraph workflow also passed on that commit. Later corrections must pass their own exact-head CI before they are treated as validated. See the current Actions run and its evidence artifacts rather than interpreting the frozen historical JSON as today's CI state.

Run `python3 scripts/verify.py --reference-only` for the reference/formal suite (Python 3.11+, Z3 shared library or executable). Install the pinned Rust 1.85.0 toolchain and run `python3 scripts/verify.py` for full gates, including actual Rust execution and cross-language comparisons. Missing tools fail the full release gate.

The central pair uses the same ordinary outcome and policy results: one controller genuinely gates admission, another only runs shadow checks. Protected formation-bound evidence distinguishes them; missing required evidence yields Unadjudicable. The reference suite includes 22 directed scenarios, separate Oracle checks, checker mutation tests and exact reproduction. Z3 executes 17 queries in eight groups and an independent enumerator visits 2,560 finite worlds.

Collector authenticity and complete observation are explicit synthetic trust assumptions. Checksums are not authentication; a process boundary is not a hostile-host sandbox. The compromised-trust-root counterexample is deliberately retained. No production payments, deployed AI safety guarantees, empirical risk-reduction claims or universal formal proofs are supplied.

See the Chinese [README](README.md), [traceability](docs/TRACEABILITY.md), [reproducibility](docs/REPRODUCIBILITY.md), [delta ledger](docs/decisions/ARTIFACT_DELTA.md) and [security scope](SECURITY.md). Machine status: `results/validation/verification.json`.
