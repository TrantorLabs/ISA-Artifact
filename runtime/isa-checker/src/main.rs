//! Stream-only adjudication. Explicit context and trusted collector-seal inputs.
#![forbid(unsafe_code)] use std::io::{
    Read,
    Write
};
use std::path::PathBuf;
use isa_core::wire::{
    decode,
    encode,
    MAX_BYTES
};
fn main(){
    if let Err(e)=execute(){
        eprintln!("invalid input: {e}");
        std::process::exit(2);
    }
}
fn read_file(path:&PathBuf)->Result<isa_core::Doc, String>{
    let mut data=Vec::new();
    std::fs::File::open(path).map_err(|e|e.to_string())?.take((MAX_BYTES+1)as u64).read_to_end(&mut data).map_err(|e|e.to_string())?;
    decode(&data)
}
fn execute()->Result<(), String>{
    let mut args=std::env::args_os().skip(1);
    let mut context=None;
    let mut seal=None;
    let mut system=false;
    while let Some(arg)=args.next(){
        match arg.to_str(){
            Some("--system")=>{
                system=true;
            },
            Some("--context")=>{
                if context.is_some(){
                    return Err("duplicate --context".into());
                }
                context=Some(PathBuf::from(args.next().ok_or("missing context path")?));
            },
            Some("--seal")=>{
                if seal.is_some(){
                    return Err("duplicate --seal".into());
                }
                seal=Some(PathBuf::from(args.next().ok_or("missing seal path")?));
            },
            Some("--help")=>{
                println!("isa-checker --context TRUSTED_CONTEXT.isa --seal TRUSTED_COLLECTOR_SEAL.isa < evidence.isa\nCollector trust is an explicit research assumption, not supplied by a checksum.");
                return Ok(());
            },
            _=>return Err("unknown argument".into()),
        }
    }
    if system{
        if context.is_some()||seal.is_some(){
            return Err("system analysis does not accept instance context".into());
        }
        let mut raw=Vec::new();
        std::io::stdin().take((MAX_BYTES+1)as u64).read_to_end(&mut raw).map_err(|e|e.to_string())?;
        let report=isa_checker::system::check(&decode(&raw)?)?;
        std::io::stdout().write_all(&encode(&report)).map_err(|e|e.to_string())?;
        return Ok(());
    }
    let c=read_file(&context.ok_or("--context required")?)?;
    let s=read_file(&seal.ok_or("--seal required")?)?;
    let mut data=Vec::new();
    std::io::stdin().take((MAX_BYTES+1)as u64).read_to_end(&mut data).map_err(|e|e.to_string())?;
    let d=decode(&data)?;
    let r=isa_checker::check(&c, &s, &d);
    std::io::stdout().write_all(&encode(&r)).map_err(|e|e.to_string())?;
    Ok(())
}
