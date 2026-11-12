"""Compare two fresh executions byte-for-byte. Never compare a file to itself."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
def fingerprints(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
def main():
    with tempfile.TemporaryDirectory(prefix='isa-reproduce-') as temporary:
        base=Path(temporary)
        for name in ('first','second'):
            subprocess.run([sys.executable,str(ROOT/'research/reference/run.py'),'--out',str(base/name)],check=True,capture_output=True,timeout=90)
        first,second=fingerprints(base/'first'),fingerprints(base/'second')
        assert first==second,'independent regenerations differ'
        archived=fingerprints(ROOT/'results/reference')
        assert first==archived,'committed reference evidence differs from fresh execution'
        result={'backend':'python-reference','fresh_runs':2,'compared_files':len(first),'byte_identical':True,'archive_matches':True}
    (ROOT/'results/validation/determinism.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
