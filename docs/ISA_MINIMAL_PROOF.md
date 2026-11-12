# ISA minimal proof contract — bounded research evidence

**Definition authority:** frozen ISA v1.2 FINAL. This document maps existing
claims to executable evidence; it does not introduce a new theory or a fifth
formation condition.

| Claim | Theory target | Existing challenge | Targeted strengthening |
| --- | --- | --- | --- |
| C1: same ordinary behavior may hide different formation control | Observation equivalence / Constraint / conditional non-identifiability | FQ1 SAT, E00 vs E03-S, equal Omega-0 projection | Exact 2-group to 4-check projection across all 16 input vectors and five controller expressions; a *real* LangGraph A/B pair |
| C2: Path, Attribution and Constraint are distinguishable formation facts | FormConform 3 first-order predicates | FQ4, E01-E03, relation mutations | No new conditions |
| C3: absence of evidence is not observed nonconformance | Audit / three verdicts | FQ5-FQ6, E04/E10 and mutation controls | Retain separation of hidden Oracle and Checker |
| C4: reliable structural observation or a verified construction changes identifiability | Evidence Bridge | FQ2, FQ2-WEAK, FQ3 | No universal bridge claim |
| C5: one conformant instance does not prove system-wide mediation | System-level separate from instance-level ISA | FQ7/FQ8, E07-E09 | No change |

## Precise strength of the new checks

1. The two abstract evaluation inputs are exactly the Boolean conjunctions
   `recipient AND transaction` and `dual AND channel`. For the five
   original finite controller expressions, `scripts/replay_formal.py`
   checks all 5 x 16 evaluation vectors in the Python reference engine.
   A corresponding Rust engine test checks the same 80 finite mappings.
   This closes that **finite admission-output projection**, not an arbitrary
   state-by-state refinement proof for the complete runtime.
2. `research/external/langgraph_counterexample.py` constructs and runs
   two independent LangGraph StateGraph architectures. The genuine graph
   conditionally routes admission to payment or refusal. The shadow graph
   evaluates the same checks but unconditionally routes to payment. Their
   all-pass public observations coincide. Under each single-check failure,
   only the genuine graph blocks the sandbox payment node. The complete
   16-vector finite domain is checked for both graphs.
3. LangGraph scheduler observations and the sandbox ledger are **not**
   an independently attested evidence root. This external experiment
   demonstrates ISA's real-control question in a different executable
   architecture, but does not award `Conformant` or claim full Path /
   Attribution / Constraint + Audit for a deployed Agent.

## Run

- Existing finite proof and reference suite:
  `python3 scripts/verify.py --reference-only`
- Full Rust checks:
  `python3 scripts/verify.py`
- External framework experiment (separate, pinned dependency):
  `python3 -m pip install langgraph==1.2.20`
  then `python3 research/external/langgraph_counterexample.py --out results/validation/langgraph-counterexample.json`

New findings are recorded in fresh CI run artifacts. The frozen source ZIP,
source registry, prior verification JSON, and v1.2 theory remain unchanged.

## Publication identity boundary

New research code and claim documents contain no personal authorship metadata.
The repository, Git history, frozen archive, legal notices and canonical source
links are retained for research provenance. They **must not** be copied
wholesale into a double-blind submission. A distinct reviewed anonymous
export is required at submission; this research tree is not that export.

## Execution-relation negative witnesses (post-2026-11 bounded correction)

The same frozen Path predicate includes the current decision–admission–
execution relation. Under the declared finite payment profile:

- A **denied** admission followed by an actual **paid** execution is a
  Formation Path failure when a trusted collector records that execution.
- An admitted payment executed for a different amount fails the same
  decision–action binding.
- A legitimate refusal **after** an allowed admission remains valid when
  no payment occurred.
- Altering a receipt **after** the independent collector sealed it yields
  `Unadjudicable`, not a fabricated negative Formation fact.

Research-only downstream executor witnesses are injected *before* the
synthetic collector observes the actual effect. They never set any
`formation.path` or `verdict` flag directly. Both the independent
Python checker and actual compiled Rust checker must agree with an Oracle
derived from the witnessed execution, without importing Oracle labels.

`results/reference/cases/*/system-report.json` now contains the Checker
report, exactly matching `system-report.isa`; hidden system ground truth
is stored separately under `results/reference/research-only/*/system-truth.json`.
The immutable original v0.1.0 archive remains preserved without edits.
