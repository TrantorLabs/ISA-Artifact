"""Research-only semantic oracle. Never imported by the checker or collector.
Truth is derived from the engine's actual state, not from expected labels.
"""
from __future__ import annotations
from itertools import product
from typing import Any
from wire import CHANNELS, KINDS, QUERIES, REQUIRES, channel, csv, digest

def _value(code: list[str], root: int, assignment: dict[str,bool]) -> bool:
    instruction = code[root]
    if instruction == 'T': return True
    if instruction == 'F': return False
    if instruction[:2] == 'E:': return assignment[instruction[2:]]
    args = tuple(_value(code,int(j),assignment) for j in instruction[2:].split(','))
    return False not in args if instruction[0] == 'A' else True in args

def ground_truth(world: Any) -> dict[str, bool]:
    s,ctx = world.spec,world.context
    # Independent formation truth: inspect the actual downstream effect, not
    # the checker-reconstructed evidence or the experiment's expected label.
    ledger = world.ledger
    executed_binding = (
        (ledger['status'] == 'paid' and world.admission and ledger['amount'] == str(s.amount))
        or (ledger['status'] == 'refused' and ledger['amount'] == '0')
    )
    p = (s.execution_instance == ctx['instance'] and s.execution_decision == ctx['decision']
         and s.execution_admission == ctx['admission'] and s.route != 'direct'
         and s.amount == int(ctx['amount'])
         and ledger['instance'] == ctx['instance'] and ledger['decision'] == ctx['decision']
         and ledger['admission'] == ctx['admission'] and executed_binding)
    a = s.bound_source == s.actual_source and bool(s.actual_source)
    a &= s.authority_scopes[0] == ctx['required_scope'] and bool(s.authority_subjects[0])
    if 'dual' in world.applicable:
        a &= s.authority_scopes[1] == ctx['required_scope'] and s.authority_subjects[0] != s.authority_subjects[1] and bool(s.authority_subjects[1])
    a &= s.bound_controller == ctx['controller']
    selected = world.applicable if s.include_applicable is None else s.include_applicable
    c = selected == world.applicable
    alternatives = []
    for bits in product((False,True), repeat=len(world.applicable)):
        assignment = s.values.copy(); assignment.update(zip(world.applicable,bits))
        actual = _value(s.code,s.root,assignment)
        alternatives.append((bits,actual))
        c &= actual == all(bits)
    for index in range(len(world.applicable)):
        dependent = False
        for bits,actual in alternatives:
            switched = list(bits); switched[index] = not switched[index]
            dependent |= next(a for b,a in alternatives if b == tuple(switched)) != actual
        c &= dependent
    c &= set(world.applicable).issubset(world.reads)
    c &= world.admission == _value(s.code,s.root,s.values)
    return {'path':bool(p),'attribution':bool(a),'constraint':bool(c),'form_conform':bool(p and a and c)}

def audit_reality(world: Any, context: dict[str,str], seal: dict[str,str], evidence: dict[str,str]) -> dict[str,bool]:
    # Independent oracle compares observable assertions to actual emitted relations;
    # it does not call check(), queries() or any checker inference function.
    raw = dict(item for _, fields in world.events for item in fields.items())
    pre = (int(context['declared_tick']) < int(context['start_tick'])
           and context == world.context and digest(context) == evidence.get('context_digest') == seal.get('context_digest'))
    pre &= evidence.get('start_tick') == seal.get('start_tick') == context['start_tick']
    pre &= evidence.get('finish_tick') == seal.get('finish_tick')
    integrity = all(digest(channel(evidence,k)) == seal.get('digest.'+k) for k in CHANNELS)
    independence = not all(context['controller'] in csv(context.get('writers.'+k,'')) for k in CHANNELS)
    coverage = set(csv(context.get('queries',''))) == set(QUERIES) and set(csv(context.get('channels',''))) == set(CHANNELS)
    coverage &= all(set(v).issubset(csv(context.get('requires.'+q,''))) for q,v in REQUIRES.items())
    coverage &= all(k in evidence for k in raw if not k.startswith('lineage.'))
    preservation = all(channel(evidence,k) == channel(raw,k) for k in CHANNELS if k != 'lineage')
    localization = all(set(REQUIRES[q]).issubset(csv(evidence.get('lineage.'+q,''))) for q in QUERIES)
    return {'prerequisite':bool(pre),'integrity':bool(integrity),'independence':bool(independence),
            'scopecoverage':bool(coverage),'preservation':bool(preservation),'localization':bool(localization)}

def expected(world: Any, context: dict[str,str], seal: dict[str,str], evidence: dict[str,str]) -> dict[str,Any]:
    truth = ground_truth(world)
    audit = audit_reality(world,context,seal,evidence)
    valid = all(audit.values())
    return {'formation_truth':truth, 'audit_reality':audit,
            'verdict': ('Conformant' if truth['form_conform'] else 'Non-conformant') if valid else 'Unadjudicable',
            'formation_states': {k:('supported' if v else 'refuted') if valid else 'not_adjudicated' for k,v in truth.items() if k != 'form_conform'}}
