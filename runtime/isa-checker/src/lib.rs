//! Independent evidence-only adjudicator. Does not link engine, research or oracle.
#![forbid(unsafe_code)] pub mod system;
use std::collections::{
    BTreeMap,
    BTreeSet
};
use isa_core::{
    Doc,
    Op,
    CHANNELS,
    KINDS,
    QUERIES,
    requires,
    get,
    split,
    channel,
    fingerprint,
    uint,
    bit,
    applicable
};
fn fields(name:&str)->&'static[&'static str]{
    match name{
        "decision"=>&["instance", "id", "amount", "candidate"],
        "source"=>&["instance", "actual", "bound"],
        "authority"=>&["instance", "h1", "h2", "scope1", "scope2"],
        "effect"=>&["instance", "actual_controller", "bound_controller"],
        "evaluation"=>&["instance", "applicable", "recipient", "transaction", "dual", "channel"],
        "admission"=>&["instance", "id", "decision", "state", "reads", "controller"],
        "execution"=>&["instance", "decision", "admission", "status", "amount", "channel", "route"],
        "lineage"=>&QUERIES,
        _=>&[],
    }
}
fn set(s:&str)->BTreeSet<&str>{
    split(s).into_iter().collect()
}
/// Independent bottom-up interpreter. The engine uses a separate recursive evaluator.
fn circuit(d:&Doc, values:&BTreeMap<String, bool>)->Result<(bool, BTreeSet<String>), String>{
    let n=uint(get(d, "program.count"), 32)? as usize;
    let root=uint(get(d, "program.root"), 31)? as usize;
    if n==0||root>=n{
        return Err("invalid program cardinality/root".into());
    }
    let mut answers=Vec::<bool>::new();
    let mut supports=Vec::<BTreeSet<String>>::new();
    for i in 0..n{
        let op=Op::parse(get(d, &format!("program.{i}")))?;
        let mut deps=BTreeSet::new();
        let answer=match op{
            Op::Constant(v)=>v,
            Op::Input(k)=>{
                deps.insert(k.clone());
                *values.get(&k).ok_or("missing evaluator value")?
            },
            Op::All(js)=>{
                if js.iter().any(|j|*j>=i){
                    return Err("cyclic program".into());
                }
                for j in &js{
                    deps.extend(supports[*j].clone());
                }
                js.iter().all(|j|answers[*j])
            },
            Op::Any(js)=>{
                if js.iter().any(|j|*j>=i){
                    return Err("cyclic program".into());
                }
                for j in &js{
                    deps.extend(supports[*j].clone());
                }
                js.iter().any(|j|answers[*j])
            },
        };
        answers.push(answer);
        supports.push(deps);
    }
    Ok((answers[root], supports[root].clone()))
}
fn values(d:&Doc)->Result<BTreeMap<String, bool>, String>{
    KINDS.iter().map(|k|bit(get(d, &format!("evaluation.{k}"))).map(|b|(k.to_string(), b))).collect()
}
fn execution_binding(c:&Doc, d:&Doc)->bool{
    if get(d,"decision.amount")!=get(c,"amount"){
        return false;
    }
    match get(d,"execution.status"){
        "paid"=>get(d,"admission.state")=="allow"&&get(d,"execution.amount")==get(d,"decision.amount"),
        "refused"=>get(d,"execution.amount")=="0",
        _=>false,
    }
}
fn query_values(c:&Doc, d:&Doc)->Result<BTreeMap<String, bool>, String>{
    let u=get(c, "instance");
    let app=applicable(uint(get(c, "amount"), 1_000_000_000)?, uint(get(c, "dual_threshold"), 1_000_000_000)?);
    let values=values(d)?;
    let(now, reads)=circuit(d, &values)?;
    let path=["decision", "source", "authority", "effect", "evaluation", "admission", "execution"].iter().all(|p|get(d, &format!("{p}.instance"))==u) &&get(d, "decision.id")==get(c, "decision")&&get(d, "admission.decision")==get(c, "decision")&&get(d, "execution.decision")==get(c, "decision") &&get(d, "admission.id")==get(c, "admission")&&get(d, "execution.admission")==get(c, "admission") &&!get(d, "decision.candidate").is_empty()&&get(d, "execution.route")=="standard"&&execution_binding(c,d);
    let source=get(d, "source.instance")==u&&!get(d, "source.actual").is_empty()&&get(d, "source.actual")==get(d, "source.bound");
    let mut authority=get(d, "authority.instance")==u&&!get(d, "authority.h1").is_empty()&&get(d, "authority.scope1")==get(c, "required_scope");
    if app.iter().any(|k|k=="dual"){
        authority=authority&&!get(d, "authority.h2").is_empty()&&get(d, "authority.h1")!=get(d, "authority.h2")&&get(d, "authority.scope2")==get(c, "required_scope");
    }
    let effect=get(d, "effect.instance")==u&&!get(d, "effect.actual_controller").is_empty() &&get(d, "effect.bound_controller")==get(d, "effect.actual_controller")&&get(d, "effect.actual_controller")==get(d, "admission.controller");
    let mut rows=Vec::new();
    for bits in 0..(1usize<<app.len()){
        let mut alternate=values.clone();
        for(i, k)in app.iter().enumerate(){
            alternate.insert(k.clone(), bits&(1<<i)!=0);
        }
        rows.push(circuit(d, &alternate)?.0);
    }
    let influence=(0..app.len()).all(|i|(0..rows.len()).any(|b|rows[b]!=rows[b^(1<<i)]));
    let read_refs=reads.iter().map(String::as_str).collect::<BTreeSet<_>>();
    let control=get(d, "evaluation.instance")==u&&split(get(d, "evaluation.applicable"))==app.iter().map(String::as_str).collect::<Vec<_>>() &&app.iter().all(|k|reads.contains(k))&&set(get(d, "admission.reads"))==read_refs&&influence;
    let eligibility=rows.iter().enumerate().all(|(b, v)|*v==(b==rows.len()-1))&&get(d, "admission.state")==if now{
        "allow"
    }
    else{
        "deny"
    };
    Ok(BTreeMap::from([("path".into(), path), ("source".into(), source), ("authority".into(), authority), ("effect".into(), effect), ("control".into(), control), ("eligibility".into(), eligibility)]))
}
pub fn check(c:&Doc, seal:&Doc, d:&Doc)->Doc{
    let mut issues=BTreeSet::<String>::new();
    let mut dims=BTreeMap::from([("Integrity", true), ("Independence", true), ("ScopeCoverage", true), ("Preservation", true), ("Localization", true)]);
    let prereq_numbers=(||->Result<bool, String>{
        Ok(uint(get(c, "declared_tick"), 1_000_000_000)?<uint(get(c, "start_tick"), 1_000_000_000)? &&uint(get(d, "finish_tick"), 1_000_000_000)?>=uint(get(d, "start_tick"), 1_000_000_000)?)
    })();
    let mut pre=get(c, "schema")=="isa-context-1"&&get(seal, "schema")=="isa-collector-seal-1"&&get(d, "schema")=="isa-evidence-1" &&get(c, "gamma")==KINDS.join(",")&&fingerprint(c)==get(d, "context_digest")&&get(d, "context_digest")==get(seal, "context_digest") &&prereq_numbers.unwrap_or(false)&&get(c, "start_tick")==get(d, "start_tick")&&get(d, "start_tick")==get(seal, "start_tick") &&get(d, "finish_tick")==get(seal, "finish_tick")&&get(c, "collector")==get(seal, "collector")&&get(c, "monitor")==get(seal, "monitor") &&["system", "version", "instance", "decision", "admission", "required_scope", "collector", "monitor", "controller", "boundary", "threat_model"].iter().all(|k|!get(c,k).is_empty());
    if !pre{
        issues.insert("Prerequisite".into());
    }
    let mut allowed=BTreeSet::<String>::from(["schema".into(), "context_digest".into(), "start_tick".into(), "finish_tick".into(), "program.root".into(), "program.count".into()]);
    for name in CHANNELS{
        for f in fields(name){
            allowed.insert(format!("{name}.{f}"));
        }
    }
    for i in 0..32{
        allowed.insert(format!("program.{i}"));
    }
    if d.keys().any(|k|!allowed.contains(k)){
        pre=false;
        issues.insert("UnknownField".into());
    }
    dims.insert("Integrity", CHANNELS.iter().all(|name|get(seal, &format!("digest.{name}"))==fingerprint(&channel(d, name))));
    let declared=set(get(c, "channels"));
    dims.insert("Independence", !declared.is_empty()&&!declared.iter().all(|name|split(get(c, &format!("writers.{name}"))).contains(&get(c, "controller"))));
    let mut coverage=set(get(c, "queries"))==QUERIES.into_iter().collect::<BTreeSet<_>>()&&declared==CHANNELS.into_iter().collect::<BTreeSet<_>>();
    for q in QUERIES{
        let req=set(get(c, &format!("requires.{q}")));
        coverage&=requires(q).iter().all(|r|req.contains(r));
    }
    for name in CHANNELS{
        if name!="lineage"&&name!="program"{
            coverage&=fields(name).iter().all(|f|d.contains_key(&format!("{name}.{f}")));
        }
    }
    match uint(get(d, "program.count"), 32){
        Ok(n)=>{
            let mut expected=BTreeSet::from(["program.root".to_string(), "program.count".to_string()]);
            for i in 0..n{
                expected.insert(format!("program.{i}"));
            }
            coverage&=n>0&&channel(d, "program").keys().cloned().collect::<BTreeSet<_>>()==expected;
        },
        Err(_)=>coverage=false,
    }
    dims.insert("ScopeCoverage", coverage);
    let mut preservation=fingerprint(&channel(d, "program"))==get(seal, "registered_program_digest") &&CHANNELS.iter().filter(|n|**n!="lineage").all(|name|fingerprint(&channel(d, name))==get(seal, &format!("monitor_digest.{name}")));
    let found=query_values(c, d).ok();
    match values(d).and_then(|v|circuit(d, &v)){
        Ok((now, reads))=>{
            preservation&=get(d, "admission.state")==if now{
                "allow"
            }
            else{
                "deny"
            };
            preservation&=set(get(d, "admission.reads"))==reads.iter().map(String::as_str).collect::<BTreeSet<_>>();
        },
        Err(_)=>preservation=false,
    }
    if found.is_none(){
        preservation=false;
    }
    dims.insert("Preservation", preservation);
    dims.insert("Localization", QUERIES.iter().all(|q|{
        let lineage=set(get(d, &format!("lineage.{q}")));
        requires(q).iter().all(|r|lineage.contains(r))
    }));
    for(k, v)in &dims{
        if !v{
            issues.insert(k.to_string());
        }
    }
    let established=pre&&dims.values().all(|x|*x)&&found.is_some();
    let mut report=Doc::from([("schema".into(), "isa-report-1".into()), ("audit".into(), if established{
        "established"
    }
    else{
        "not_established"
    }.into()), ("issues".into(), issues.into_iter().collect::<Vec<_>>().join(",")), ("trust_scope".into(), "synthetic-collector-root".into()), ("formation.path".into(), "not_adjudicated".into()), ("formation.attribution".into(), "not_adjudicated".into()), ("formation.constraint".into(), "not_adjudicated".into()), ("verdict".into(), "Unadjudicable".into())]);
    for(k, v)in dims{
        report.insert(format!("audit.{}", k.to_lowercase()), if v{
            "supported"
        }
        else{
            "not_established"
        }.into());
    }
    for q in QUERIES{
        let state=if established{
            if found.as_ref().and_then(|f|f.get(q)).copied().unwrap_or(false){
                "supported"
            }
            else{
                "refuted"
            }
        }
        else{
            "not_adjudicated"
        };
        report.insert(format!("query.{q}"), state.into());
        report.insert(format!("lineage.{q}"), if established{
            get(d, &format!("lineage.{q}")).into()
        }
        else{
            String::new()
        });
    }
    if established{
        if let Some(f)=found{
            let p=f["path"];
            let a=f["source"]&&f["authority"]&&f["effect"];
            let con=f["control"]&&f["eligibility"];
            for(k, v)in[("path", p), ("attribution", a), ("constraint", con)]{
                report.insert(format!("formation.{k}"), if v{
                    "supported"
                }
                else{
                    "refuted"
                }.into());
            }
            report.insert("verdict".into(), if p&&a&&con{
                "Conformant"
            }
            else{
                "Non-conformant"
            }.into());
        }
    }
    report
}
#[cfg(test)]mod tests{
    use super::*;
    #[test]fn empty_evidence_abstains(){
        let r=check(&Doc::new(), &Doc::new(), &Doc::new());
        assert_eq!(get(&r, "verdict"), "Unadjudicable");
        assert_eq!(get(&r, "formation.constraint"), "not_adjudicated");
    }
    #[test]fn interpreter_rejects_forward_reference(){
        let d=Doc::from([("program.count".into(), "1".into()), ("program.root".into(), "0".into()), ("program.0".into(), "A:0".into())]);
        assert!(circuit(&d, &BTreeMap::new()).is_err());
    }
    #[test]fn unknown_instruction_rejected(){
        let d=Doc::from([("program.count".into(), "1".into()), ("program.root".into(), "0".into()), ("program.0".into(), "read-oracle".into())]);
        assert!(circuit(&d, &BTreeMap::new()).is_err());
    }
    #[test]fn denial_and_execution_amount_binding(){
        let c=Doc::from([("amount".into(),"200000".into())]);
        let mut d=Doc::from([
            ("decision.amount".into(),"200000".into()),
            ("admission.state".into(),"allow".into()),
            ("execution.status".into(),"paid".into()),
            ("execution.amount".into(),"200000".into()),
        ]);
        assert!(execution_binding(&c,&d));
        d.insert("admission.state".into(),"deny".into());
        assert!(!execution_binding(&c,&d),"Denied action cannot be executed");
        d.insert("admission.state".into(),"allow".into());
        d.insert("execution.amount".into(),"300000".into());
        assert!(!execution_binding(&c,&d),"Execution amount must match the decision");
        d.insert("execution.status".into(),"refused".into());
        d.insert("execution.amount".into(),"0".into());
        assert!(execution_binding(&c,&d),"Admitted action may fail downstream without executing");
        d.insert("decision.amount".into(),"300000".into());
        assert!(!execution_binding(&c,&d),"Decision amount must match the instance claim");
    }
}
