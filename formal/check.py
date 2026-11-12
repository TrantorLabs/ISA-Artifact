"""Three bounded formal views, eight FQ groups, and negative controls.
The solver searches relations; Path/Attr/Const/Audit are derived expressions.
"""
from __future__ import annotations
import argparse
from itertools import product
import json
from pathlib import Path
from solver import Z3

ROOT=Path(__file__).resolve().parents[1]
def AND(*x): return 'true' if not x else '(and '+' '.join(x)+')'
def OR(*x): return 'false' if not x else '(or '+' '.join(x)+')'
def NOT(x): return '(not '+x+')'
def EQ(a,b): return '(= '+a+' '+b+')'
def ITE(a,b,c): return '(ite '+a+' '+b+' '+c+')'
def atom(x): return str(x).lower() if isinstance(x,bool) else str(x)

class Model:
    def __init__(self):self.lines=['(set-logic QF_LIA)'];self.domains={}
    def integer(self,n,lo,hi):
        self.domains[n]=(lo,hi);self.lines += [f'(declare-const {n} Int)',f'(assert (and (<= {lo} {n}) (<= {n} {hi})))'];return n
    def boolean(self,n):
        self.domains[n]=(False,True);self.lines += [f'(declare-const {n} Bool)'];return n
    def define(self,n,expr,sort='Bool'):
        self.lines.append(f'(define-fun {n} () {sort} {expr})');return n
    def require(self,*terms):self.lines.extend('(assert '+t+')' for t in terms)
    def script(self):return '\n'.join(self.lines)+'\n'

# Finite controller grammar: Input0, Input1, And(Input0,Input1), Or(...), ConstantTrue.
# A controller node is executable structure. It is NOT a conformance label.
def gate(root,x,y):
    return ITE(EQ(root,'0'),x,ITE(EQ(root,'1'),y,ITE(EQ(root,'2'),AND(x,y),ITE(EQ(root,'3'),OR(x,y),'true'))))

FIELDS=('decision_instance','execution_instance','decision_link','admission_link','source_actual','source_bound','authority_scope','controller_actual','controller_bound','root')
def world(m,p):
    w={k:m.integer(p+k,0,4 if k=='root' else 1) for k in FIELDS}
    path=AND(*(EQ(w[k],'0') for k in ('decision_instance','execution_instance','decision_link','admission_link')))
    src=EQ(w['source_actual'],w['source_bound']);auth=EQ(w['authority_scope'],'0');eff=EQ(w['controller_actual'],w['controller_bound'])
    rows=[gate(w['root'],atom(x),atom(y)) for x,y in product((False,True),repeat=2)]
    controls=AND(OR(NOT(EQ(rows[0],rows[2])),NOT(EQ(rows[1],rows[3]))),OR(NOT(EQ(rows[0],rows[1])),NOT(EQ(rows[2],rows[3]))))
    eligibility=AND(NOT(rows[0]),NOT(rows[1]),NOT(rows[2]),rows[3])
    w['queries']=[path,src,auth,eff,controls,eligibility]
    w['path']=m.define(p+'path',path);w['attr']=m.define(p+'attr',AND(src,auth,eff));w['const']=m.define(p+'const',AND(controls,eligibility))
    w['form']=m.define(p+'form',AND(w['path'],w['attr'],w['const']));w['outcome']=rows[3]
    return w

def pair(m):return world(m,'a_'),world(m,'b_')
def different(a,b,target='form'):return NOT(EQ(a[target],b[target]))
def equal_observation(a,b,enriched=False,program_only=False):
    terms=[EQ(a['outcome'],b['outcome'])]
    if enriched:terms += [EQ(a[k],b[k]) for k in FIELDS]
    elif program_only:terms.append(EQ(a['root'],b['root']))
    return AND(*terms)
def constructor(w):
    # A concrete finite constructor binds identities/roles and emits an AND node.
    return AND(*(EQ(w[k],'0') for k in ('decision_instance','execution_instance','decision_link','admission_link','authority_scope')),
               EQ(w['source_actual'],w['source_bound']),EQ(w['controller_actual'],w['controller_bound']),EQ(w['root'],'2'))

def evidence(m,w,p='e_',mutant=False,forge_monitor=False):
    e={k:m.integer(p+k,0,4 if k=='root' else 1) for k in FIELDS}
    # Derive evidence propositions independently from actual relation fields.
    ep=AND(*(EQ(e[k],'0') for k in ('decision_instance','execution_instance','decision_link','admission_link')))
    es=EQ(e['source_actual'],e['source_bound']);ea=EQ(e['authority_scope'],'0');ee=EQ(e['controller_actual'],e['controller_bound'])
    er=[gate(e['root'],atom(x),atom(y)) for x,y in product((False,True),repeat=2)]
    ec=AND(OR(NOT(EQ(er[0],er[2])),NOT(EQ(er[1],er[3]))),OR(NOT(EQ(er[0],er[1])),NOT(EQ(er[2],er[3]))))
    el=AND(NOT(er[0]),NOT(er[1]),NOT(er[2]),er[3]);qs=[ep,es,ea,ee,ec,el]
    # Raw evidence availability, contract correspondence and producer/lineage relations.
    present=[m.integer(p+'present_'+str(i),0,1) for i in range(6)]
    requested=[m.integer(p+'requested_'+str(i),0,1) for i in range(6)]
    lineage=[m.integer(p+'lineage_'+str(i),-1,5) for i in range(6)]
    writer0=m.integer(p+'writer0',0,1);writer1=m.integer(p+'writer1',0,1)
    producer=m.integer(p+'producer',0,1);sealproducer=m.integer(p+'seal_producer',0,1)
    integrity=EQ(producer,sealproducer);independent=NOT(AND(EQ(writer0,'1'),EQ(writer1,'1')))
    covered=AND(*(EQ(x,'1') for x in present+requested));localized=AND(*(EQ(x,str(i)) for i,x in enumerate(lineage)))
    preserved=AND(*(EQ(x,y) for x,y in zip(qs,w['queries'])))
    actual_audit=m.define(p+'audit_truth',AND(integrity,independent,covered,localized,preserved))
    # Protected monitor commitment is modeled by injective equality over the finite
    # field tuple. The checker compares commitments, never calls actual_audit.
    monitor_matches=AND(*(EQ(e[k],w[k]) for k in FIELDS))
    assurance='true' if forge_monitor else monitor_matches
    established=m.define(p+'audit_established',AND(integrity,independent,localized,assurance,'true' if mutant else covered))
    reported_form=AND(*qs)
    report=m.define(p+'reported_verdict',ITE(established,ITE(reported_form,'1','0'),'-1'),'Int')
    return {'audit':actual_audit,'established':established,'verdict':report,'report_form':reported_form,'present':present,'queries':qs}

def build_queries():
    result=[]
    def add(identifier,m,expected,meaning,scope,assumptions):
        result.append((identifier,m,expected,meaning,scope,assumptions))
    m=Model();a,b=pair(m);m.require(a['path'],a['attr'],b['path'],b['attr'],equal_observation(a,b),different(a,b),*(EQ(a[k],b[k]) for k in FIELDS if k!='root'))
    add('FQ1',m,'SAT','Same ordinary observation, distinct actual control/formation.','2 instances/worlds; 2 evaluations; 5 controller expressions','Path and attribution held valid to isolate control, all-pass canonical observation.')
    m=Model();a,b=pair(m);m.require(equal_observation(a,b,enriched=True),different(a,b))
    add('FQ2',m,'UNSAT','Complete protected structural observation resolves the finite target.','All finite relation fields of two worlds','Faithful, complete monitor projection; not a universal deployment claim.')
    m=Model();a,b=pair(m);m.require(equal_observation(a,b,program_only=True),different(a,b))
    add('FQ2-WEAK',m,'SAT','Program evidence alone does not establish Path and Attribution.','Same finite class as FQ2','Deliberately insufficient bridge; remaining structural dimensions are free.')
    m=Model();a,b=pair(m);m.require(constructor(a),constructor(b),equal_observation(a,b),different(a,b))
    add('FQ3',m,'UNSAT','A concrete bound-and-AND constructor removes the finite ambiguity.','Finite constructor class','Constructor constraints are on relation allocation and instructions, not FormConform labels.')
    m=Model();a=world(m,'a_');m.require(constructor(a),a['outcome'])
    add('FQ3-NONVACUOUS',m,'SAT','Constructor admits real normal execution.','One constructor world','All-pass observation.')
    m=Model();a=world(m,'a_');m.require(constructor(a),NOT(gate(a['root'],'false','true')))
    add('FQ3-DENIAL',m,'SAT','Constructor also rejects a forbidden evaluation vector.','One constructor world','Same policy; input intervention only.')
    for q in ('path','attr','const','audit'):
        m=Model();w=world(m,'w_');e=evidence(m,w);preds={k:w[k] for k in ('path','attr','const')};preds['audit']=e['audit']
        m.require(*(NOT(v) if k==q else v for k,v in preds.items()))
        add('FQ4-'+q.upper(),m,'SAT','Search a 3+1 deletion witness from actual relations.','One world, six query/evidence relations','No free Path/Attr/Const/Audit inputs.')
    for mutate in (False,True):
        m=Model();w=world(m,'w_');e=evidence(m,w,mutant=mutate)
        m.require(NOT(e['audit']),NOT(EQ(e['verdict'],'-1')))
        add('FQ5-MUTANT' if mutate else 'FQ5',m,'SAT' if mutate else 'UNSAT','Detect false certainty in a separate evidence-only algorithm.','Finite world plus monitor/evidence relations','Mutation ignores required evidence; protected root remains fixed.')
    m=Model();w=world(m,'w_');e=evidence(m,w,forge_monitor=True)
    m.require(e['established'],NOT(e['audit']))
    add('FQ5-TRUST-BREACH',m,'SAT','A compromised trusted monitor can create undetectable false certainty.','Outside the protected-root assumption','This is a recorded limitation, not a claimed in-scope defence.')
    for mutate in (False,True):
        m=Model();w=world(m,'w_');e=evidence(m,w)
        missing=EQ(e['present'][4],'0')
        status=ITE(missing,'0',ITE(e['queries'][4],'1','0')) if mutate else ITE(AND(e['established'],NOT(missing)),ITE(e['queries'][4],'1','0'),'-1')
        m.require(missing,EQ(status,'0'))
        add('FQ6-MUTANT' if mutate else 'FQ6',m,'SAT' if mutate else 'UNSAT','Do not report absent control evidence as a negative formation fact.','One scoped query in the finite model','Mutant maps missing evidence to false; reference abstains.')
    for q in ('FQ7','FQ8'):
        m=Model();w=world(m,'w_');e=evidence(m,w)
        batch_actual=m.integer('batch_channel_actual',0,1);batch_governed=m.integer('batch_channel_governed',0,1)
        direct=m.integer('candidate_to_batch_executor_edge',0,1)
        coverage=OR(EQ(batch_actual,'0'),EQ(batch_governed,'1'))
        mediation=NOT(AND(EQ(batch_governed,'1'),EQ(direct,'1')))
        m.require(w['form'],e['audit'],EQ(batch_actual,'1'))
        if q=='FQ7':m.require(NOT(coverage))
        else:m.require(coverage,NOT(mediation))
        add(q,m,'SAT','Current conformant instance does not prove the whole system property.','Standard plus batch channel, one additional direct path','System channel/path relations are separate from the standard instance.')
    return result

def exhaustive_projection():
    # Independent finite enumeration, separate from both SMT construction and checker.
    def output(op,x,y):
        return (x,y,x and y,x or y,True)[op]
    rows=[]
    # Vary concrete identity / binding relations, not free conformance truth flags.
    for di,ei,link,adlink,actualsrc,boundsrc,scope,ctrl,bctrl,root in product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(5)):
        path=di==ei==link==adlink==0;attr=actualsrc==boundsrc and scope==0 and ctrl==bctrl
        tab=tuple(output(root,x,y) for x,y in product((False,True),repeat=2))
        control=any(tab[i]!=tab[i^2] for i in range(4)) and any(tab[i]!=tab[i^1] for i in range(4))
        con=control and tab==(False,False,False,True)
        fields=(di,ei,link,adlink,actualsrc,boundsrc,scope,ctrl,bctrl,root)
        rows.append((fields,path,attr,con,path and attr and con,tab[-1]))
    groups={}
    for fields,p,a,c,f,o in rows:
        if p and a:groups.setdefault(o,{}).setdefault(f,fields)
    collisions=[{'observation_allow':o,'positive':v[True],'negative':v[False]} for o,v in groups.items() if len(v)==2]
    assert collisions
    return {'world_count':len(rows),'fq1_collision_classes':len(collisions),'canonical_witness':collisions[0],
            'finite_profile':'9 binary binding fields and one five-expression controller',
            'all_form_true_worlds':sum(r[4] for r in rows)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'results/formal');a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    smtdir=ROOT/'formal/smt2';smtdir.mkdir(exist_ok=True);z=Z3();results=[]
    for name,m,expect,meaning,scope,assumptions in build_queries():
        script=m.script();(smtdir/(name+'.smt2')).write_text('; '+meaning+'\n'+script+'(check-sat)\n')
        got=z.solve(script)
        (a.out/(name+'.txt')).write_text(got['status']+'\n'+got['model']+'\n'+got['reason'])
        if got['status']!=expect:raise AssertionError((name,expect,got))
        results.append({'id':name,'status':got['status'],'expected':expect,'matched':True,'meaning':meaning,'scope':scope,'assumptions':assumptions,'solver':z.version})
    enumeration=exhaustive_projection()
    (a.out/'queries.json').write_text(json.dumps(results,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    (a.out/'enumeration.json').write_text(json.dumps(enumeration,indent=2,sort_keys=True)+'\n')
    (a.out/'summary.json').write_text(json.dumps({'solver':'Z3 '+z.version,'groups':8,'queries':len(results),'matched':len(results),'enumerated_worlds':enumeration['world_count'],'scope':'bounded finite relational instances only'},indent=2)+'\n')
    print(json.dumps({'solver':z.version,'queries':len(results),'matched':len(results),'worlds':enumeration['world_count']}))
if __name__=='__main__':main()
