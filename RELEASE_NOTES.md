# ISA-Artifact v1.0.0 — Verified Research Release

This is the first official **identified, non-anonymous** software release accompanying the full ISA research preprint V1.0.

## Provenance

- Source research repository: `RcityHunter/ISA-Artifact`
- Exact validated source commit: `bca9dac4810782bd7631245253125d4c163923af`
- Original source files: 498; 495 source blobs identical after import. Only `README.md`, `VERSION`, and `CITATION.cff` received publication metadata updates.
- The original v0.1.0 ZIP is kept unchanged under `archive/` with its historical `VALIDATION_INCOMPLETE` status. The current independent GitHub Actions validation is not represented as historical execution.

## Reproduction

GitHub Actions independently builds and tests Python, real Rust workspaces and harness, Z3 formal models, reference scenarios, cross-language differential checks, and LangGraph A/B countermodels. A passing `full-research-validation` and `external-langgraph-counterexample` is required for the exact release code.

Run `python3 scripts/verify.py` after installing the pinned Rust toolchain, Z3 and Python prerequisites. Run `python3 research/external/langgraph_counterexample.py --out results/validation/langgraph-counterexample.json` with LangGraph 1.2.20 for the independent experiment.

This release demonstrates **bounded** formation-control, model-class and evidence-checking properties; it does not prove production payment safety, universally trusted Audit, or general safety of all AI agents.

## Publication boundaries

This official TrantorLabs repository is the **public companion of the complete research preprint**. Its attribution, Git history, LICENSE, NOTICE, and CITATION are intentionally visible. It is **not** the anonymous IEEE S&P reviewer artifact; that independent snapshot must retain its own fixed version, identity scan and review link. No Zenodo DOI or arXiv identifier is assigned by this GitHub release.
