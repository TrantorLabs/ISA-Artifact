//! Research orchestration. The checker executes in another process with explicit inputs.
#![forbid(unsafe_code)] use std::path::{
    Path,
    PathBuf
};
use std::process::{
    Command,
    Stdio
};
use std::io::Write;
use std::sync::atomic::{
    AtomicUsize,
    Ordering
};
use std::time::{
    Duration,
    Instant
};
use isa_core::{
    Doc,
    get,
    wire
};
static COUNTER:AtomicUsize=AtomicUsize::new(0);
struct Scratch(PathBuf);
impl Scratch{
    fn new()->Result<Self,
    String>{
        let n=COUNTER.fetch_add(1, Ordering::SeqCst);
        let p=std::env::temp_dir().join(format!("isa-checker-{}-{n}", std::process::id()));
        std::fs::create_dir(&p).map_err(|e|e.to_string())?;
        Ok(Self(p))
    }
}
impl Drop for Scratch{
    fn drop(&mut self){
        let _=std::fs::remove_dir_all(&self.0);
    }
}
fn invoke(binary:&Path, c:&Doc, s:&Doc, d:&Doc, system:bool)->Result<Doc, String>{
    let dir=Scratch::new()?;
    let binary=std::fs::canonicalize(binary).map_err(|e|e.to_string())?;
    let mut command=Command::new(binary);
    command.current_dir(&dir.0).env_clear().stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
    if system{
        command.arg("--system");
    }
    else{
        for(name, doc)in[("context.isa", c), ("seal.isa", s)]{
            std::fs::write(dir.0.join(name), wire::encode(doc)).map_err(|e|e.to_string())?;
        }
        command.args(["--context", "context.isa", "--seal", "seal.isa"]);
    }
    let mut child=command.spawn().map_err(|e|e.to_string())?;
    child.stdin.take().ok_or("checker stdin unavailable")?.write_all(&wire::encode(d)).map_err(|e|e.to_string())?;
    let start=Instant::now();
    loop{
        if child.try_wait().map_err(|e|e.to_string())?.is_some(){
            break;
        }
        if start.elapsed()>Duration::from_secs(15){
            let _=child.kill();
            let _=child.wait();
            return Err("checker timed out".into());
        }
        std::thread::sleep(Duration::from_millis(5));
    }
    let output=child.wait_with_output().map_err(|e|e.to_string())?;
    if !output.status.success(){
        return Err(format!("checker failed: {}", String::from_utf8_lossy(&output.stderr)));
    }
    wire::decode(&output.stdout)
}
fn write(dir:&Path, name:&str, d:&Doc)->Result<(), String>{
    std::fs::create_dir_all(dir).map_err(|e|e.to_string())?;
    std::fs::write(dir.join(name), wire::encode(d)).map_err(|e|e.to_string())
}
fn main(){
    if let Err(e)=execute(){
        eprintln!("validation failed: {e}");
        std::process::exit(1);
    }
}
fn execute()->Result<(), String>{
    let mut args=std::env::args().skip(1);
    let mut selected=None;
    let mut checker=None;
    let mut out=PathBuf::from("results-rust");
    while let Some(arg)=args.next(){
        match arg.as_str(){
            "--checker"=>checker=Some(PathBuf::from(args.next().ok_or("missing checker path")?)),
            "--out"=>out=PathBuf::from(args.next().ok_or("missing output path")?),
            "--scenario"=>selected=Some(args.next().ok_or("missing scenario id")?),
            "--help"=>{
                println!("isa-harness --checker CHECKER_BINARY --out DIRECTORY [--scenario E00]\nPAY-00 aliases E00; PAY-01 aliases E03-S.");
                return Ok(());
            },
            _=>return Err(format!("unknown argument: {arg}")),
        }
    }
    let binary=checker.ok_or("--checker is required; build the separate runtime workspace first")?;
    let ids=match selected.as_deref(){
        Some("PAY-00")=>vec!["E00"],
        Some("PAY-01")=>vec!["E03-S"],
        Some(s)=>vec![s],
        None=>isa_scenarios::IDS.to_vec()
    };
    let mut count=0;
    for name in ids{
        let c=isa_scenarios::build(name)?;
        let report=invoke(&binary, &c.context, &c.seal, &c.evidence, false)?;
        // Oracle computation follows checker execution and is never transmitted to it.
        let expected=isa_oracle::expected(&c.world, &c.context, &c.seal, &c.evidence);
        for key in ["verdict", "formation.path", "formation.attribution", "formation.constraint"]{
            if get(&report, key)!=get(&expected, key){
                return Err(format!("{name}: mismatch for {key}: {} != {}", get(&report, key), get(&expected, key)));
            }
        }
        let system_evidence=c.system.public_evidence();
        let system=invoke(&binary, &Doc::new(), &Doc::new(), &system_evidence, true)?;
        if system!=c.system.report(){
            return Err(format!("{name}: system report mismatch"));
        }
        let public=out.join("cases").join(name);
        for(file, doc)in[("context.isa", &c.context), ("collector-seal.isa", &c.seal), ("evidence.isa", &c.evidence), ("report.isa", &report), ("system-report.isa", &system), ("system-evidence.isa", &system_evidence)]{
            write(&public, file, doc)?;
        }
        write(&public, "observation-omega0.isa", &isa_engine::baseline(&c.world))?;
        write(&out.join("research-only").join(name), "oracle.isa", &expected)?;
        println!("{name}: {} (matched)", get(&report, "verdict"));
        count+=1;
    }
    let a=isa_scenarios::build("E00")?;
    let b=isa_scenarios::build("E03-S")?;
    if a.context!=b.context||isa_engine::baseline(&a.world)!=isa_engine::baseline(&b.world)||a.evidence==b.evidence{
        return Err("canonical pair isolation failed".into());
    }
    let summary=Doc::from([("backend".into(), "rust".into()), ("scenarios".into(), count.to_string()), ("matched".into(), count.to_string()), ("pair".into(), "baseline-equal-structure-different".into())]);
    write(&out, "summary.isa", &summary)?;
    Ok(())
}
