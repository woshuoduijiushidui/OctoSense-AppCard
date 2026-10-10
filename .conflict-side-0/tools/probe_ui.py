"""Native remote inspection and real capture for a task-owned hidden window."""
import argparse
import http.client
import json
from pathlib import Path
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("route", nargs="?", default="snap")
    parser.add_argument("--param", action="append", default=[])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    params = dict(item.split("=", 1) for item in args.param)
    url = f"http://127.0.0.1:{args.port}/{args.route}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            body = response.read()
    except (http.client.RemoteDisconnected, ConnectionResetError):
        if args.route not in ("quit", "gq"):
            raise
        print("task-owned test window closed")
        return
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(body)
        print(args.out)
    else:
        data = json.loads(body)
        if args.route == "snap":
            data = [w for w in data.get("s", []) if w.get("ty") not in ("Splash", "Window", "KeyboardView")
                    and (w.get("t") or w.get("ty") == "TextInput")]
        print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
