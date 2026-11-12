//! Research scenario registry. No labels cross the checker input boundary.
#![forbid(unsafe_code)] use std::collections::{
    BTreeMap,
    BTreeSet
};
use isa_core::{
    Doc,
    Op,
    CHANNELS,
    fingerprint
};
use isa_engine::{
    Spec,
    Run,
    context,
    run
};
use isa_evidence::Collector;
pub const IDS:[&str;22]=["E00", "E01", "E02-S", "E02-A", "E02-E", "E03-S", "E03-B", "E04-I", "E04-N", "E04-S", "E04-P", "E04-L", "E07", "E08", "E09", "E10", "M1-APPLICABILITY", "M2-CONTRACT", "M2-CHERRY", "E11-BLIND-SHADOW", "E12-DENY", "E13-LOW-VALUE"];
#[derive(Clone, Debug)]pub struct SystemWorld{
    pub channels:BTreeSet<String>,
    pub governed:BTreeSet<String>,
    pub edges:Vec<(String, String)>,
    pub gates:BTreeMap<String,
    Vec<bool>>,
    pub root:String
}
impl SystemWorld{
    pub fn reference(kind:&str)->Self{
        let channels=["standard", "batch", "privileged"].iter().map(|s|s.to_string()).collect::<BTreeSet<_>>();
        let mut edges=vec![("candidate".into(), "gate".into())];
        for c in &channels{
            edges.push(("gate".into(), format!("executor-{c}")));
            edges.push((format!("executor-{c}"), c.clone()));
        }
        let mut governed=channels.clone();
        if kind=="E07"{
            governed.remove("batch");
        }
        if kind=="E08"{
            edges.push(("candidate".into(), "executor-batch".into()));
        }
        if kind=="E09"{
            edges.push(("candidate".into(), "executor-standard".into()));
        }
        Self{
            channels,
            governed,
            edges,
            gates:BTreeMap::from([("gate".into(), vec![false, true])]),
            root:"candidate".into()
        }
    }
    pub fn public_evidence(&self)->Doc{
        let mut edges = self.edges.clone();
        edges.sort();
        let mut d=Doc::from([("schema".into(), "isa-system-1".into()), ("root".into(), self.root.clone()), ("actual".into(), self.channels.iter().cloned().collect::<Vec<_>>().join(",")), ("governed".into(), self.governed.iter().cloned().collect::<Vec<_>>().join(",")), ("edges".into(), edges.iter().map(|(a, b)|format!("{a}>{b}")).collect::<Vec<_>>().join(",")), ("gates".into(), self.gates.keys().cloned().collect::<Vec<_>>().join(","))]);
        for(k, v)in &self.gates{
            d.insert(format!("gate.{k}.outputs"), v.iter().map(|x|u8::from(*x).to_string()).collect::<Vec<_>>().join(","));
        }
        d
    }
    pub fn report(&self)->Doc{
        fn paths(node:&str, target:&str, seen:&mut Vec<String>, edges:&[(String, String)], out:&mut Vec<Vec<String>>){
            if seen.len()>32{
                return;
            }
            seen.push(node.into());
            if node==target{
                out.push(seen.clone());
            }
            else{
                for(a, b)in edges{
                    if a==node&&!seen.contains(b){
                        paths(b, target, seen, edges, out);
                    }
                }
            }
            seen.pop();
        }
        let effective=self.gates.iter().filter(|(_, v)|v.contains(&false)&&v.contains(&true)).map(|(k, _)|k.clone()).collect::<BTreeSet<_>>();
        let coverage=self.channels.is_subset(&self.governed);
        let mut mediation=true;
        for c in &self.governed{
            let mut all=Vec::new();
            paths(&self.root, c, &mut Vec::new(), &self.edges, &mut all);
            mediation&=all.iter().all(|p|p.iter().any(|n|effective.contains(n)));
        }
        Doc::from([("schema".into(), "isa-system-report-1".into()), ("coverage".into(), u8::from(coverage).to_string()), ("mediation".into(), u8::from(mediation).to_string()), ("scope".into(), "declared-finite-graph".into())])
    }
}
pub struct Case{
    pub name:String,
    pub context:Doc,
    pub evidence:Doc,
    pub seal:Doc,
    pub world:Run,
    pub system:SystemWorld
}
pub fn build(name:&str)->Result<Case, String>{
    if !IDS.contains(&name){
        return Err("unknown scenario".into());
    }
    let mut s=Spec::default();
    match name{
        "E01"=>s.execution_instance="u-other".into(),
        "E02-S"=>s.bound_source="unrelated-record".into(),
        "E02-A"=>s.authority_scopes[1]="read-only".into(),
        "E02-E"=>s.bound_controller="adviser-1".into(),
        "E03-S"|"E11-BLIND-SHADOW"=>s.program.code[4]=Op::Constant(true),
        "E03-B"=>{
            s.program.code[4]=Op::Any(vec![0, 1, 2, 3]);
            s.values.insert("recipient".into(), false);
        },
        "E09"=>{
            s.route="direct".into();
            s.values.insert("recipient".into(), false);
        },
        "M1-APPLICABILITY"=>{
            s.values.insert("recipient".into(), false);
            s.include_applicable=Some(vec!["transaction".into(), "dual".into(), "channel".into()]);
            s.program.code[4]=Op::All(vec![1, 2, 3]);
        },
        "E12-DENY"=>{
            s.values.insert("recipient".into(), false);
        },
        "E13-LOW-VALUE"=>{
            s.amount=100;
            s.program.code[4]=Op::All(vec![0, 1, 3]);
            s.authority_scopes[1]="read-only".into();
        },
        _=>{
        }
    }
    let mut c=context(&s);
    if name=="E04-N"{
        for ch in CHANNELS{
            c.insert(format!("writers.{ch}"), "collector-1,controller-1".into());
        }
    }
    if name=="E04-S"{
        c.insert("queries".into(), "path,source,authority,effect,eligibility".into());
    }
    let mut collector=Collector::new(&c);
    let world=run(&s, &c, &mut collector)?;
    let replace=if name=="E04-P"{
        Doc::from([("program.4".into(), "O:0,1,2,3".into())])
    }
    else{
        Doc::new()
    };
    let mut omit=BTreeSet::new();
    if name=="E04-L"{
        omit.insert("lineage.control".into());
    }
    if name=="E10"||name=="E11-BLIND-SHADOW"{
        omit.extend(s.program.records().keys().cloned());
    }
    let(mut evidence, seal)=collector.finish(&replace, &omit)?;
    if name=="E04-I"{
        evidence.insert("execution.amount".into(), "999".into());
    }
    if name=="M2-CONTRACT"{
        let mut changed=c.clone();
        changed.insert("queries".into(), "path".into());
        evidence.insert("context_digest".into(), fingerprint(&changed));
    }
    if name=="M2-CHERRY"{
        evidence.insert("program.4".into(), "T".into());
    }
    Ok(Case{
        name:name.into(), context:c, evidence, seal, world, system:SystemWorld::reference(name)
    })
}
#[cfg(test)]mod tests{
    use super::*;
    #[test]fn canonical_twins_observe_same_outcome(){
        let a=build("E00").unwrap();
        let b=build("E03-S").unwrap();
        assert_eq!(isa_engine::baseline(&a.world), isa_engine::baseline(&b.world));
        assert_ne!(a.evidence, b.evidence);
        assert_eq!(a.context, b.context);
    }
    #[test]fn missing_evidence_does_not_change_world(){
        let a=build("E00").unwrap();
        let b=build("E10").unwrap();
        assert_eq!(a.world.events, b.world.events);
        assert!(!b.evidence.contains_key("program.4"));
    }
    #[test]fn invalid_scope_is_real_relation_fault(){
        let a=build("E02-A").unwrap();
        assert_eq!(a.world.spec.authority_scopes[1], "read-only");
        assert!(a.world.admission);
    }
    #[test]fn system_scale_is_independent(){
        let a=build("E07").unwrap();
        assert_eq!(isa_core::get(&a.system.report(), "coverage"), "0");
        assert!(a.world.admission);
    }
}
