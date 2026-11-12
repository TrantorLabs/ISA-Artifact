"""Replay the solver-found controller witness in the four-constraint reference engine.
Two formal inputs map to (recipient AND transaction) and (dual AND channel).
The reference checker remains a separate process. Rust replay is a separate gate.
"""
from __future__ import annotations
import json
from itertools import product
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research/reference'))
from engine import Spec,context,run,baseline,evaluate
from evidence import Collector
from oracle import ground_truth
from run import isolated_check
from wire import dump,KINDS

def code(root):
    p=['E:recipient','E:transaction','E:dual','E:channel','A:0,1','A:2,3']
    if root==0:return p,4
    if root==1:return p,5
    p.append({2:'A:4,5',3:'O:4,5',4:'T'}[root]);return p,6

def main():
    text=(ROOT/'results/formal/FQ1.txt').read_text()
    roots=[]
    for prefix in ('a','b'):
        match=re.search(r'^'+prefix+r'_root -> ([0-4])\s*$',text,re.M)
        if not match:
            match=re.search(r'\(define-fun '+prefix+r'_root \(\) Int\s+([0-4])\)',text)
        if not match:raise ValueError('cannot extract solver controller witness')
        roots.append(int(match.group(1)))
    # Complete finite projection for the five controller expressions:
    # two formal inputs are (recipient AND transaction) and (dual AND channel).
    # Every one of the 16 four-check valuations is exercised in the running engine.
    tested = 0
    for controller in range(5):
        instructions, root = code(controller)
        for bits in product((False, True), repeat=4):
            left, right = (bits[0] and bits[1]), (bits[2] and bits[3])
            abstract = (left, right, left and right, left or right, True)[controller]
            actual, _ = evaluate(instructions, root, dict(zip(KINDS, bits)))
            if actual != abstract:
                raise AssertionError((controller, bits, abstract, actual))
            tested += 1
    rows=[];observations=[]
    for r in roots:
        s=Spec();s.code,s.root=code(r);ctx=context(s);collector=Collector(ctx);world=run(s,ctx,collector.observe);ev,seal=collector.finish()
        report=isolated_check(ctx,seal,ev);truth=ground_truth(world);observations.append(dump(baseline(world)))
        rows.append({'solver_controller':r,'code':s.code,'root':s.root,'formation_truth':truth,'checker_verdict':report['verdict']})
    assert observations[0]==observations[1] and rows[0]['formation_truth']['form_conform']!=rows[1]['formation_truth']['form_conform']
    result={'backend':'python-reference','solver_witness_replayed':True,'observation_equal':True,'worlds':rows,'rust_replay':'NOT_RUN',
            'four_check_projection_vectors_tested':tested,'finite_controller_count':5,
            'refinement_scope':'80 admission outputs: five finite controllers x sixteen four-check valuations; not a whole-runtime refinement proof'}
    (ROOT/'results/formal/replay.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('Solver witness replay: PASS (python-reference)')
if __name__=='__main__':main()
