> **Publication release v1.0.0** — Official research implementation maintained at [TrantorLabs/ISA-Artifact](https://github.com/TrantorLabs/ISA-Artifact). This version is derived from the validated original research commit `RcityHunter/ISA-Artifact@bca9dac4810782bd7631245253125d4c163923af`; original historical source and evidence ZIP remain preserved. Publication verification in this repository is authoritative for this release, not the historic ZIP's first incomplete report. This is the **identified, non-anonymous preprint companion**; it is not the separate IEEE S&P blinded artifact.

# ISA — Executable Research Artifact

Independent, reproducible research artifact for **Internal Structured Alignment (ISA)**. ISA asks whether a designated safety constraint genuinely controlled a bounded high-consequence judgment–action formation, and whether independent evidence is sufficient to establish that fact.

**Theory authority:** ISA Chinese paper **v1.2 FINAL** (frozen). This repository implements and evaluates its claims; code does not redefine the paper. The frozen paper source is [included locally](docs/paper/ISA_CN_v1.2_FINAL.md), with the six artifact contracts under [docs/anchors](docs/anchors/).

## Frozen source provenance

The exact original `isa-artifact-v0.1.0` source/evidence ZIP is retained in `archive/` without modification.

| Property | Fixed value |
| --- | --- |
| Artifact version | v0.1.0 |
| Original ZIP bytes | 478,510 |
| ZIP SHA-256 | `87bdb03400d2d5829fa21601c7b9ed976c66443dafd5cf44743ce5957293864e` |
| Git Blob SHA-1 | `53b30334def40e2ddb163373331db1e4d27b2ccb` |
| Archived entries | 472 |
| Frozen Chinese theory | ISA v1.2 FINAL |
| Initial verification status | `VALIDATION_INCOMPLETE`, `release_ready=false` |

The archived original report records **60 Python tests**, **22/22** independent reference scenarios, **17 Z3 queries**, **2,560** finite enumerated worlds and **6/6** mutation detections. Rust builds/tests, the real Rust harness, Rust/Python parity, formatting/lint and remote CI were **not executed** at that historical checkpoint. New checks must be described as *new evidence* with their own run identifiers, never retroactively attached to the original report.

## Research structure

- `runtime/` — isolated formation world, evidence, and independent checker.
- `research/` — test scenarios, independent oracle and research harness.
- `formal/` — bounded formal models, sibling to runtime.
- `docs/` — frozen paper snapshot, anchors, change rationale, research provenance.
- `results/` — original experimental outputs and verification logs.
- `scripts/verify.py` — reference-only and full verification entry point.
- `archive/` — byte-preserved original source and evidence package.

This is a research validation artifact, **not** a production payment system or a proof of universal safety. Formation facts, designated evidence, independent checker verdicts and hidden research truth must remain separate.

## Reproduction

```bash
sha256sum -c archive/ISA_ARTIFACT_v0.1.0_SOURCE_AND_EVIDENCE.zip.sha256
python3 scripts/verify.py --reference-only
# With pinned Rust, Python and Z3 dependencies:
python3 scripts/verify.py
```

For exact source-specific requirements see the original `docs/` and `scripts/` after import. Publishing and release status will be updated only from reproducible CI execution evidence.

## Publication relationship

SoulAuth establishes a continuous authenticated actor identity; subject-rooted governance studies long-lived authority, real effects and responsibility; ISA independently asks whether a specific action formation was really governed and knowably so. The repositories may be cited together but do not share a single proof claim.

## Narrow follow-up research (2026-11)

See [the minimal claim/evidence contract](docs/ISA_MINIMAL_PROOF.md).
The original FQ1 finite counterexample is reinforced by exhaustive
two-group/four-check admission projection tests in Python and Rust.
A separate [LangGraph StateGraph experiment](research/external/langgraph_counterexample.py)
executes one genuine gate and one shadow route through actual framework nodes;
the all-pass public observation is identical, while intervention outcomes differ.
It is a bounded **application of the Constraint concept**, not evidence
of full deployed Agent conformance or independently attested Audit.
The original source archive and historical verification records remain frozen.
New experiments must pass their own current CI runs.

The repository and its history contain attribution and provenance; they are
not a blinded review distribution. Produce a separate anonymous submission
copy after the final paper and artifact versions are fixed.
