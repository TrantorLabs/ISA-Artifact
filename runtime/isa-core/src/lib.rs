//! Shared semantic vocabulary and strict wire encoding. No audit decisions or oracle.
#![forbid(unsafe_code)] use std::collections::BTreeMap;
pub mod wire;
pub mod sha256;
pub type Doc = BTreeMap<String, String>;
pub const CHANNELS: [&str;9] = ["decision", "source", "authority", "effect", "evaluation", "program", "admission", "execution", "lineage"];
pub const QUERIES: [&str;6] = ["path", "source", "authority", "effect", "control", "eligibility"];
pub const KINDS: [&str;4] = ["recipient", "transaction", "dual", "channel"];
pub fn requires(q: &str) -> &'static [&'static str] {
    match q {
        "path" => &["decision", "admission", "execution"],
        "source" => &["source"],
        "authority" => &["authority"],
        "effect" => &["effect", "admission"],
        "control" | "eligibility" => &["evaluation", "program", "admission"],
        _ => &[],
    }
}
pub fn get<'a>(doc: &'a Doc, key: &str) -> &'a str {
    doc.get(key).map(String::as_str).unwrap_or("")
}
pub fn split(value: &str) -> Vec<&str> {
    value.split(',').filter(|x| !x.is_empty()).collect()
}
pub fn channel(doc: &Doc, name: &str) -> Doc {
    let prefix = format!("{name}.");
    doc.iter().filter(|(k, _)| k.starts_with(&prefix)).map(|(k, v)|(k.clone(), v.clone())).collect()
}
pub fn fingerprint(doc: &Doc) -> String {
    sha256::hex(&wire::encode(doc))
}
pub fn uint(value: &str, upper: u64) -> Result<u64, String> {
    if value.is_empty() || !value.bytes().all(|b|b.is_ascii_digit()) || (value.len()>1 && value.starts_with('0')) {
        return Err("invalid unsigned integer".into());
    }
    let n = value.parse::<u64>().map_err(|_|"integer overflow".to_string())?;
    if n>upper {
        Err("integer outside declared bound".into())
    }
    else {
        Ok(n)
    }
}
pub fn bit(value: &str) -> Result<bool, String> {
    match value {
        "0"=>Ok(false),
        "1"=>Ok(true),
        _=>Err("invalid Boolean".into())
    }
}
pub fn applicable(amount: u64, threshold: u64) -> Vec<String> {
    KINDS.iter().filter(|k| **k!="dual" || amount>threshold).map(|s|s.to_string()).collect()
}
/// Boolean DAG instructions. These are executable relations, not conformance flags.
#[derive(Clone, Debug, PartialEq, Eq)] pub enum Op {
    Input(String),
    All(Vec<usize>),
    Any(Vec<usize>),
    Constant(bool)
}
impl Op {
    pub fn text(&self)->String {
        match self {
            Self::Input(k)=>format!("E:{k}"),
            Self::All(v)=>format!("A:{}", v.iter().map(usize::to_string).collect::<Vec<_>>().join(",")),
            Self::Any(v)=>format!("O:{}", v.iter().map(usize::to_string).collect::<Vec<_>>().join(",")),
            Self::Constant(true)=>"T".into(),
            Self::Constant(false)=>"F".into(),
        }
    }
    pub fn parse(text:&str)->Result<Self,
    String> {
        if text=="T" {
            return Ok(Self::Constant(true));
        }
        if text=="F" {
            return Ok(Self::Constant(false));
        }
        if let Some(k)=text.strip_prefix("E:") {
            if KINDS.contains(&k) {
                return Ok(Self::Input(k.into()));
            }
            return Err("unknown evaluator".into());
        }
        let (kind, tail)=text.split_once(':').ok_or("invalid opcode")?;
        let refs=split(tail).iter().map(|x|uint(x, 31).map(|n|n as usize)).collect::<Result<Vec<_>,
        _>>()?;
        if refs.is_empty() {
            return Err("empty operator".into());
        }
        match kind {
            "A"=>Ok(Self::All(refs)),
            "O"=>Ok(Self::Any(refs)),
            _=>Err("unsupported opcode".into())
        }
    }
}
#[derive(Clone, Debug)] pub struct Program {
    pub code: Vec<Op>,
    pub root: usize
}
impl Program {
    pub fn canonical()->Self {
        let mut code=KINDS.iter().map(|x|Op::Input(x.to_string())).collect::<Vec<_>>();
        code.push(Op::All(vec![0, 1, 2, 3]));
        Self {
            code,
            root:4
        }
    }
    pub fn records(&self)->Doc {
        let mut d=Doc::from([("program.root".into(), self.root.to_string()), ("program.count".into(), self.code.len().to_string())]);
        for (i, op) in self.code.iter().enumerate(){
            d.insert(format!("program.{i}"), op.text());
        }
        d
    }
    pub fn validate(&self)->Result<(),
    String>{
        if self.code.is_empty() || self.code.len()>32 || self.root>=self.code.len(){
            return Err("invalid program bounds".into());
        }
        for (i, op) in self.code.iter().enumerate(){
            match op {
                Op::All(v)|Op::Any(v) if v.is_empty() || v.iter().any(|j|*j>=i)=>return Err("program must be acyclic".into()),
                Op::Input(k) if !KINDS.contains(&k.as_str())=>return Err("unknown evaluator".into()),
                _=>{
                }
            }
        }
        Ok(())
    }
}
/// Event observers receive executed relations only, never hidden research labels.
pub trait EventSink {
    fn observe(&mut self, name: &str, fields: &Doc) -> Result<(),
    String>;
}
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn applicability_uses_declared_threshold(){
        assert_eq!(applicable(1, 2).len(), 3);
        assert_eq!(applicable(3, 2).len(), 4);
    }
    #[test] fn circuit_must_be_acyclic(){
        let p=Program{
            code:vec![Op::All(vec![0])],
            root:0
        };
        assert!(p.validate().is_err());
    }
    #[test] fn roles_are_distinct(){
        assert_ne!(requires("source"), requires("authority"));
    }
    #[test] fn canonical_program_roundtrip(){
        for op in Program::canonical().code{
            assert_eq!(Op::parse(&op.text()).unwrap(), op);
        }
    }
}
