//! ISA/1: sorted keys, tab, lowercase hex-encoded UTF-8 values, END terminator.
//! Deliberately small protocol; no floating point, implicit defaults, duplicate keys.
use crate::Doc;
pub const MAX_BYTES:usize=1_048_576;
pub const MAX_FIELDS:usize=4096;
fn valid_key(k:&str)->bool {
    !k.is_empty() && k.len()<=160 && k.as_bytes()[0].is_ascii_lowercase() && k.bytes().all(|b|b.is_ascii_lowercase()||b.is_ascii_digit()||b"_.-".contains(&b))
}
pub fn encode(d:&Doc)->Vec<u8>{
    const HEX:&[u8]=b"0123456789abcdef";
    let mut out=b"ISA/1\n".to_vec();
    for(k, v) in d {
        out.extend_from_slice(k.as_bytes());
        out.push(b'\t');
        for b in v.as_bytes(){
            out.push(HEX[(b>>4)as usize]);
            out.push(HEX[(b&15)as usize]);
        }
        out.push(b'\n');
    }
    out.extend_from_slice(b"END\n");
    out
}
fn nibble(b:u8)->Result<u8, String>{
    match b{
        b'0'..=b'9'=>Ok(b-b'0'),
        b'a'..=b'f'=>Ok(b-b'a'+10),
        _=>Err("noncanonical hexadecimal".into())
    }
}
pub fn decode(data:&[u8])->Result<Doc, String>{
    if data.len()>MAX_BYTES {
        return Err("document too large".into());
    }
    if !data.is_ascii(){
        return Err("wire envelope must be ASCII".into());
    }
    let s=std::str::from_utf8(data).map_err(|_|"invalid wire text")?;
    let lines=s.lines().collect::<Vec<_>>();
    if lines.len()<2||lines[0]!="ISA/1"||lines.last()!=Some(&"END"){
        return Err("missing framing".into());
    }
    if lines.len()-2>MAX_FIELDS{
        return Err("too many fields".into());
    }
    let mut d=Doc::new();
    for line in &lines[1..lines.len()-1]{
        let(k, v)=line.split_once('\t').ok_or("missing field delimiter")?;
        if !valid_key(k)||d.contains_key(k)||v.contains('\t')||v.len()%2!=0{
            return Err("invalid or duplicate field".into());
        }
        let mut bytes=Vec::with_capacity(v.len()/2);
        for pair in v.as_bytes().chunks_exact(2){
            bytes.push(nibble(pair[0])?*16+nibble(pair[1])?);
        }
        let value=String::from_utf8(bytes).map_err(|_|"invalid UTF-8 value")?;
        d.insert(k.into(), value);
    }
    Ok(d)
}
#[cfg(test)] mod tests{
    use super::*;
    #[test] fn unicode_roundtrip(){
        let d=Doc::from([("name".into(), "判断\n行动\t".into())]);
        assert_eq!(decode(&encode(&d)).unwrap(), d);
    }
    #[test] fn duplicate_rejected(){
        assert!(decode(b"ISA/1\nx\t30\nx\t31\nEND\n").is_err());
    }
    #[test] fn missing_end_rejected(){
        assert!(decode(b"ISA/1\nx\t30\n").is_err());
    }
    #[test] fn uppercase_hex_rejected(){
        assert!(decode(b"ISA/1\nx\tFF\nEND\n").is_err());
    }
    #[test] fn bad_utf8_rejected(){
        assert!(decode(b"ISA/1\nx\tff\nEND\n").is_err());
    }
    #[test] fn non_ascii_envelope_rejected(){
        assert!(decode("ISA/1\n中文\t30\nEND\n".as_bytes()).is_err());
    }
    #[test] fn oversize_rejected(){
        assert!(decode(&vec![b'x';MAX_BYTES+1]).is_err());
    }
}
