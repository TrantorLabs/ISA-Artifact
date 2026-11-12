"""Real source mutations of the reference checker, run in isolated processes.
A killed mutant is an intentionally wrong checker detected by the test, not a
safety verdict about an AI. No Rust mutation result is claimed here.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/reference'))
from wire import dump,load
from scenarios import build
from oracle import expected

MUTATIONS=[
 ('MU01_SHADOW_AS_GATE','E03-S',"control = (d['evaluation.instance']", "control = (True or d['evaluation.instance']",'constraint'),
 ('MU02_UNKNOWN_AS_NEGATIVE','E10',"'verdict':'Unadjudicable'", "'verdict':'Non-conformant'",'verdict'),
 ('MU03_IGNORE_SCOPE','E02-A',"d['authority.scope2'] == context['required_scope']",'True','attribution'),
 ('MU04_IGNORE_PRESERVATION','E04-P',"established = bool(prereq and all(dimensions.values()) and found is not None)","dimensions['Preservation'] = True\n    established = bool(prereq and all(dimensions.values()) and found is not None)",'verdict'),
 ('MU05_IGNORE_LOCALIZATION','E04-L',"established = bool(prereq and all(dimensions.values()) and found is not None)","dimensions['Localization'] = True\n    established = bool(prereq and all(dimensions.values()) and found is not None)",'verdict'),
 ('MU06_IGNORE_CONTEXT_COMMITMENT','M2-CONTRACT',"prereq &= digest(context) == d.get('context_digest') == seal.get('context_digest')",'prereq &= True','verdict'),
]

def main():
    original=(ROOT/'research/reference/checker.py').read_text();rows=[]
    for name,scenario,old,new,target in MUTATIONS:
        if original.count(old)!=1:raise AssertionError((name,'patch site not unique'))
        text=original.replace(old,new)
        if name=='MU01_SHADOW_AS_GATE':
            # Replace both control and policy obligations with the existence of checks.
            text=text.replace("eligibility = rows == policy and (d['admission.state'] == ('allow' if now else 'deny'))",'eligibility = True')
        compile(text,name,'exec')
        c=build(scenario);truth=expected(c.world,c.context,c.seal,c.evidence)
        with tempfile.TemporaryDirectory(prefix='isa-mutant-') as tmp:
            d=Path(tmp);(d/'checker.py').write_text(text);shutil.copyfile(ROOT/'research/reference/wire.py',d/'wire.py')
            (d/'context.isa').write_bytes(dump(c.context));(d/'seal.isa').write_bytes(dump(c.seal))
            r=subprocess.run([sys.executable,'-I',str(d/'checker.py'),'--context',str(d/'context.isa'),'--seal',str(d/'seal.isa')],input=dump(c.evidence),capture_output=True,timeout=15,cwd=d,env={'LANG':'C.UTF-8'},check=False)
            if r.returncode:raise AssertionError((name,'mutant crashed, not a semantic kill',r.stderr.decode()))
            observed=load(r.stdout)
        killed=observed['verdict']!=truth['verdict'] or any(observed['formation.'+k]!=v for k,v in truth['formation_states'].items())
        if not killed:raise AssertionError((name,'survived',observed,truth))
        rows.append({'id':name,'scenario':scenario,'killed':killed,'expected_verdict':truth['verdict'],'mutant_verdict':observed['verdict'],'backend':'python-reference-source-mutation'})
    out=ROOT/'results/validation';out.mkdir(parents=True,exist_ok=True)
    (out/'mutation-report.json').write_text(json.dumps(rows,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'mutants':len(rows),'killed':sum(x['killed'] for x in rows),'backend':'python-reference'}))
if __name__=='__main__':main()
