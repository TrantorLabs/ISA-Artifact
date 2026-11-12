"""Independent Python reference execution, NOT the Rust runtime.
A small Boolean DAG is really executed; no conformance flags are input.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from typing import Callable
from wire import KINDS, QUERIES, REQUIRES, CHANNELS, digest

@dataclass
class Spec:
    amount: int = 200_000
    threshold: int = 100_000
    values: dict[str, bool] = field(default_factory=lambda: dict.fromkeys(KINDS, True))
    code: list[str] = field(default_factory=lambda: ['E:'+k for k in KINDS] + ['A:0,1,2,3'])
    root: int = 4
    actual_source: str = 'supplier-record'
    bound_source: str = 'supplier-record'
    authority_scopes: tuple[str, str] = ('payment', 'payment')
    authority_subjects: tuple[str, str] = ('H1', 'H2')
    bound_controller: str = 'controller-1'
    execution_instance: str = 'u-1'
    execution_decision: str = 'd-1'
    execution_admission: str = 'a-1'
    route: str = 'standard'
    include_applicable: tuple[str, ...] | None = None

@dataclass
class World:
    context: dict[str, str]
    spec: Spec
    applicable: tuple[str, ...]
    actual_evaluations: dict[str, bool]
    admission: bool
    executed: bool
    reads: set[str]
    ledger: dict[str, str]
    events: list[tuple[str, dict[str, str]]]

def context(spec: Spec) -> dict[str, str]:
    result = {
        'schema': 'isa-context-1', 'system': 'payment-reference', 'version': '1',
        'instance': 'u-1', 'decision': 'd-1', 'admission': 'a-1',
        'amount': str(spec.amount), 'dual_threshold': str(spec.threshold),
        'required_scope': 'payment', 'declared_tick': '0', 'start_tick': '10',
        'gamma': ','.join(KINDS), 'queries': ','.join(QUERIES),
        'channels': ','.join(CHANNELS), 'collector': 'collector-1',
        'monitor': 'monitor-1', 'controller': 'controller-1',
        'boundary': 'finite-enterprise-payment', 'threat_model': 'synthetic-collector-root',
    }
    for q, channels in REQUIRES.items():
        result['requires.'+q] = ','.join(channels)
    for ch in CHANNELS:
        result['writers.'+ch] = 'collector-1'
    return result

def evaluate(code: list[str], root: int, values: dict[str, bool]) -> tuple[bool, set[str]]:
    if not 0 <= root < len(code) <= 32:
        raise ValueError('invalid program size/root')
    stack: dict[int, bool] = {}
    reads: set[str] = set()
    def visit(i: int) -> bool:
        if i in stack:
            return stack[i]
        op = code[i]
        if op in ('T', 'F'):
            answer = op == 'T'
        elif op.startswith('E:'):
            key = op[2:]
            if key not in values:
                raise ValueError('missing evaluator input')
            reads.add(key); answer = values[key]
        elif op.startswith(('A:', 'O:')):
            refs = [int(x) for x in op[2:].split(',') if x]
            if not refs or any(j < 0 or j >= i for j in refs):
                raise ValueError('program must be a nonempty acyclic DAG')
            # Evaluate all inputs, including non-short-circuit reads.
            args = [visit(j) for j in refs]
            answer = all(args) if op.startswith('A:') else any(args)
        else:
            raise ValueError('unsupported instruction')
        stack[i] = answer
        return answer
    return visit(root), reads

def run(spec: Spec, ctx: dict[str, str], sink: Callable[[str, dict[str, str]], None]) -> World:
    app = tuple(k for k in KINDS if k != 'dual' or spec.amount > spec.threshold)
    selected = app if spec.include_applicable is None else spec.include_applicable
    events: list[tuple[str, dict[str, str]]] = []
    def emit(name: str, fields: dict[str, str]) -> None:
        data = {name+'.'+k: v for k, v in fields.items()}
        events.append((name, data.copy())); sink(name, data)
    emit('decision', {'instance': ctx['instance'], 'id': ctx['decision'], 'amount': str(spec.amount), 'candidate': 'candidate-1'})
    emit('source', {'instance': ctx['instance'], 'actual': spec.actual_source, 'bound': spec.bound_source})
    emit('authority', {'instance': ctx['instance'], 'h1': spec.authority_subjects[0], 'h2': spec.authority_subjects[1],
                       'scope1': spec.authority_scopes[0], 'scope2': spec.authority_scopes[1]})
    emit('effect', {'instance': ctx['instance'], 'actual_controller': ctx['controller'], 'bound_controller': spec.bound_controller})
    ev = {'instance': ctx['instance'], 'applicable': ','.join(selected)}
    for kind in KINDS:
        ev[kind] = str(int(spec.values[kind]))
    emit('evaluation', ev)
    pg = {'root': str(spec.root), 'count': str(len(spec.code))}
    pg.update({str(i): op for i, op in enumerate(spec.code)})
    emit('program', pg)
    allow, reads = evaluate(spec.code, spec.root, spec.values)
    emit('admission', {'instance': ctx['instance'], 'id': ctx['admission'], 'decision': ctx['decision'],
        'state': 'allow' if allow else 'deny', 'reads': ','.join(sorted(reads)), 'controller': ctx['controller']})
    executed = allow or spec.route == 'direct'
    ledger = {'instance': spec.execution_instance, 'decision': spec.execution_decision,
              'admission': spec.execution_admission if spec.route != 'direct' else 'direct',
              'status': 'paid' if executed else 'refused', 'amount': str(spec.amount if executed else 0),
              'channel': 'standard', 'route': spec.route}
    emit('execution', ledger)
    emit('lineage', {q: ','.join(REQUIRES[q]) for q in QUERIES})
    return World(ctx.copy(), deepcopy(spec), app, spec.values.copy(), allow, executed, reads, ledger, events)

def baseline(world: World) -> dict[str, str]:
    # Ω0 is predeclared: real external outcome and check values, NOT gate code.
    doc = {'outcome': world.ledger['status'], 'amount': world.ledger['amount'],
           'channel': world.ledger['channel'], 'explanation': 'Payment evaluated under declared enterprise rules.'}
    doc.update({'check.'+k: str(int(v)) for k, v in world.actual_evaluations.items()})
    return doc
