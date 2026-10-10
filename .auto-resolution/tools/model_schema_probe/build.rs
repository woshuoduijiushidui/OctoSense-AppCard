use std::{env,fs,path::PathBuf};
fn main() {
    println!("cargo:rerun-if-env-changed=PANTRY_HOST_SCHEMA_RS");
    let source = fs::canonicalize(env::var_os("PANTRY_HOST_SCHEMA_RS").expect("set PANTRY_HOST_SCHEMA_RS to the official host schema.rs")).unwrap();
    println!("cargo:rerun-if-changed={}",source.display());
    let wrapper = format!("#[path = {:?}] mod host_schema;",source.to_string_lossy());
    fs::write(PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("host_schema_module.rs"),wrapper).unwrap();
}
