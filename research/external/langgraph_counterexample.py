"""One actual LangGraph workflow pair for ISA's bounded formation-control claim.

Only the Agent framework's scheduler events and a sandbox ledger are observed.
This does not import the ISA runtime, checker, research oracle, or hidden labels.
The experiment tests a finite control relation, not full 3+1 audit conformance.
"""
from __future__ import annotations

import argparse
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

CHECKS = ("recipient", "transaction", "dual", "channel")


class PaymentState(TypedDict, total=False):
    instance: str
    checks: dict[str, bool]
    decision: str
    evaluated: dict[str, bool]
    advisory: bool
    status: str
    ledger: tuple[str, ...]


def build_workflow(shadow: bool):
    """The conditional graph and the shadow graph have different real edges."""
    def propose(state: PaymentState) -> dict:
        return {"decision": "pay-designated-invoice"}

    def evaluate(state: PaymentState) -> dict:
        return {"evaluated": dict(state["checks"])}

    def admission(state: PaymentState) -> dict:
        # This computed result is recorded in BOTH graphs.
        # Only the genuine graph uses it to grant execution eligibility.
        return {"advisory": all(state["evaluated"][k] for k in CHECKS)}

    def route(state: PaymentState) -> str:
        return "execute" if state["advisory"] else "refuse"

    def execute(state: PaymentState) -> dict:
        # A real node transition mutates an in-memory sandbox resource.
        return {"status": "paid", "ledger": ("paid:" + state["instance"],)}

    def refuse(state: PaymentState) -> dict:
        return {"status": "refused", "ledger": ()}

    graph = StateGraph(PaymentState)
    for name, fn in (
        ("propose", propose), ("evaluate", evaluate),
        ("admission", admission), ("execute", execute), ("refuse", refuse)
    ):
        graph.add_node(name, fn)
    graph.add_edge(START, "propose")
    graph.add_edge("propose", "evaluate")
    graph.add_edge("evaluate", "admission")
    if shadow:
        graph.add_edge("admission", "execute")
    else:
        graph.add_conditional_edges(
            "admission", route, {"execute": "execute", "refuse": "refuse"}
        )
    graph.add_edge("execute", END)
    graph.add_edge("refuse", END)
    return graph.compile()


def execute_once(workflow, flags: tuple[bool, ...]) -> dict:
    state: PaymentState = {"instance": "u-1", "checks": dict(zip(CHECKS, flags))}
    visited: list[str] = []
    # Stream node updates from the actual LangGraph scheduler. Do not trust a
    # mode flag, an expected verdict, or a self-reported trace in the state.
    for event in workflow.stream(state, stream_mode="updates"):
        assert len(event) == 1, event
        node, changes = next(iter(event.items()))
        assert isinstance(changes, dict), (node, changes)
        visited.append(node)
        state.update(changes)
    assert visited[:3] == ["propose", "evaluate", "admission"], visited
    assert visited[-1] in ("execute", "refuse"), visited
    assert len(visited) == 4, visited
    paid = visited[-1] == "execute"
    assert (state["status"] == "paid") == paid
    assert bool(state["ledger"]) == paid
    assert state["evaluated"] == state["checks"]
    assert state["decision"] == "pay-designated-invoice"
    # Ordinary observation deliberately excludes the graph's control edges.
    public = {
        "checks": state["evaluated"],
        "outcome": state["status"],
        "amount": 200000 if paid else 0,
        "explanation": "Payment evaluated under declared enterprise rules.",
    }
    return {
        "paid": paid,
        "trace": visited,
        "public": public,
        "advisory": state["advisory"],
        "ledger": list(state["ledger"]),
    }


def verify() -> dict:
    genuine = build_workflow(shadow=False)
    shadow = build_workflow(shadow=True)
    outcomes: dict[tuple[bool, ...], dict[str, dict]] = {}
    for bits in product((False, True), repeat=len(CHECKS)):
        a = execute_once(genuine, bits)
        b = execute_once(shadow, bits)
        outcomes[bits] = {"genuine": a, "shadow": b}
        # Exhaustive evidence for this finite four-check domain.
        assert a["paid"] == all(bits), ("genuine", bits, a)
        assert b["paid"], ("shadow", bits, b)
    all_pass = (True,) * len(CHECKS)
    assert outcomes[all_pass]["genuine"]["public"] == outcomes[all_pass]["shadow"]["public"]
    for i in range(len(CHECKS)):
        flipped = tuple(j != i for j in range(len(CHECKS)))
        assert not outcomes[flipped]["genuine"]["paid"]
        assert outcomes[flipped]["shadow"]["paid"]
        assert not outcomes[flipped]["shadow"]["advisory"]
    result = {
        "status": "PASS",
        "framework": "LangGraph StateGraph",
        "framework_version": version("langgraph"),
        "control_domain": "four Boolean payment checks, one bounded instance",
        "runs": 2 * len(outcomes),
        "vectors_per_graph": len(outcomes),
        "normal_observation_equivalent": True,
        "genuine_execution_count": sum(p["genuine"]["paid"] for p in outcomes.values()),
        "shadow_execution_count": sum(p["shadow"]["paid"] for p in outcomes.values()),
        "one_check_failure_interventions": len(CHECKS),
        "all_pass_paths": {
            "genuine": outcomes[all_pass]["genuine"]["trace"],
            "shadow": outcomes[all_pass]["shadow"]["trace"],
        },
        "assertion": "same all-pass behavior, different actual action-admission control",
        "trust_limit": "in-process LangGraph scheduler observations and sandbox ledger; no independently authenticated 3+1 Audit claim",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = verify()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
