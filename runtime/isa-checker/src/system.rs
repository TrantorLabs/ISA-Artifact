//! Separate system-level finite-graph analysis; never changes instance ISA verdict.
use std::collections::{
    BTreeMap,
    BTreeSet,
    VecDeque
};
use isa_core::{
    Doc,
    get,
    split
};
pub fn check(d:&Doc)->Result<Doc, String>{
    if get(d, "schema")!="isa-system-1"{
        return Err("invalid system schema".into());
    }
    let root=get(d, "root");
    if root.is_empty(){
        return Err("missing graph root".into());
    }
    let actual=split(get(d, "actual")).into_iter().collect::<BTreeSet<_>>();
    let governed=split(get(d, "governed")).into_iter().collect::<BTreeSet<_>>();
    let mut adjacency=BTreeMap::<&str,
    Vec<&str>>::new();
    let mut nodes=BTreeSet::new();
    for edge in split(get(d, "edges")){
        let(a, b)=edge.split_once('>').ok_or("invalid edge")?;
        if a.is_empty()||b.is_empty(){
            return Err("empty vertex".into());
        }
        adjacency.entry(a).or_default().push(b);
        nodes.insert(a);
        nodes.insert(b);
    }
    if nodes.len()>32||actual.is_empty(){
        return Err("finite graph exceeds profile or has no channel".into());
    }
    let mut effective=BTreeSet::new();
    for gate in split(get(d, "gates")){
        let outputs=split(get(d, &format!("gate.{gate}.outputs")));
        if outputs.contains(&"0")&&outputs.contains(&"1"){
            effective.insert(gate);
        }
    }
    fn reachable<'a>(root:&'a str, adj:&BTreeMap<&'a str, Vec<&'a str>>, blocked:&BTreeSet<&'a str>)->BTreeSet<&'a str>{
        let mut seen=BTreeSet::new();
        let mut todo=VecDeque::from([root]);
        while let Some(n)=todo.pop_front(){
            if blocked.contains(n)||!seen.insert(n){
                continue;
            }
            if let Some(ns)=adj.get(n){
                todo.extend(ns.iter().copied());
            }
        }
        seen
    }
    let all=reachable(root, &adjacency, &BTreeSet::new());
    if !actual.is_subset(&all){
        return Err("claimed actual channel not reachable in finite model".into());
    }
    let unmediated=reachable(root, &adjacency, &effective);
    let coverage=actual.is_subset(&governed);
    let mediation=governed.iter().all(|c|!unmediated.contains(c));
    Ok(Doc::from([("schema".into(), "isa-system-report-1".into()), ("coverage".into(), u8::from(coverage).to_string()), ("mediation".into(), u8::from(mediation).to_string()), ("scope".into(), "declared-finite-graph".into())]))
}
#[cfg(test)]mod tests{
    use super::*;
    #[test]fn direct_path_fails_mediation(){
        let d=Doc::from([("schema".into(), "isa-system-1".into()), ("root".into(), "r".into()), ("actual".into(), "c".into()), ("governed".into(), "c".into()), ("edges".into(), "r>g,g>c,r>c".into()), ("gates".into(), "g".into()), ("gate.g.outputs".into(), "0,1".into())]);
        let out=check(&d).unwrap();
        assert_eq!(get(&out, "coverage"), "1");
        assert_eq!(get(&out, "mediation"), "0");
    }
}
