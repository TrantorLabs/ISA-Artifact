"""Finite graph system assurance, independent from instance adjudication."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from wire import load,dump,csv

def check(d):
    if d.get('schema') != 'isa-system-1': raise ValueError('invalid system schema')
    root=d.get('root','')
    if not root: raise ValueError('missing root')
    actual=set(csv(d.get('actual','')));governed=set(csv(d.get('governed','')))
    adj={};nodes=set()
    for text in csv(d.get('edges','')):
        a,b=text.split('>')
        if not a or not b: raise ValueError('empty vertex')
        adj.setdefault(a,[]).append(b);nodes.update((a,b))
    if len(nodes)>32 or not actual: raise ValueError('finite graph bounds')
    effective={g for g in csv(d.get('gates','')) if {'0','1'}.issubset(csv(d.get('gate.'+g+'.outputs','')))}
    def reach(blocked):
        seen=set();todo=[root]
        while todo:
            n=todo.pop()
            if n in blocked or n in seen:continue
            seen.add(n);todo.extend(adj.get(n,[]))
        return seen
    if not actual.issubset(reach(set())): raise ValueError('unreachable declared actual channel')
    return {'schema':'isa-system-report-1','scope':'declared-finite-graph',
            'coverage':str(int(actual.issubset(governed))), 'mediation':str(int(not(governed & reach(effective))))}
if __name__=='__main__':
    try:sys.stdout.buffer.write(dump(check(load(sys.stdin.buffer.read(1_048_577)))))
    except (OSError,ValueError) as e:print(str(e),file=sys.stderr);raise SystemExit(2)
