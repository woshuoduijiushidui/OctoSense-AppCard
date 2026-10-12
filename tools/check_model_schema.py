"""Compile captured requests with the official host's unchanged schema.rs.

This compiles only the schema module, never configures or calls a provider.
The host checkout is supplied explicitly; no workstation paths are committed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

APP = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-schema', type=Path, required=True)
    parser.add_argument('--target-dir', type=Path, default=APP / 'target/model-schema-probe')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('requests', type=Path, nargs='+', help='captured model.complete payloads or schemas')
    args = parser.parse_args()
    source = args.host_schema.resolve(strict=True)
    env = dict(os.environ, PANTRY_HOST_SCHEMA_RS=str(source), CARGO_TARGET_DIR=str(args.target_dir.resolve()))
    command = ['cargo', 'build', '--locked', '--manifest-path', str(APP / 'tools/model_schema_probe/Cargo.toml')]
    if args.offline:
        command.append('--offline')
    subprocess.run(command, env=env, check=True)
    probe = args.target_dir.resolve() / 'debug' / ('pantry-model-schema-probe.exe' if os.name == 'nt' else 'pantry-model-schema-probe')
    subprocess.run([str(probe), *map(str, args.requests)], check=True)
    # A negative control proves the real compiler's keyword policy is exercised.
    with tempfile.TemporaryDirectory(prefix='pantry-schema-') as temp:
        path = Path(temp) / 'unsupported-keyword.json'
        path.write_text(json.dumps(dict(type='array', uniqueItems=True, items=dict(type='integer'))), encoding='utf-8')
        result = subprocess.run([str(probe), str(path)], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 1 or 'uniqueItems' not in result.stderr:
            raise RuntimeError('official compiler negative control did not reject uniqueItems')
    print('PASS official compiler rejects uniqueItems; captured schemas accepted')
    print('Official schema source SHA256:', hashlib.sha256(source.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
