//! Research-only semantic oracle. No checker dependency and no expected-label lookup.
#![forbid(unsafe_code)] use std::collections::{
    BTreeMap,
    BTreeSet
};
use isa_core::{
    Doc,
    Op,
    Program,
    CHANNELS,
    QUERIES,
    requires,
    channel,
    get,
    split,
    fingerprint
};
use isa_engine::Run;
#[derive(Clone, Debug)]pub struct Truth{
    pub path:bool,
    pub attribution:bool,
    pub constraint:bool
}
impl Truth{
    pub fn conforms(&self)->bool{
        self.path&&self.attribution&&self.constraint
    }
}
fn value(p:&Program, i:usize, v:&BTreeMap<String, bool>)->bool{
    match &p.code[i]{
        Op::Constant(x)=>*x,
        Op::Input(k)=>v[k],
        Op::All(js)=>!js.iter().any(|j|!value(p, *j, v)),
        Op::Any(js)=>js.iter().any(|j|value(p, *j, v))
    }
}
pub fn truth(w:&Run)->Truth{
    let s=&w.spec;
    let c=&w.context;
    // Ground truth uses the actual downstream execution record, not the checker.
    let effect_match=match get(&w.ledger, "status"){
        "paid"=>w.admission&&get(&w.ledger, "amount")==s.amount.to_string(),
        "refused"=>get(&w.ledger, "amount")=="0",
        _=>false,
    };
    let p=s.execution_instance==get(c, "instance")&&s.execution_decision==get(c, "decision")&&s.execution_admission==get(c, "admission")&&s.route!="direct"
        &&s.amount.to_string()==get(c, "amount")
        &&get(&w.ledger, "instance")==get(c, "instance")
        &&get(&w.ledger, "decision")==get(c, "decision")
        &&get(&w.ledger, "admission")==get(c, "admission")&&effect_match;
    let mut a=s.bound_source==s.actual_source&&!s.actual_source.is_empty()&&!s.authority_subjects[0].is_empty()&&s.authority_scopes[0]==get(c, "required_scope");
    if w.applicable.iter().any(|x|x=="dual"){
        a=a&&s.authority_scopes[1]==get(c, "required_scope")&&!s.authority_subjects[1].is_empty()&&s.authority_subjects[0]!=s.authority_subjects[1];
    }
    a&=s.bound_controller==get(c, "controller");
    let selected=s.include_applicable.as_ref().unwrap_or(&w.applicable);
    let mut con=selected==&w.applicable;
    let n=w.applicable.len();
    let mut table=Vec::new();
    for mask in 0..(1usize<<n){
        let mut v=s.values.clone();
        for(i, k)in w.applicable.iter().enumerate(){
            v.insert(k.clone(), mask&(1<<i)!=0);
        }
        let actual=value(&s.program, s.program.root, &v);
        table.push(actual);
        con&=actual==(mask==(1<<n)-1);
    }
    con&=(0..n).all(|i|(0..table.len()).any(|b|table[b]!=table[b^(1<<i)]));
    con&=w.applicable.iter().all(|k|w.reads.contains(k));
    con&=w.admission==value(&s.program, s.program.root, &s.values);
    Truth{
        path:p,
        attribution:a,
        constraint:con
    }
}
pub fn audit_reality(w:&Run, c:&Doc, seal:&Doc, d:&Doc)->BTreeMap<String, bool>{
    let raw=w.events.iter().flat_map(|(_, f)|f.iter().map(|(k, v)|(k.clone(), v.clone()))).collect::<Doc>();
    let pre=c==&w.context&&fingerprint(c)==get(d, "context_digest")&&get(d, "context_digest")==get(seal, "context_digest") &&get(c, "declared_tick").parse::<u64>().ok().zip(get(c, "start_tick").parse::<u64>().ok()).map(|(a, b)|a<b).unwrap_or(false) &&get(d, "start_tick")==get(seal, "start_tick")&&get(d, "start_tick")==get(c, "start_tick")&&get(d, "finish_tick")==get(seal, "finish_tick");
    let integrity=CHANNELS.iter().all(|k|fingerprint(&channel(d, k))==get(seal, &format!("digest.{k}")));
    let independent=!CHANNELS.iter().all(|k|split(get(c, &format!("writers.{k}"))).contains(&get(c, "controller")));
    let mut covered=split(get(c, "queries")).into_iter().collect::<BTreeSet<_>>()==QUERIES.into_iter().collect::<BTreeSet<_>>() &&split(get(c, "channels")).into_iter().collect::<BTreeSet<_>>()==CHANNELS.into_iter().collect::<BTreeSet<_>>();
    covered&=QUERIES.iter().all(|q|requires(q).iter().all(|r|split(get(c, &format!("requires.{q}"))).contains(r)));
    covered&=raw.keys().filter(|k|!k.starts_with("lineage.")).all(|k|d.contains_key(k));
    let preserved=CHANNELS.iter().filter(|k|**k!="lineage").all(|k|channel(d, k)==channel(&raw, k));
    let localized=QUERIES.iter().all(|q|requires(q).iter().all(|r|split(get(d, &format!("lineage.{q}"))).contains(r)));
    BTreeMap::from([("prerequisite".into(), pre), ("integrity".into(), integrity), ("independence".into(), independent), ("scopecoverage".into(), covered), ("preservation".into(), preserved), ("localization".into(), localized)])
}
pub fn expected(w:&Run, c:&Doc, seal:&Doc, d:&Doc)->Doc{
    let t=truth(w);
    let audit=audit_reality(w, c, seal, d);
    let valid=audit.values().all(|v|*v);
    let mut out=Doc::from([("verdict".into(), if !valid{
        "Unadjudicable"
    }
    else if t.conforms(){
        "Conformant"
    }
    else{
        "Non-conformant"
    }.into())]);
    for(k, v)in[("path", t.path), ("attribution", t.attribution), ("constraint", t.constraint)]{
        out.insert(format!("truth.{k}"), u8::from(v).to_string());
        out.insert(format!("formation.{k}"), if !valid{
            "not_adjudicated"
        }
        else if v{
            "supported"
        }
        else{
            "refuted"
        }.into());
    }
    for(k, v)in audit{
        out.insert(format!("truth.audit.{k}"), u8::from(v).to_string());
    }
    out
}
