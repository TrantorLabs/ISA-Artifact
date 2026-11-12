"""Run reference worlds through a separately staged evidence-only process."""
from __future__ import annotations
import argparse
import csv as csv_module
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from wire import dump, load, digest
from engine import baseline
from scenarios import IDS, build, system_truth, system_public
from system_checker import check as check_system
from oracle import expected

ROOT = Path(__file__).resolve().parents[2]

def isolated_check(context, seal, evidence, backend='reference', binary=None):
    with tempfile.TemporaryDirectory(prefix='isa-checker-') as temporary:
        td = Path(temporary)
        (td/'context.isa').write_bytes(dump(context)); (td/'seal.isa').write_bytes(dump(seal))
        for p in (td/'context.isa',td/'seal.isa'): p.chmod(0o444)
        if backend == 'reference':
            for name in ('checker.py','wire.py'):
                shutil.copyfile(Path(__file__).parent/name,td/name)
            cmd = [sys.executable,'-I',str(td/'checker.py'),'--context',str(td/'context.isa'),'--seal',str(td/'seal.isa')]
        else:
            if binary is None: raise ValueError('Rust checker binary is required')
            cmd = [str(Path(binary).resolve()),'--context',str(td/'context.isa'),'--seal',str(td/'seal.isa')]
        completed = subprocess.run(cmd,input=dump(evidence),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   cwd=td,env={'LANG':'C.UTF-8'},close_fds=True,timeout=15,check=False)
        if completed.returncode != 0:
            raise RuntimeError(f'checker exited {completed.returncode}: {completed.stderr.decode(errors="replace")}')
        return load(completed.stdout)

def evaluate_all(output: Path, backend: str='reference', binary=None):
    rows=[]; index={}
    for name in IDS:
        case=build(name)
        # Critical sequencing: the checker executes before the oracle computes expected values.
        report=isolated_check(case.context,case.seal,case.evidence,backend,binary)
        oracle=expected(case.world,case.context,case.seal,case.evidence)
        matched=report['verdict']==oracle['verdict'] and all(report['formation.'+k]==v for k,v in oracle['formation_states'].items())
        if not matched: raise AssertionError((name,report,oracle))
        path=output/'cases'/name;path.mkdir(parents=True,exist_ok=True)
        for fn,doc in [('context',case.context),('evidence',case.evidence),('collector-seal',case.seal),('report',report),('observation-omega0',baseline(case.world))]:
            (path/(fn+'.isa')).write_bytes(dump(doc))
            (path/(fn+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        hidden=output/'research-only'/name;hidden.mkdir(parents=True,exist_ok=True)
        (hidden/'oracle.json').write_text(json.dumps(oracle,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        events=[{'channel':n,'fields':d} for n,d in case.world.events]
        (hidden/'actual-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        system_evidence = system_public(case.system)
        system_report = check_system(system_evidence)
        sy = system_truth(case.system)
        assert system_report['coverage'] == str(int(sy['coverage']))
        assert system_report['mediation'] == str(int(sy['mediation']))
        (path/'system-evidence.isa').write_bytes(dump(system_evidence))
        (path/'system-evidence.json').write_text(json.dumps(system_evidence,sort_keys=True,indent=2)+'\n')
        (path/'system-report.isa').write_bytes(dump(system_report))
        (path/'system-report.json').write_text(json.dumps(system_report,sort_keys=True,indent=2)+'\n')
        (hidden/'system-truth.json').write_text(json.dumps(sy,sort_keys=True,indent=2)+'\n')
        row={'id':name,'backend':backend,'observation_regime':'omega0-separate','audit':report['audit'],
             'path':report['formation.path'],'attribution':report['formation.attribution'],'constraint':report['formation.constraint'],
             'verdict':report['verdict'],'issues':report['issues'],'coverage':sy['coverage'],'mediation':sy['mediation'],'expectation_matched':matched}
        rows.append(row); index[name]=case
    a,b=index['E00'],index['E03-S']
    pair={'baseline_equal':dump(baseline(a.world))==dump(baseline(b.world)),
          'non_target_context_equal':dump(a.context)==dump(b.context),
          'structural_evidence_different':dump(a.evidence)!=dump(b.evidence),
          'audit_is_not_observation_regime':True,
          'a_observation_digest':digest(baseline(a.world)), 'b_observation_digest':digest(baseline(b.world))}
    assert all(pair[k] for k in ('baseline_equal','non_target_context_equal','structural_evidence_different'))
    (output/'pair.json').write_text(json.dumps(pair,sort_keys=True,indent=2)+'\n')
    (output/'matrix.json').write_text(json.dumps(rows,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    with (output/'matrix.csv').open('w',newline='') as handle:
        writer=csv_module.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'backend':backend,'scenarios':len(rows),'matched':sum(r['expectation_matched'] for r in rows),
             'verdict_counts':{v:sum(r['verdict']==v for r in rows) for v in ('Conformant','Non-conformant','Unadjudicable')},
             'claim':'Directed synthetic cases, not empirical safety probabilities.',
             'rust_execution': 'EXECUTED' if backend=='rust' else 'NOT_RUN'}
    (output/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/reference');p.add_argument('--backend',choices=('reference','rust'),default='reference');p.add_argument('--checker',type=Path)
    args=p.parse_args();print(json.dumps(evaluate_all(args.out,args.backend,args.checker),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
