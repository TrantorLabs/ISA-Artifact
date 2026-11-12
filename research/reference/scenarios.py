"""Scenario labels remain in research. They mutate relations, never predicates."""
from __future__ import annotations
from dataclasses import dataclass
from engine import Spec, World, context, run, baseline
from evidence import Collector
from wire import CHANNELS, digest

IDS = ('E00','E01','E02-S','E02-A','E02-E','E03-S','E03-B',
       'E04-I','E04-N','E04-S','E04-P','E04-L','E07','E08','E09','E10',
       'M1-APPLICABILITY','M2-CONTRACT','M2-CHERRY','E11-BLIND-SHADOW','E12-DENY','E13-LOW-VALUE')

@dataclass
class Case:
    name: str
    context: dict[str,str]
    evidence: dict[str,str]
    seal: dict[str,str]
    world: World
    system: dict[str,object]

def system_world(kind: str) -> dict[str,object]:
    channels = ['standard','batch','privileged']
    edges = [('candidate','gate')] + [('gate','executor-'+c) for c in channels] + [('executor-'+c,c) for c in channels]
    governed = channels[:]
    if kind == 'E07': governed.remove('batch')
    if kind == 'E08': edges.append(('candidate','executor-batch'))
    if kind == 'E09': edges.append(('candidate','executor-standard'))
    return {'actual_channels':channels,'governed_channels':governed,'edges':edges,
            'gate_tables': {'gate': [False,True]}, 'root':'candidate'}

def system_public(s: dict[str, object]) -> dict[str, str]:
    """Finite graph evidence, independent of all research labels."""
    d = {'schema': 'isa-system-1', 'root': s['root'],
         'actual': ','.join(sorted(s['actual_channels'])),
         'governed': ','.join(sorted(s['governed_channels'])),
         'edges': ','.join(a+'>'+b for a,b in sorted(s['edges'])),
         'gates': ','.join(sorted(s['gate_tables']))}
    for k,v in sorted(s['gate_tables'].items()):
        d['gate.'+k+'.outputs'] = ','.join(str(int(x)) for x in v)
    return d

def system_truth(s: dict[str,object]) -> dict[str,bool]:
    channels = set(s['actual_channels']); governed = set(s['governed_channels'])
    edges = s['edges']; gates = s['gate_tables']; effective = {g for g,t in gates.items() if set(t) == {False,True}}
    def paths(node, target, seen):
        if node == target: return [seen+(node,)]
        return [p for a,b in edges if a == node and b not in seen for p in paths(b,target,seen+(node,))]
    mediation = all(any(n in effective for n in p) for c in governed for p in paths(s['root'],c,()))
    return {'coverage':channels.issubset(governed),'mediation':mediation}

def build(name: str) -> Case:
    if name not in IDS: raise ValueError('unknown scenario')
    spec = Spec()
    if name == 'E01': spec.execution_instance = 'u-other'
    if name == 'E02-S': spec.bound_source = 'unrelated-record'
    if name == 'E02-A': spec.authority_scopes = ('payment','read-only')
    if name == 'E02-E': spec.bound_controller = 'adviser-1'
    if name in ('E03-S','E11-BLIND-SHADOW'): spec.code[-1] = 'T'
    if name == 'E03-B': spec.code[-1] = 'O:0,1,2,3'; spec.values['recipient'] = False
    if name == 'E09': spec.route = 'direct'; spec.values['recipient'] = False
    if name == 'M1-APPLICABILITY':
        spec.values['recipient'] = False
        spec.include_applicable = ('transaction','dual','channel')
        spec.code[-1] = 'A:1,2,3'
    if name == 'E12-DENY': spec.values['recipient'] = False
    if name == 'E13-LOW-VALUE':
        spec.amount = 100; spec.code[-1] = 'A:0,1,3'; spec.authority_scopes = ('payment','read-only')
    ctx = context(spec)
    if name == 'E04-N':
        for ch in CHANNELS: ctx['writers.'+ch] = 'collector-1,controller-1'
    if name == 'E04-S': ctx['queries'] = 'path,source,authority,effect,eligibility'
    collector = Collector(ctx)
    world = run(spec,ctx,collector.observe)
    replace = {'program.4':'O:0,1,2,3'} if name == 'E04-P' else {}
    omit = ('lineage.control',) if name == 'E04-L' else ()
    if name in ('E10','E11-BLIND-SHADOW'):
        omit = tuple(k for k in collector.records if k.startswith('program.'))
    evidence, seal = collector.finish(replace,omit)
    if name == 'E04-I': evidence['execution.amount'] = '999'
    if name == 'M2-CONTRACT':
        forged = ctx.copy(); forged['queries'] = 'path'
        evidence['context_digest'] = digest(forged)
    if name == 'M2-CHERRY':
        # Replace the designated original bytes, leaving the trusted checkpoint intact.
        evidence['program.4'] = 'T'
    return Case(name,ctx,evidence,seal,world,system_world(name))

# Research-only downstream execution witnesses: events are replaced BEFORE
# the trusted synthetic collector observes them, never after seal issuance.
# This models a truthful trace of a faulty executor, not a forged audit record.
EXECUTION_WITNESSES = (
    ('deny_but_paid', 'E12-DENY', {'status': 'paid', 'amount': '200000'}),
    ('paid_amount_drift', 'E00', {'amount': '300000'}),
    ('allowed_but_not_executed', 'E00', {'status': 'refused', 'amount': '0'}),
)

def executor_witness(base: str, changed_execution: dict[str, str]) -> Case:
    if base not in ('E00', 'E12-DENY') or not changed_execution or not set(changed_execution) <= {'status', 'amount'}:
        raise ValueError('unsupported bounded executor witness')
    case = build(base)
    collector = Collector(case.context)
    actual_events: list[tuple[str, dict[str, str]]] = []
    ledger: dict[str, str] | None = None
    for event_name, fields in case.world.events:
        observed = fields.copy()
        if event_name == 'execution':
            observed.update({'execution.' + key: value for key, value in changed_execution.items()})
            ledger = {key.removeprefix('execution.'): value for key, value in observed.items()}
        collector.observe(event_name, observed)
        actual_events.append((event_name, observed))
    if ledger is None:
        raise AssertionError('missing execution event')
    case.world.events = actual_events
    case.world.ledger = ledger
    case.world.executed = ledger['status'] == 'paid'
    case.evidence, case.seal = collector.finish()
    return case
