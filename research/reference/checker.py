"""Evidence-only executable reference checker. No engine/scenario/oracle imports.
Its outputs are claims under the supplied, separately trusted collector root.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
# When staged by the harness this directory contains only checker.py and wire.py.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wire import CHANNELS, KINDS, QUERIES, REQUIRES, WireError, bool_value, channel, csv, digest, integer, load, dump

FIELDS = {
    'decision': ('instance','id','amount','candidate'),
    'source': ('instance','actual','bound'),
    'authority': ('instance','h1','h2','scope1','scope2'),
    'effect': ('instance','actual_controller','bound_controller'),
    'evaluation': ('instance','applicable', *KINDS),
    'admission': ('instance','id','decision','state','reads','controller'),
    'execution': ('instance','decision','admission','status','amount','channel','route'),
    'lineage': QUERIES,
}

def allowed_fields(d: dict[str, str]) -> set[str]:
    allowed = {'schema','context_digest','start_tick','finish_tick','program.root','program.count'}
    for name, fields in FIELDS.items():
        allowed.update(name+'.'+f for f in fields)
    # Bound all dynamic array indices, including hostile documents.
    allowed.update('program.'+str(i) for i in range(32))
    return allowed

def circuit(d: dict[str, str], values: dict[str, bool]) -> tuple[bool, set[str]]:
    """Bottom-up independent interpreter, not the engine's recursive evaluator."""
    n = integer(d.get('program.count',''), 32)
    root = integer(d.get('program.root',''), 31)
    if n == 0 or root >= n:
        raise WireError('program cardinality/root')
    computed: list[bool] = []
    supports: list[set[str]] = []
    for i in range(n):
        op = d.get('program.'+str(i), '')
        deps: set[str] = set()
        if op in ('T','F'):
            answer = op == 'T'
        elif op.startswith('E:'):
            k = op[2:]
            if k not in values:
                raise WireError('program evaluator outside domain')
            answer = values[k]; deps.add(k)
        elif op.startswith(('A:', 'O:')):
            refs = [integer(x,31) for x in csv(op[2:])]
            if not refs or any(x >= i for x in refs):
                raise WireError('cyclic or empty operator')
            args = [computed[j] for j in refs]
            answer = all(args) if op[0] == 'A' else any(args)
            for j in refs:
                deps.update(supports[j])
        else:
            raise WireError('unknown instruction')
        computed.append(answer); supports.append(deps)
    return computed[root], supports[root]

def execution_binding(c: dict[str, str], d: dict[str, str]) -> bool:
    """Current executed effect must remain bound to the admitted decision."""
    if d['decision.amount'] != c['amount']:
        return False
    if d['execution.status'] == 'paid':
        return d['admission.state'] == 'allow' and d['execution.amount'] == d['decision.amount']
    if d['execution.status'] == 'refused':
        return d['execution.amount'] == '0'
    return False

def queries(context: dict[str,str], d: dict[str,str]) -> dict[str,bool]:
    u = context['instance']
    applicable = tuple(k for k in KINDS if k != 'dual' or integer(context['amount']) > integer(context['dual_threshold']))
    values = {k: bool_value(d['evaluation.'+k]) for k in KINDS}
    now, reads = circuit(d, values)
    path = (all(d[p+'.instance'] == u for p in ('decision','source','authority','effect','evaluation','admission','execution'))
            and d['decision.id'] == context['decision'] == d['admission.decision'] == d['execution.decision']
            and d['admission.id'] == context['admission'] == d['execution.admission']
            and bool(d['decision.candidate']) and d['execution.route'] == 'standard'
            and execution_binding(context, d))
    source = d['source.instance'] == u and bool(d['source.actual']) and d['source.bound'] == d['source.actual']
    authority = (d['authority.instance'] == u and bool(d['authority.h1'])
                 and d['authority.scope1'] == context['required_scope'])
    if 'dual' in applicable:
        authority = authority and bool(d['authority.h2']) and d['authority.h1'] != d['authority.h2'] and d['authority.scope2'] == context['required_scope']
    effect = (d['effect.instance'] == u and bool(d['effect.actual_controller'])
              and d['effect.bound_controller'] == d['effect.actual_controller'] == d['admission.controller'])
    rows: list[bool] = []
    for bits in range(1 << len(applicable)):
        alternate = values.copy()
        alternate.update({k: bool(bits & (1 << i)) for i,k in enumerate(applicable)})
        rows.append(circuit(d, alternate)[0])
    # A read is not control. Require actual dependence in the finite evaluation domain.
    influence = all(any(rows[b] != rows[b ^ (1 << i)] for b in range(len(rows))) for i in range(len(applicable)))
    control = (d['evaluation.instance'] == u and tuple(csv(d['evaluation.applicable'])) == applicable
               and set(applicable).issubset(reads) and set(csv(d['admission.reads'])) == reads and influence)
    policy = [bits == (1 << len(applicable)) - 1 for bits in range(1 << len(applicable))]
    eligibility = rows == policy and (d['admission.state'] == ('allow' if now else 'deny'))
    return {'path':path,'source':source,'authority':authority,'effect':effect,'control':control,'eligibility':eligibility}

def check(context: dict[str,str], seal: dict[str,str], d: dict[str,str]) -> dict[str,str]:
    issues: set[str] = set()
    dimensions = dict.fromkeys(('Integrity','Independence','ScopeCoverage','Preservation','Localization'), True)
    prereq = (context.get('schema') == 'isa-context-1' and seal.get('schema') == 'isa-collector-seal-1'
              and d.get('schema') == 'isa-evidence-1')
    try:
        prereq &= context['gamma'] == ','.join(KINDS)
        prereq &= digest(context) == d.get('context_digest') == seal.get('context_digest')
        prereq &= integer(context['declared_tick']) < integer(context['start_tick'])
        prereq &= context['start_tick'] == d.get('start_tick') == seal.get('start_tick')
        prereq &= d.get('finish_tick') == seal.get('finish_tick') and integer(d['finish_tick']) >= integer(d['start_tick'])
        prereq &= context['collector'] == seal.get('collector') and context['monitor'] == seal.get('monitor')
        prereq &= all(bool(context.get(k, '')) for k in ('system', 'version', 'instance', 'decision', 'admission', 'required_scope', 'collector', 'monitor', 'controller', 'boundary', 'threat_model'))
    except (KeyError, ValueError):
        prereq = False
    if not prereq:
        issues.add('Prerequisite')
    if set(d) - allowed_fields(d):
        prereq = False; issues.add('UnknownField')
    dimensions['Integrity'] = all(seal.get('digest.'+name) == digest(channel(d,name)) for name in CHANNELS)
    declared = set(csv(context.get('channels','')))
    dimensions['Independence'] = bool(declared) and not all(context.get('controller','') in csv(context.get('writers.'+name,'')) for name in declared)
    dimensions['ScopeCoverage'] = set(csv(context.get('queries',''))) == set(QUERIES) and declared == set(CHANNELS)
    for q, required in REQUIRES.items():
        dimensions['ScopeCoverage'] &= set(required).issubset(csv(context.get('requires.'+q,'')))
    for name, fields in FIELDS.items():
        if name == 'lineage':
            continue
        dimensions['ScopeCoverage'] &= all(name+'.'+field in d for field in fields)
    try:
        count = integer(d.get('program.count',''),32)
        dimensions['ScopeCoverage'] &= count > 0 and set(channel(d,'program')) == {'program.root','program.count', *('program.'+str(i) for i in range(count))}
    except ValueError:
        dimensions['ScopeCoverage'] = False
    dimensions['Preservation'] = (digest(channel(d,'program')) == seal.get('registered_program_digest')
        and all(digest(channel(d,name)) == seal.get('monitor_digest.'+name) for name in CHANNELS if name != 'lineage'))
    found: dict[str,bool] | None = None
    try:
        found = queries(context,d)
        values = {k:bool_value(d['evaluation.'+k]) for k in KINDS}
        now, reads = circuit(d,values)
        dimensions['Preservation'] &= d['admission.state'] == ('allow' if now else 'deny')
        dimensions['Preservation'] &= set(csv(d['admission.reads'])) == reads
    except (KeyError,ValueError,OverflowError):
        dimensions['Preservation'] = False
    dimensions['Localization'] = all(set(REQUIRES[q]).issubset(csv(d.get('lineage.'+q,''))) for q in QUERIES)
    for dim, valid in dimensions.items():
        if not valid:
            issues.add(dim)
    established = bool(prereq and all(dimensions.values()) and found is not None)
    report = {'schema':'isa-report-1', 'audit':'established' if established else 'not_established',
              'issues':','.join(sorted(issues)), 'trust_scope':'synthetic-collector-root',
              'formation.path':'not_adjudicated','formation.attribution':'not_adjudicated','formation.constraint':'not_adjudicated',
              'verdict':'Unadjudicable'}
    report.update({'audit.'+dim.lower(): 'supported' if v else 'not_established' for dim,v in dimensions.items()})
    for q in QUERIES:
        report['query.'+q] = ('supported' if found[q] else 'refuted') if established and found is not None else 'not_adjudicated'
        report['lineage.'+q] = d.get('lineage.'+q,'') if established else ''
    if established and found is not None:
        p = found['path']; a = all(found[q] for q in ('source','authority','effect')); c = found['control'] and found['eligibility']
        report.update({'formation.path':'supported' if p else 'refuted',
                       'formation.attribution':'supported' if a else 'refuted',
                       'formation.constraint':'supported' if c else 'refuted',
                       'verdict':'Conformant' if p and a and c else 'Non-conformant'})
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description='Evidence-only ISA reference checker; trusts separately supplied collector checkpoints.')
    parser.add_argument('--context', required=True); parser.add_argument('--seal', required=True)
    args = parser.parse_args()
    try:
        c = load(Path(args.context).read_bytes()); s = load(Path(args.seal).read_bytes())
        d = load(sys.stdin.buffer.read(1_048_577))
        sys.stdout.buffer.write(dump(check(c,s,d)))
    except (ValueError,OSError) as exc:
        print('invalid input: '+str(exc),file=sys.stderr); return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
