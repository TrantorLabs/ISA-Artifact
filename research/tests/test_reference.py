"""Executable tests for the independent Python reference and source boundaries.
These are NOT represented as Rust compilation or Rust unit-test results.
"""
from __future__ import annotations
import ast
import copy
import importlib.util
import json
import itertools
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/reference'))
from wire import dump,load,WireError,CHANNELS,KINDS,QUERIES,channel,digest
from engine import Spec,context,run,evaluate,baseline
from evidence import Collector
from checker import check,circuit
from scenarios import IDS,build,system_truth,EXECUTION_WITNESSES,executor_witness
from oracle import expected,ground_truth
from run import isolated_check
from system_checker import check as system_check

class WireTests(unittest.TestCase):
    def test_unicode_roundtrip(self):
        d={'name':'判断\t行动\n🌈'};self.assertEqual(load(dump(d)),d)
    def test_order_canonical(self):self.assertEqual(dump({'b':'2','a':'1'}),dump({'a':'1','b':'2'}))
    def test_duplicate(self):
        with self.assertRaises(WireError):load(b'ISA/1\nx\t30\nx\t31\nEND\n')
    def test_truncated(self):
        with self.assertRaises(WireError):load(b'ISA/1\nx\t30\n')
    def test_hex_uppercase(self):
        with self.assertRaises(WireError):load(b'ISA/1\nx\tFF\nEND\n')
    def test_non_utf8(self):
        with self.assertRaises(WireError):load(b'ISA/1\nx\tff\nEND\n')
    def test_non_ascii_key(self):
        with self.assertRaises(WireError):load('ISA/1\n中\t30\nEND\n'.encode())
    def test_oversize(self):
        with self.assertRaises(WireError):load(b'x'*1_048_577)
    def test_field_limit(self):
        with self.assertRaises(WireError):dump({'x'+str(i):'v' for i in range(4097)})
    def test_two_concatenated_messages_rejected(self):
        with self.assertRaises(WireError):load(dump({'x':'1'})+dump({'x':'2'}))
    def test_deterministic_parser_fuzz(self):
        rng=random.Random(919)
        for _ in range(400):
            data=bytes(rng.randrange(256) for _ in range(rng.randrange(1,128)))
            try:doc=load(data)
            except ValueError:continue
            self.assertEqual(load(dump(doc)),doc)

class SemanticTests(unittest.TestCase):
    def inspect(self,name):
        c=build(name);r=check(c.context,c.seal,c.evidence);return c,r
    def test_all_directed_cases_against_independent_oracle(self):
        for name in IDS:
            with self.subTest(name=name):
                c,r=self.inspect(name);e=expected(c.world,c.context,c.seal,c.evidence)
                self.assertEqual(r['verdict'],e['verdict'])
                for k,v in e['formation_states'].items():self.assertEqual(r['formation.'+k],v)
    def test_nominal(self):self.assertEqual(self.inspect('E00')[1]['verdict'],'Conformant')
    def test_shadow(self):self.assertEqual(self.inspect('E03-S')[1]['formation.constraint'],'refuted')
    def test_broken_gate(self):
        c,r=self.inspect('E03-B');self.assertTrue(c.world.executed);self.assertEqual(r['formation.constraint'],'refuted')
    def test_path_not_audit_failure(self):
        c,r=self.inspect('E01');self.assertEqual(r['formation.path'],'refuted');self.assertEqual(r['audit'],'established')
    def test_authority_scope_not_label(self):
        c,r=self.inspect('E02-A');self.assertTrue(c.world.admission);self.assertEqual(r['formation.attribution'],'refuted');self.assertEqual(r['formation.constraint'],'supported')
    def test_source_not_authority(self):self.assertEqual(self.inspect('E02-S')[1]['query.source'],'refuted')
    def test_control_effect_binding(self):self.assertEqual(self.inspect('E02-E')[1]['query.effect'],'refuted')
    def test_five_audit_failures(self):
        for name,dim in [('E04-I','integrity'),('E04-N','independence'),('E04-S','scopecoverage'),('E04-P','preservation'),('E04-L','localization')]:
            with self.subTest(name=name):
                c,r=self.inspect(name);self.assertTrue(ground_truth(c.world)['form_conform']);self.assertEqual(r['verdict'],'Unadjudicable');self.assertEqual(r['audit.'+dim],'not_established')
    def test_preservation_keeps_world_constant(self):self.assertEqual(build('E00').world.events,build('E04-P').world.events)
    def test_absence_is_not_negative(self):
        _,r=self.inspect('E10');self.assertEqual(r['formation.constraint'],'not_adjudicated');self.assertEqual(r['verdict'],'Unadjudicable')
    def test_nonconformant_world_can_be_unknown(self):
        c,r=self.inspect('E11-BLIND-SHADOW');self.assertFalse(ground_truth(c.world)['constraint']);self.assertEqual(r['verdict'],'Unadjudicable')
    def test_countermodel_projection_exact(self):
        a,b=build('E00'),build('E03-S');self.assertEqual(dump(baseline(a.world)),dump(baseline(b.world)));self.assertEqual(a.context,b.context);self.assertNotEqual(a.evidence,b.evidence)
    def test_required_context_fields_cannot_be_omitted(self):
        required = ('system','version','instance','decision','admission','required_scope',
                    'collector','monitor','controller','boundary','threat_model')
        for key in required:
            c = build('E00')
            c.context.pop(key)
            c.evidence['context_digest'] = digest(c.context)
            c.seal['context_digest'] = digest(c.context)
            r = check(c.context, c.seal, c.evidence)
            self.assertEqual(r['verdict'], 'Unadjudicable', key)
            self.assertIn('Prerequisite', r['issues'], key)

    def test_no_self_serving_applicability(self):self.assertEqual(self.inspect('M1-APPLICABILITY')[1]['formation.constraint'],'refuted')
    def test_no_posthoc_contract(self):self.assertEqual(self.inspect('M2-CONTRACT')[1]['verdict'],'Unadjudicable')
    def test_no_cherry_picking(self):self.assertEqual(self.inspect('M2-CHERRY')[1]['verdict'],'Unadjudicable')
    def test_safe_refusal_not_failed_task(self):
        c,r=self.inspect('E12-DENY');self.assertFalse(c.world.executed);self.assertEqual(r['verdict'],'Conformant')
    def test_trusted_downstream_execution_witnesses(self):
        for label, base, changes in EXECUTION_WITNESSES:
            with self.subTest(label=label):
                case=executor_witness(base,changes)
                result=isolated_check(case.context,case.seal,case.evidence)
                truth=expected(case.world,case.context,case.seal,case.evidence)
                expected_path=(label=='allowed_but_not_executed')
                self.assertEqual(truth['formation_truth']['path'],expected_path)
                self.assertTrue(all(truth['audit_reality'].values()))
                self.assertEqual(result['audit'],'established')
                self.assertEqual(result['formation.path'],'supported' if expected_path else 'refuted')
                self.assertEqual(result['formation.constraint'],'supported')
                self.assertEqual(result['verdict'],truth['verdict'])
                self.assertEqual(result['verdict'],'Conformant' if expected_path else 'Non-conformant')
    def test_postseal_executor_tampering_is_unknown(self):
        case=build('E00')
        evidence=case.evidence.copy()
        evidence['execution.amount']='300000'
        report=isolated_check(case.context,case.seal,evidence)
        self.assertEqual(report['verdict'],'Unadjudicable')
        self.assertEqual(report['formation.path'],'not_adjudicated')

    def test_legitimate_applicability_change(self):
        c,r=self.inspect('E13-LOW-VALUE');self.assertNotIn('dual',c.world.applicable);self.assertEqual(r['verdict'],'Conformant')
    def test_ordinary_logs_cannot_replace_structure(self):
        c=build('E00');d={'schema':'isa-evidence-1','outcome':'paid'};self.assertEqual(check(c.context,c.seal,d)['verdict'],'Unadjudicable')
    def test_unknown_label_field_is_not_accepted(self):
        c=build('E00');c.evidence['expected_verdict']='Conformant';self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
    def test_every_required_evidence_deletion_abstains(self):
        c=build('E00')
        for key in c.evidence:
            d=c.evidence.copy();d.pop(key)
            self.assertEqual(check(c.context,c.seal,d)['verdict'],'Unadjudicable',key)
    def test_each_channel_tamper_detected(self):
        c=build('E00')
        for ch in CHANNELS:
            d=c.evidence.copy();key=next(iter(channel(d,ch)));d[key]='tampered'
            self.assertEqual(check(c.context,c.seal,d)['verdict'],'Unadjudicable',ch)
    def test_context_version_is_pinned(self):
        c=build('E00');c.context['version']='2';self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
    def test_contract_must_predate_run(self):
        c=build('E00');c.context['declared_tick']='11';self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
    def test_frozen_scope_not_log_driven(self):
        c=build('E00');c.context['requires.control']='lineage';self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
    def test_consulted_but_irrelevant_is_not_control(self):
        s=Spec();s.code += ['T','O:4,5'];s.root=6;c=context(s);collector=Collector(c);w=run(s,c,collector.observe);d,seal=collector.finish()
        self.assertEqual(w.reads,set(KINDS));self.assertEqual(check(c,seal,d)['formation.constraint'],'refuted')
    def test_all_sixteen_evaluation_vectors(self):
        for mask in range(16):
            s=Spec();s.values={k:bool(mask&(1<<i)) for i,k in enumerate(KINDS)};c=context(s);co=Collector(c);w=run(s,c,co.observe);d,se=co.finish()
            self.assertEqual(w.executed,mask==15);self.assertEqual(check(c,se,d)['verdict'],'Conformant')
    def test_independent_interpreters_agree_on_dag_family(self):
        for root in ('A:0,1,2,3','O:0,1,2,3','T','F','A:0,1','O:2,3'):
            for mask in range(16):
                s=Spec();s.code[4]=root;s.values={k:bool(mask&(1<<i)) for i,k in enumerate(KINDS)};d={'program.root':'4','program.count':'5',**{'program.'+str(i):op for i,op in enumerate(s.code)}}
                self.assertEqual(evaluate(s.code,4,s.values),circuit(d,s.values))
    def test_cyclic_program_fails_without_recursion(self):
        c=build('E00');c.evidence['program.0']='A:4';self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
    def test_undeclared_extra_program_nodes_rejected(self):
        c=build('E00');c.evidence['program.31']='T';self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
    def test_two_authorizations_need_two_subjects(self):
        s=Spec();s.authority_subjects=('H1','H1');c=context(s);co=Collector(c);run(s,c,co.observe);d,se=co.finish();self.assertEqual(check(c,se,d)['formation.attribution'],'refuted')
    def test_later_input_mutation_cannot_rewrite_world(self):
        s=Spec();c=context(s);co=Collector(c);w=run(s,c,co.observe);before=ground_truth(w)
        s.code[4]="T";s.bound_source="changed-later"
        self.assertEqual(before,ground_truth(w))
    def test_collector_cannot_read_expected_result(self):
        text=(ROOT/'research/reference/evidence.py').read_text();tree=ast.parse(text)
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertNotIn('oracle',imports);self.assertNotIn('scenarios',imports)
    def test_compromised_trusted_root_is_a_recorded_limit(self):
        # Forge both data and the separately trusted checkpoints. This is OUTSIDE Θ_A.
        good=build('E00');bad=build('E03-S')
        r=check(good.context,good.seal,good.evidence)
        self.assertEqual(r['verdict'],'Conformant');self.assertFalse(ground_truth(bad.world)['form_conform'])
        # Identical checker input cannot distinguish a different invisible actual world.
        forged_reality=expected(bad.world,good.context,good.seal,good.evidence)
        self.assertFalse(forged_reality['audit_reality']['preservation'])

class IsolationTests(unittest.TestCase):
    def test_actual_checker_process(self):
        c=build('E00');self.assertEqual(isolated_check(c.context,c.seal,c.evidence)['verdict'],'Conformant')
    def test_all_cases_through_process(self):
        for name in IDS:
            c=build(name);r=isolated_check(c.context,c.seal,c.evidence);e=expected(c.world,c.context,c.seal,c.evidence);self.assertEqual(r['verdict'],e['verdict'],name)
    def test_hidden_label_changes_no_runtime_bytes(self):
        c=build('E03-S');before=isolated_check(c.context,c.seal,c.evidence)
        hidden={'fault':'Nominal','expected':'Conformant','truth':'anything'}
        hidden.update(fault='banana',expected='Unadjudicable')
        after=isolated_check(c.context,c.seal,c.evidence);self.assertEqual(before,after)
    def test_parent_environment_cannot_inject_answer(self):
        c=build('E10');old=os.environ.get('ISA_EXPECTED')
        try:os.environ['ISA_EXPECTED']='Conformant';self.assertEqual(isolated_check(c.context,c.seal,c.evidence)['verdict'],'Unadjudicable')
        finally:
            if old is None:os.environ.pop('ISA_EXPECTED',None)
            else:os.environ['ISA_EXPECTED']=old
    def test_alpha_renamed_instances_work(self):
        for name in ('u-new','case-871','not-a-training-case'):
            s=Spec();s.execution_instance=name;s.execution_decision='new-d';s.execution_admission='new-a'
            c=context(s);c.update(instance=name,decision='new-d',admission='new-a',version='independent-version')
            co=Collector(c);run(s,c,co.observe);d,se=co.finish();self.assertEqual(isolated_check(c,se,d)['verdict'],'Conformant')
    def test_checker_import_boundary(self):
        tree=ast.parse((ROOT/'research/reference/checker.py').read_text())
        imported=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertTrue(set(imported).issubset({'__future__','pathlib','wire'}))
    def test_rust_dependency_boundary(self):
        for path in (ROOT/'runtime').glob('*/Cargo.toml'):
            d=tomllib.loads(path.read_text())
            for name,dep in d.get('dependencies',{}).items():
                self.assertNotIn('research',str(dep));self.assertNotIn('oracle',name);self.assertNotIn('scenarios',name)
        d=tomllib.loads((ROOT/'runtime/isa-checker/Cargo.toml').read_text())
        self.assertEqual(set(d.get('dependencies',{})),{'isa-core'})
    def test_no_runtime_import_of_hidden_research(self):
        for path in (ROOT/'runtime').rglob('*.rs'):
            text=path.read_text();self.assertNotRegex(text,r'\b(?:use|extern\s+crate)\s+isa_(?:oracle|scenarios|harness)')
            self.assertNotIn('include_str!',text);self.assertNotIn('include_bytes!',text)

class SystemTests(unittest.TestCase):
    @staticmethod
    def public(s):
        d={'schema':'isa-system-1','root':s['root'],'actual':','.join(sorted(s['actual_channels'])),
           'governed':','.join(sorted(s['governed_channels'])),'edges':','.join(a+'>'+b for a,b in s['edges']),
           'gates':','.join(s['gate_tables'])}
        for k,v in s['gate_tables'].items():d['gate.'+k+'.outputs']=','.join(str(int(x)) for x in v)
        return d
    def test_all_system_graphs_against_separate_algorithm(self):
        for name in IDS:
            s=build(name).system;r=system_check(self.public(s));truth=system_truth(s)
            self.assertEqual(r['coverage'],str(int(truth['coverage'])));self.assertEqual(r['mediation'],str(int(truth['mediation'])))
    def test_public_system_json_is_checker_report_not_oracle_truth(self):
        for name in IDS:
            with self.subTest(name=name):
                root=ROOT/'results/reference'
                public=root/'cases'/name
                report=json.loads((public/'system-report.json').read_text())
                self.assertEqual(report,load((public/'system-report.isa').read_bytes()))
                truth=json.loads((root/'research-only'/name/'system-truth.json').read_text())
                self.assertEqual(truth,system_truth(build(name).system))
                self.assertEqual({k:report[k]=='1' for k in ('coverage','mediation')},truth)
                self.assertEqual(report['scope'],'declared-finite-graph')

    def test_instance_conformance_does_not_imply_coverage(self):
        c=build('E07');self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Conformant');self.assertFalse(system_truth(c.system)['coverage'])
    def test_instance_conformance_does_not_imply_mediation(self):
        c=build('E08');self.assertEqual(check(c.context,c.seal,c.evidence)['verdict'],'Conformant');self.assertFalse(system_truth(c.system)['mediation'])
    def test_bypass_not_shadow(self):
        bypass=build('E09');shadow=build('E03-S');self.assertTrue(ground_truth(bypass.world)['constraint']);self.assertFalse(ground_truth(bypass.world)['path']);self.assertFalse(ground_truth(shadow.world)['constraint'])
    def test_current_bypass_endpoint_exists_in_system_graph(self):
        c = build('E09')
        endpoint = c.world.ledger['channel']
        self.assertIn(('candidate', 'executor-'+endpoint), c.system['edges'])
        self.assertFalse(system_truth(c.system)['mediation'])

    def test_unknown_exit_is_not_certified_by_empty_graph(self):
        d=self.public(build('E00').system);d['edges']='candidate>gate'
        with self.assertRaises(ValueError):system_check(d)

if __name__=='__main__':unittest.main(verbosity=2)
