//! Local test installation through App Hub's real signature and policy checks.
use octosense_app_hub::{today, PublisherKeys, Store};
use octosense_app_policy::HostLimits;
use std::{collections::BTreeMap, fs, path::PathBuf};

fn main() {
    if let Err(error) = run() {
        eprintln!("local-install: {error}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() != 4 {
        return Err("usage: pantry-local-install <mirror> <app-data> <anchor-public> <publisher-public>".into());
    }
    let mirror = PathBuf::from(&args[0]);
    let data = PathBuf::from(&args[1]);
    let json = fs::read_to_string(mirror.join("catalog.json")).map_err(|e| e.to_string())?;
    // This installer is paired with the full OctoSense shell, which registers
    // the host-api-v1 device consent broker before it admits apps.
    let versions = BTreeMap::from([("app_policy.device_consent".into(), 1)]);
    let mut store = Store::new(&args[2], &data, HostLimits::default()).with_host_api_versions(versions);
    store.accept_catalog(&json)?;
    let entry = store.entry("pantry-steward").ok_or("test catalog has no pantry-steward")?;
    let staged = mirror.join(&entry.artifact);
    let keys = PublisherKeys::default().with("pantry-local-test", &args[3]);
    store.install_staged("pantry-steward", &staged, &keys, &today())?;
    fs::write(data.join("catalog.json"), &json).map_err(|e| e.to_string())?;
    store.may_run("pantry-steward")?;
    println!("installed pantry-steward: signatures, digest and policy verified");
    Ok(())
}
