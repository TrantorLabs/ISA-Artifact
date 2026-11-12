//! Streaming evidence collector. No engine, oracle or scenario dependency.
#![forbid(unsafe_code)] use std::collections::BTreeSet;
use isa_core::{
    Doc,
    EventSink,
    CHANNELS,
    channel,
    fingerprint,
    get,
    uint
};
pub struct Collector{
    context:Doc,
    records:Doc,
    registration:String,
    count:u64
}
impl Collector{
    pub fn new(c:&Doc)->Self{
        Self{
            context:c.clone(),
            records:Doc::from([("schema".into(), "isa-evidence-1".into()), ("context_digest".into(), fingerprint(c)), ("start_tick".into(), get(c, "start_tick").into())]),
            registration:String::new(),
            count:0
        }
    }
    /// Faulty serializer transforms are generic data transformations, never fault labels.
    pub fn finish(&self, replacements:&Doc, omit:&BTreeSet<String>)->Result<(Doc, Doc),
    String>{
        let mut d=self.records.clone();
        let finish=uint(get(&self.context, "start_tick"), 1_000_000_000)?.checked_add(self.count).ok_or("clock overflow")?;
        d.insert("finish_tick".into(), finish.to_string());
        for(k, v)in replacements{
            d.insert(k.clone(), v.clone());
        }
        for k in omit{
            d.remove(k);
        }
        let mut seal=Doc::from([("schema".into(), "isa-collector-seal-1".into()), ("context_digest".into(), fingerprint(&self.context)), ("collector".into(), get(&self.context, "collector").into()), ("monitor".into(), get(&self.context, "monitor").into()), ("registered_program_digest".into(), self.registration.clone()), ("start_tick".into(), get(&self.context, "start_tick").into()), ("finish_tick".into(), get(&d, "finish_tick").into())]);
        for name in CHANNELS{
            seal.insert(format!("digest.{name}"), fingerprint(&channel(&d, name)));
            if name!="lineage"{
                seal.insert(format!("monitor_digest.{name}"), fingerprint(&channel(&self.records, name)));
            }
        }
        Ok((d, seal))
    }
}
impl EventSink for Collector{
    fn observe(&mut self, name:&str, fields:&Doc)->Result<(),
    String>{
        if !CHANNELS.contains(&name)||fields.keys().any(|k|self.records.contains_key(k)||!k.starts_with(&format!("{name}."))){
            return Err("duplicate or unknown event".into());
        }
        self.records.extend(fields.clone());
        self.count+=1;
        if name=="program"{
            self.registration=fingerprint(fields);
        }
        Ok(())
    }
}
#[cfg(test)]mod tests{
    use super::*;
    #[test]fn duplicate_capture_is_rejected(){
        let c=Doc::from([("start_tick".into(), "10".into())]);
        let mut s=Collector::new(&c);
        let f=Doc::from([("program.count".into(), "1".into())]);
        s.observe("program", &f).unwrap();
        assert!(s.observe("program", &f).is_err());
    }
    #[test]fn unknown_channel_is_rejected(){
        let mut s=Collector::new(&Doc::new());
        assert!(s.observe("oracle", &Doc::new()).is_err());
    }
}
