include!(concat!(env!("OUT_DIR"), "/host_schema_module.rs"));
use std::{env,fs,process};
fn main() {
    let paths: Vec<_> = env::args().skip(1).collect();
    if paths.is_empty() { eprintln!("usage: pantry-model-schema-probe request.json [...]"); process::exit(2); }
    let mut failed = false;
    for path in paths {
        let value: serde_json::Value = serde_json::from_slice(&fs::read(&path).expect("request file")).expect("request JSON");
        let source = value.get("schema").unwrap_or(&value);
        match host_schema::Schema::compile(source) {
            Ok(_) => println!("PASS {}",path),
            Err(error) => { eprintln!("REJECT {}: {}",path,error); failed = true; }
        }
    }
    if failed { process::exit(1); }
}
