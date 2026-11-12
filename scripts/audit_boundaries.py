"""Static import, workspace, source-freeze, and artifact hygiene checks.
Static checks do not substitute for Rust compilation.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import tomllib
ROOT=Path(__file__).resolve().parents[1]
def main():
    assertions=[]
    registry=json.loads((ROOT/'docs/SOURCE_REGISTRY.json').read_text())
    for item in registry:
        path=ROOT/item['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],path
    assertions.append('all_seven_source_files_byte_identical')
    graph={}
    for p in [*(ROOT/'runtime').glob('*/Cargo.toml'),*(ROOT/'research').glob('*/Cargo.toml')]:
        data=tomllib.loads(p.read_text());name=data['package']['name'];graph[name]=list(data.get('dependencies',{}))
        for dep,info in data.get('dependencies',{}).items():
            assert isinstance(info,dict) and 'path' in info,(p,dep,'unexpected registry dependency')
            target=(p.parent/info['path']).resolve();assert (target/'Cargo.toml').exists(),target
            if p.is_relative_to(ROOT/'runtime'):
                assert target.is_relative_to(ROOT/'runtime'),(p,dep,'runtime imported research')
    assert set(graph['isa-checker'])=={'isa-core'}
    assertions += ['seven_local_rust_packages','zero_registry_dependencies','checker_dependency_is_core_only','runtime_cannot_import_research_or_formal']
    for p in (ROOT/'runtime').rglob('*.rs'):
        text=p.read_text()
        assert not re.search(r'\b(?:use|extern\s+crate)\s+isa_(?:oracle|scenarios|harness)',text),p
        assert not any(x in text for x in ('include_bytes!','include_str!','unsafe {','unsafe{')),p
    assertions.append('no_hidden_import_or_file_inclusion_in_runtime_sources')
    for p in (ROOT/'research/reference').glob('*.py'):
        tree=ast.parse(p.read_text())
        if p.name in ('checker.py','evidence.py','system_checker.py'):
            imports=[x.module for x in ast.walk(tree) if isinstance(x,ast.ImportFrom)]
            assert not set(imports)&{'oracle','scenarios'},(p,imports)
    assertions.append('reference_checker_and_collector_do_not_import_oracle')
    for p in (ROOT/'formal').glob('*.py'):ast.parse(p.read_text())
    result={'status':'PASS','checks':assertions,'cargo_typecheck':'NOT_PERFORMED_BY_THIS_SCRIPT','dependency_graph':graph}
    output=ROOT/'results/validation';output.mkdir(parents=True,exist_ok=True)
    (output/'boundary-check.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS','checks':len(assertions),'packages':len(graph)}))
if __name__=='__main__':main()
