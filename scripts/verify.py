"""One-command validation. Missing tools are BLOCKED, never PASS.
--reference-only executes available reference/formal gates but cannot release Rust.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]

def source_fingerprint():
    h=hashlib.sha256();count=0
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(x in rel.parts for x in ('results','target','.git','__pycache__','.venv')):continue
        h.update(str(rel).replace('\\','/').encode()+b'\0'+p.read_bytes()+b'\0');count+=1
    return h.hexdigest(),count

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference-only',action='store_true');a=parser.parse_args()
    out=ROOT/'results/validation';out.mkdir(parents=True,exist_ok=True);steps=[]
    def run(name,cmd,timeout=120):
        try:
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=timeout,check=False)
            (out/(name+'.log')).write_text(p.stdout+'\n'+p.stderr)
            step={'name':name,'status':'PASS' if p.returncode==0 else 'FAIL','exit_code':p.returncode,'command':cmd}
        except (OSError,subprocess.TimeoutExpired) as e:
            step={'name':name,'status':'BLOCKED','exit_code':None,'reason':str(e),'command':cmd}
            (out/(name+'.log')).write_text(str(e)+'\n')
        steps.append(step);print(name+': '+step['status'],flush=True);return step['status']=='PASS'
    run('boundary-check',[sys.executable,'scripts/audit_boundaries.py'])
    run('reference-tests',[sys.executable,'-m','unittest','discover','-s','research/tests','-v'])
    run('reference-run',[sys.executable,'research/reference/run.py'])
    run('reference-mutations',[sys.executable,'research/tests/mutation_check.py'])
    run('formal-z3',[sys.executable,'formal/check.py'])
    run('formal-witness-replay',[sys.executable,'scripts/replay_formal.py'])
    run('reference-determinism',[sys.executable,'scripts/determinism.py'],timeout=150)
    cargo=shutil.which('cargo')
    rust_gates=['rust-runtime-build','rust-runtime-tests','rust-research-build','rust-research-tests','rust-harness','rust-differential']
    if not a.reference_only and cargo:
        ok=True
        for area in ('runtime','research'):
            ok=run('rust-'+area+'-build',[cargo,'build','--manifest-path',area+'/Cargo.toml','--workspace','--locked','--offline'],timeout=180) and ok
            ok=run('rust-'+area+'-tests',[cargo,'test','--manifest-path',area+'/Cargo.toml','--workspace','--locked','--offline'],timeout=180) and ok
        suffix='.exe' if os.name=='nt' else ''
        checker=ROOT/'runtime/target/debug'/('isa-checker'+suffix)
        harness=ROOT/'research/target/debug'/('isa-harness'+suffix)
        if ok:
            harness_ok = run('rust-harness',[str(harness),'--checker',str(checker),'--out',str(ROOT/'results/rust')])
            if harness_ok:
                run('rust-differential',[sys.executable,'scripts/compare_rust.py','--checker',str(checker)])
            else:
                steps.append({'name':'rust-differential','status':'NOT_RUN','exit_code':None,'reason':'Rust harness failed; archived files are not treated as fresh results'})
        else:
            for name in ('rust-harness','rust-differential'):
                steps.append({'name':name,'status':'NOT_RUN','exit_code':None,'reason':'Rust build/test prerequisite failed'})
    else:
        for name in rust_gates:
            steps.append({'name':name,'status':'NOT_RUN','exit_code':None,'reason':'Explicit reference-only mode' if cargo else 'Rust compiler/Cargo unavailable in this environment'})
    source,count=source_fingerprint()
    release_ready=not a.reference_only and all(s['status']=='PASS' for s in steps) and all(any(s['name']==g and s['status']=='PASS' for s in steps) for g in rust_gates)
    summary={'release_ready':release_ready,'status':'PASS' if release_ready else 'VALIDATION_INCOMPLETE',
             'mode':'reference-only' if a.reference_only else 'full','steps':steps,
             'source_sha256':source,'source_file_count':count,'python':platform.python_version(),'platform':platform.platform(),
             'rustc_available':shutil.which('rustc') is not None,'cargo_available':cargo is not None,
             'ci_remote_run':'NOT_RUN','format_rustfmt':'NOT_RUN','production_attestation':'NOT_IMPLEMENTED',
             'note':'Passed reference/formal gates must not be reported as compiled Rust validation.'}
    (out/'verification.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':summary['status'],'release_ready':release_ready,'source_sha256':source},indent=2))
    if a.reference_only:
        raise SystemExit(0 if all(s['status']=='PASS' for s in steps if not s['name'].startswith('rust-')) else 1)
    raise SystemExit(0 if release_ready else 1)
if __name__=='__main__':main()
