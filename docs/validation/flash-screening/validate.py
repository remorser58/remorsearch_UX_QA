"""Live check of GM-04 flash screening on small pages in real Chromium.

Serves this folder on a free local port, records each scenario with the web
driver (flash sampling on), evaluates GM-04 for the default Galaxy S24 profile
and prints a table against the expected verdicts.

    python3 docs/validation/flash-screening/validate.py [--repeat N]
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import socketserver
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SKILL = REPO / "skills" / "remorsearch-ux-qa"
sys.path.insert(0, str(SKILL))

from ergoqa import checks  # noqa: E402
from ergoqa.devices import get_device  # noqa: E402
from ergoqa.profiles import sample_profiles  # noqa: E402

EXPECTED = {
    "SC-flash-a-box": "fail",            # (a) 190 x 120 px box, 5 Hz, ~0.0085 sr
    "SC-flash-a2-box-small": "pass",     # same flash, 60 x 60 px (below the area threshold)
    "SC-flash-b-halves": "fail",         # (b) counter-phase halves, constant mean luminance
    "SC-flash-c-red": "fail",            # (c) #ff0000 <-> #7f7f7f full screen, 5 Hz
    "SC-flash-d-wait": "fail",           # (d) flash starts during a wait step
    "SC-flash-e-flicker30": "fail",      # (e) 30 Hz flicker (aliasing without capture jitter)
    "SC-flash-f-scroll-text": "pass",    # high-contrast text scrolling
    "SC-flash-g-static": "pass",         # static page
    "SC-flash-h-feed-scroll": "pass",    # user scrolls a feed
    "SC-flash-j-feed-scroll-inner": "pass",  # the same feed in an app-shell scroll box
    "SC-flash-i-slow": "pass",           # 1 Hz full-screen change
    "SC-flash-k-scroll-shake": "fail",   # page scroll shaking back and forth at 5 Hz over bands
}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:  # noqa: D102
        pass


def serve() -> tuple[socketserver.TCPServer, int]:
    handler = functools.partial(Quiet, directory=str(HERE))
    server =socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def verdict(run: dict) -> tuple[str, dict]:
    device = get_device("galaxy-s24")
    profile = sample_profiles(1, 0, ["galaxy-s24"])[0]
    obs = [o for o in checks.check_run_timing(run, profile, device, {}, None) if o.check_id == "GM-04"]
    if not obs:
        return "no-samples", {}
    m = obs[0].measurement
    return m.get("verdict", "fail" if not obs[0].passed else "pass"), m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--flash-sample-ms", type=int, default=1500)
    args = ap.parse_args()
    server, port = serve()
    rows, ok = [], True
    with tempfile.TemporaryDirectory(prefix="flash-check-") as tmp:
        for sc in sorted((HERE / "scenarios").glob("*.json")):
            sid = json.loads(sc.read_text(encoding="utf-8"))["scenario_id"]
            for rep in range(args.repeat):
                out = Path(tmp) / f"{sid}-{rep}"
                cmd = ["node", str(SKILL / "drivers" / "web" / "ergo_drive.mjs"), "run", "--scenario", str(sc), "--device", "galaxy-s24",
                       "--out", str(out), "--base", f"http://127.0.0.1:{port}", "--flash-sample-ms", str(args.flash_sample_ms),
                       "--run-id", "R-1"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                run = json.loads((out / "R-1" / "run.json").read_text(encoding="utf-8"))
                got, m = verdict(run)
                cov = m.get("coverage", {})
                worst = m.get("general", {}) if m.get("flash_kind") != "red" else m.get("red", {})
                rows.append((sid, rep, proc.returncode, EXPECTED.get(sid), got, m.get("flash_kind"), m.get("value"),
                             worst.get("area_sr"), cov.get("mean_fps"), cov.get("max_gap_ms"), cov.get("sampled_ms")))
                ok &= got == EXPECTED.get(sid)
    server.shutdown()
    print("| scenario | rep | driver exit | expected | verdict | kind | flashes/s | area sr | mean fps | max gap ms | sampled ms |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    print(f"\nall as expected: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
