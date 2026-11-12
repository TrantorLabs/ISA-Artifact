//! Deterministic formation execution. Configuration changes real relations.
#![forbid(unsafe_code)] use std::collections::{
    BTreeMap,
    BTreeSet
};
use isa_core::{
    applicable,
    Doc,
    EventSink,
    Op,
    Program,
    CHANNELS,
    KINDS,
    QUERIES,
    requires,
    get
};
#[derive(Clone, Debug)] pub struct Spec {
    pub amount:u64,
    pub threshold:u64,
    pub values:BTreeMap<String,
    bool>,
    pub program:Program,
    pub actual_source:String,
    pub bound_source:String,
    pub authority_scopes:[String;2],
    pub authority_subjects:[String;2],
    pub bound_controller:String,
    pub execution_instance:String,
    pub execution_decision:String,
    pub execution_admission:String,
    pub route:String,
    pub include_applicable:Option<Vec<String>>,
}
impl Default for Spec {
    fn default()->Self{
        Self{
            amount:200_000,
            threshold:100_000,
            values:KINDS.iter().map(|s|(s.to_string(), true)).collect(),
            program:Program::canonical(),
            actual_source:"supplier-record".into(),
            bound_source:"supplier-record".into(),
            authority_scopes:["payment".into(), "payment".into()],
            authority_subjects:["H1".into(), "H2".into()],
            bound_controller:"controller-1".into(),
            execution_instance:"u-1".into(),
            execution_decision:"d-1".into(),
            execution_admission:"a-1".into(),
            route:"standard".into(),
            include_applicable:None,
        }
    }
}
#[derive(Clone, Debug)] pub struct Run {
    pub context:Doc,
    pub spec:Spec,
    pub applicable:Vec<String>,
    pub admission:bool,
    pub executed:bool,
    pub reads:BTreeSet<String>,
    pub ledger:Doc,
    pub events:Vec<(String, Doc)>
}
pub fn context(s:&Spec)->Doc{
    let mut d=Doc::from([ ("schema".into(), "isa-context-1".into()), ("system".into(), "payment-reference".into()), ("version".into(), "1".into()), ("instance".into(), "u-1".into()), ("decision".into(), "d-1".into()), ("admission".into(), "a-1".into()), ("amount".into(), s.amount.to_string()), ("dual_threshold".into(), s.threshold.to_string()), ("required_scope".into(), "payment".into()), ("declared_tick".into(), "0".into()), ("start_tick".into(), "10".into()), ("gamma".into(), KINDS.join(",")), ("queries".into(), QUERIES.join(",")), ("channels".into(), CHANNELS.join(",")), ("collector".into(), "collector-1".into()), ("monitor".into(), "monitor-1".into()), ("controller".into(), "controller-1".into()), ("boundary".into(), "finite-enterprise-payment".into()), ("threat_model".into(), "synthetic-collector-root".into())]);
    for q in QUERIES{
        d.insert(format!("requires.{q}"), requires(q).join(","));
    }
    for ch in CHANNELS{
        d.insert(format!("writers.{ch}"), "collector-1".into());
    }
    d
}
pub fn evaluate(p:&Program, values:&BTreeMap<String, bool>)->Result<(bool, BTreeSet<String>), String>{
    p.validate()?;
    fn visit(i:usize, p:&Program, v:&BTreeMap<String, bool>, memo:&mut BTreeMap<usize, bool>, reads:&mut BTreeSet<String>)->Result<bool,
    String>{
        if let Some(x)=memo.get(&i){
            return Ok(*x);
        }
        let value=match &p.code[i]{
            Op::Constant(x)=>*x,
            Op::Input(k)=>{
                reads.insert(k.clone());
                *v.get(k).ok_or_else(||format!("missing evaluation: {k}"))?
            },
            Op::All(js)|Op::Any(js)=>{
                let mut args=Vec::new();
                for j in js{
                    args.push(visit(*j, p, v, memo, reads)?);
                }
                if matches!(&p.code[i], Op::All(_)){
                    args.iter().all(|x|*x)
                }
                else{
                    args.iter().any(|x|*x)
                }
            }
        };
        memo.insert(i, value);
        Ok(value)
    }
    let mut reads=BTreeSet::new();
    let result=visit(p.root, p, values, &mut BTreeMap::new(), &mut reads)?;
    Ok((result, reads))
}
fn fields(values:&[(&str, String)])->Doc{
    values.iter().map(|(k, v)|(k.to_string(), v.clone())).collect()
}
fn emit(name:&str, local:Doc, events:&mut Vec<(String, Doc)>, sink:&mut dyn EventSink)->Result<(), String>{
    let full=local.into_iter().map(|(k, v)|(format!("{name}.{k}"), v)).collect::<Doc>();
    sink.observe(name, &full)?;
    events.push((name.into(), full));
    Ok(())
}
pub fn run(s:&Spec, c:&Doc, sink:&mut dyn EventSink)->Result<Run, String>{
    if s.amount>1_000_000_000||s.threshold>1_000_000_000{
        return Err("amount outside reference profile".into());
    }
    let app=applicable(s.amount, s.threshold);
    let selected=s.include_applicable.as_ref().unwrap_or(&app);
    let mut events=Vec::new();
    let u=get(c, "instance");
    emit("decision", fields(&[("instance", u.into()), ("id", get(c, "decision").into()), ("amount", s.amount.to_string()), ("candidate", "candidate-1".into())]), &mut events, sink)?;
    emit("source", fields(&[("instance", u.into()), ("actual", s.actual_source.clone()), ("bound", s.bound_source.clone())]), &mut events, sink)?;
    emit("authority", fields(&[("instance", u.into()), ("h1", s.authority_subjects[0].clone()), ("h2", s.authority_subjects[1].clone()), ("scope1", s.authority_scopes[0].clone()), ("scope2", s.authority_scopes[1].clone())]), &mut events, sink)?;
    emit("effect", fields(&[("instance", u.into()), ("actual_controller", get(c, "controller").into()), ("bound_controller", s.bound_controller.clone())]), &mut events, sink)?;
    let mut ev=fields(&[("instance", u.into()), ("applicable", selected.join(","))]);
    for k in KINDS{
        ev.insert(k.into(), u8::from(*s.values.get(k).ok_or("missing evaluator")?).to_string());
    }
    emit("evaluation", ev, &mut events, sink)?;
    let pg=s.program.records();
    sink.observe("program", &pg)?;
    events.push(("program".into(), pg));
    let(allow, reads)=evaluate(&s.program, &s.values)?;
    emit("admission", fields(&[("instance", u.into()), ("id", get(c, "admission").into()), ("decision", get(c, "decision").into()), ("state", if allow{
        "allow"
    }
    else{
        "deny"
    }.into()), ("reads", reads.iter().cloned().collect::<Vec<_>>().join(",")), ("controller", get(c, "controller").into())]), &mut events, sink)?;
    let executed=allow||s.route=="direct";
    let ledger=fields(&[("instance", s.execution_instance.clone()), ("decision", s.execution_decision.clone()), ("admission", if s.route=="direct"{
        "direct".into()
    }
    else{
        s.execution_admission.clone()
    }), ("status", if executed{
        "paid"
    }
    else{
        "refused"
    }.into()), ("amount", if executed{
        s.amount
    }
    else{
        0
    }.to_string()), ("channel", "standard".into()), ("route", s.route.clone())]);
    emit("execution", ledger.clone(), &mut events, sink)?;
    emit("lineage", QUERIES.iter().map(|q|(q.to_string(), requires(q).join(","))).collect(), &mut events, sink)?;
    Ok(Run{
        context:c.clone(), spec:s.clone(), applicable:app, admission:allow, executed, reads, ledger, events
    })
}
pub fn baseline(r:&Run)->Doc{
    let mut d=Doc::from([("outcome".into(), get(&r.ledger, "status").into()), ("amount".into(), get(&r.ledger, "amount").into()), ("channel".into(), get(&r.ledger, "channel").into()), ("explanation".into(), "Payment evaluated under declared enterprise rules.".into())]);
    for(k, v)in &r.spec.values{
        d.insert(format!("check.{k}"), u8::from(*v).to_string());
    }
    d
}
#[cfg(test)]mod tests{
    use super::*;
    #[test]fn gate_actually_denies(){
        let s=Spec::default();
        let mut v=s.values.clone();
        v.insert("recipient".into(), false);
        assert!(!evaluate(&s.program, &v).unwrap().0);
    }
    #[test]fn shadow_can_allow_same_inputs(){
        let mut s=Spec::default();
        s.program.code[4]=Op::Constant(true);
        s.values.insert("recipient".into(), false);
        let(a, reads)=evaluate(&s.program, &s.values).unwrap();
        assert!(a);
        assert!(reads.is_empty());
    }
    #[test]fn consultation_is_not_control(){
        let mut s=Spec::default();
        s.program.code.push(Op::Constant(true));
        s.program.code.push(Op::Any(vec![4, 5]));
        s.program.root=6;
        let(a, reads)=evaluate(&s.program, &s.values).unwrap();
        assert!(a);
        assert_eq!(reads.len(), 4);
        s.values.insert("recipient".into(), false);
        assert!(evaluate(&s.program, &s.values).unwrap().0);
    }
    #[test]fn formal_two_group_projection_matches_all_payment_evaluations(){
        // FQ1 uses two grouped inputs. Check their exact operational meaning
        // against the actual four-input DAG for every finite valuation.
        for root_kind in 0..5 {
            let mut code=KINDS.iter().map(|k|Op::Input(k.to_string())).collect::<Vec<_>>();
            code.push(Op::All(vec![0,1]));
            code.push(Op::All(vec![2,3]));
            let root=match root_kind {
                0=>4,
                1=>5,
                2=>{code.push(Op::All(vec![4,5]));6},
                3=>{code.push(Op::Any(vec![4,5]));6},
                _=>{code.push(Op::Constant(true));6}
            };
            let program=Program{code,root};
            for bits in 0..16u32 {
                let x=(bits & 1)!=0 && (bits & 2)!=0;
                let y=(bits & 4)!=0 && (bits & 8)!=0;
                let expected=match root_kind {
                    0=>x, 1=>y, 2=>x&&y, 3=>x||y, _=>true
                };
                let values=KINDS.iter().enumerate().map(|(i,k)|
                    (k.to_string(),bits & (1<<i)!=0)
                ).collect::<BTreeMap<_,_>>();
                let (actual,_)=evaluate(&program,&values).unwrap();
                assert_eq!(actual,expected,"root_kind={root_kind} bits={bits}");
            }
        }
    }
}
