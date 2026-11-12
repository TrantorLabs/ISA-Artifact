"""Full Rust/Python differential check. Requires real compiled Rust executables."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research/reference'))
from wire import load
from scenarios import IDS,EXECUTION_WITNESSES,executor_witness
from oracle import expected
from run import isolated_check

def main():
    p=argparse.ArgumentParser();p.add_argument('--checker',type=Path,required=True);args=p.parse_args()
    subprocess.run([sys.executable,str(ROOT/'research/reference/run.py'),'--backend','rust','--checker',str(args.checker),'--out',str(ROOT/'results/rust-checker-differential')],check=True,timeout=90)
    comparisons=0
    for name in IDS:
        ref=load((ROOT/'results/reference/cases'/name/'report.isa').read_bytes())
        alt=load((ROOT/'results/rust-checker-differential/cases'/name/'report.isa').read_bytes())
        actual=load((ROOT/'results/rust/cases'/name/'report.isa').read_bytes())
        assert ref==alt==actual,(name,'Rust/Python report disagreement')
        for filename in ('context.isa','collector-seal.isa','evidence.isa','observation-omega0.isa','system-evidence.isa','system-report.isa'):
            assert (ROOT/'results/reference/cases'/name/filename).read_bytes()==(ROOT/'results/rust/cases'/name/filename).read_bytes(),(name,filename)
            comparisons+=1
        comparisons+=2
    # Independently executed checker binaries must agree on honest, sealed
    # downstream execution faults; no research-only truth is sent to either.
    for label,base,changes in EXECUTION_WITNESSES:
        case=executor_witness(base,changes)
        truth=expected(case.world,case.context,case.seal,case.evidence)
        py=isolated_check(case.context,case.seal,case.evidence)
        rs=isolated_check(case.context,case.seal,case.evidence,backend='rust',binary=args.checker)
        assert py==rs,(label,'Rust/Python executor witness disagreement')
        assert rs['verdict']==truth['verdict'],(label,'Independent oracle disagreement')
        assert all(rs['formation.'+k]==v for k,v in truth['formation_states'].items()),label
        comparisons+=1
    report={'status':'PASS','scenarios':len(IDS),'comparisons':comparisons,'rust_actually_executed':True,'execution_relation_witnesses':len(EXECUTION_WITNESSES)}
    (ROOT/'results/validation/rust-differential.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
