"""One-command rendered layout scan (`ergo_qa.py scan`).

Records one scroll-through run per device with the bundled web driver (one phone and
one laptop by default), keeps the measured checks only and writes a short candidate
list with an outlined crop for each. A candidate is a measurement to look at, not a
verdict: the reviewer opens the crop and the full screenshot before reporting it, and
dismisses what the pixels do not show.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from . import analyze, png, swarm
from .devices import get_device
from .profiles import _finalise

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "drivers" / "web" / "ergo_drive.mjs"
DEFAULT_DEVICES = ("galaxy-s24", "laptop-1440")
SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
EXAMPLES_PER_GROUP = 3


def is_layout(check_id: str) -> bool:
    """What the scanned screens show (LY) and reflow at 320 px (RF-01). The spacing and
    short-window experiments (RF-02, RF-03) change the page first and are listed with the
    other checks."""
    return check_id.startswith("LY-") or check_id == "RF-01"
EMPTY_TARGETS = {k: [] for k in ("primary", "destructive", "irreversible", "critical_message", "error_message", "status",
                                 "navigation", "ad_like", "hud", "game_control", "timed")}
# Driver warnings that mean a pass did not run, and the checks it would have fed. Their
# candidates are missing from the scan, so the report names them as a gap.
PASS_WARNINGS = (
    (re.compile(r"^reflow (pass (failed|stopped|skipped)|copy of \S+ kept .* not measured|copy failed)|^reflow: \d+ screen"), "RF-01 reflow at 320 px"),
    (re.compile(r"^adaptation (pass failed|pass skipped|copy failed)"), "RF-02 text spacing and RF-03 short window"),
    (re.compile(r"^focus walk \((load|end)\) failed"), "focus walk"),
)


def checks_not_run(warnings: list[str]) -> list[str]:
    """'<checks>: <driver warning>' for every warning that left checks out of the run."""
    out = []
    for warning in warnings:
        for pattern, label in PASS_WARNINGS:
            if isinstance(warning, str) and pattern.search(warning):
                out.append(f"{label}: {warning[:200]}")
                break
    return out[:8]


def default_profile(device_id: str) -> dict[str, Any]:
    """A neutral recorder: 30s, right-handed, normal vision, seated (measured checks ignore it)."""
    device = get_device(device_id)
    touch = device.input == "touch"
    grip = ("two_thumbs" if device.orientation == "landscape" else "one_hand_right") if touch else (
        "mouse_right" if device.input == "mouse" else "keyboard_only")
    profile = {
        "schema_version": "ergo-profile.v1", "profile_id": f"EP-SCAN-{device_id}", "origin": "manual",
        "persona_ref": None, "label_ko": "", "assumption_fields": [], "base_rate_refs": {},
        "attributes": {
            "age_band": "30s", "handedness": "right", "grip": grip, "thumb_length_mm": 0, "hand_percentile": 50,
            "device_id": device_id, "orientation": device.orientation,
            "vision": {"acuity": "normal", "presbyopia": False, "cvd": "none", "cvd_severity": 1.0, "viewing_distance_mm": 0},
            "motor": {"tremor": "none", "touch_sigma_multiplier": 1.0, "touch_sigma_mm": 0.0},
            "context": {"mobility": "seated", "lighting": "indoor", "free_hands": 1 if touch else 2, "interruptions": False},
            "cognition": {"familiarity": "returning", "time_pressure": "low", "reading_wpm_ko": 0},
            "reaction_time_ms": 0,
        },
    }
    return _finalise(profile, device)


def driver_fix(stderr: str) -> str | None:
    """The one-time command that prepares the browser driver, when a run failed for want of
    it. A plugin copy or a copied skill folder skips the installer's driver setup."""
    web = DRIVER.parent
    if "cannot load the playwright package" in stderr or "Executable doesn't exist" in stderr:
        return f"prepare the browser driver once: (cd {web} && npm ci && npx playwright install chromium)"
    if "missing dependencies" in stderr or "error while loading shared libraries" in stderr:
        try:
            version = json.loads((web / "package.json").read_text(encoding="utf-8"))["dependencies"]["playwright"]
        except (OSError, ValueError, KeyError):
            version = "1.56.1"
        return f"install Chromium's system libraries once: npx -y playwright@{version} install-deps chromium"
    return None


def scenario_for(url: str, device_id: str, tiles: int) -> dict[str, Any]:
    """Top of the page, overlapping screens of 80 % height, then the very end (End key).

    The driver captures the screen before the first action and after every scroll or key
    press, so the steps need no separate snapshot actions.
    """
    height = get_device(device_id).viewport_css[1]
    steps: list[dict[str, Any]] = [{"action": "scroll", "dy": round(height * 0.8)} for _ in range(tiles)]
    steps.append({"action": "press", "key": "End"})
    return {"schema_version": "ergo-scenario.v1", "scenario_id": f"SCAN-{device_id}", "surface": {"kind": "web", "url": url},
            "task_goal_ko": "화면을 위에서 끝까지 읽는다", "device_ids": [device_id], "targets": dict(EMPTY_TARGETS), "steps": steps}


def _crop(image: png.Image, x: int, y: int, w: int, h: int) -> png.Image:
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(image.width, x + w), min(image.height, y + h)
    rows = [image.data[(row * image.width + x0) * image.channels:(row * image.width + x1) * image.channels] for row in range(y0, y1)]
    return png.make_image(x1 - x0, y1 - y0, image.channels, b"".join(rows))


def _box_for(observation: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, float] | None:
    ids = set(observation.get("element_ids") or [])
    for element in snapshot.get("elements", []):
        if element.get("id") in ids and isinstance(element.get("box"), dict):
            return element["box"]
    anchors = set((observation.get("extra") or {}).get("anchor_selectors") or [])
    for outlier in snapshot.get("layout_outliers") or []:
        if anchors & set(outlier.get("selectors") or []):
            return outlier.get("box")
    return None


def _cached(cache: dict[Path, Any] | None, key: Path, load: Any) -> Any:
    if cache is None:
        return load()
    if key not in cache:
        cache[key] = load()
    return cache[key]


def write_crop(run_dir: Path, observation: dict[str, Any], target: Path, margin: int = 24,
               cache: dict[Path, Any] | None = None) -> str | None:
    """Save the region around the element with the element outlined. The cache keeps decoded
    screenshots and snapshots between crops of one scan (decoding is the slow part)."""
    snapshot_path = run_dir / f"{observation.get('snapshot_id')}.json"
    if not snapshot_path.is_file():
        return None
    snapshot = _cached(cache, snapshot_path, lambda: json.loads(snapshot_path.read_text(encoding="utf-8")))
    box = _box_for(observation, snapshot)
    shot = snapshot.get("screenshot") or {}
    if not box or not shot.get("path"):
        return None
    shot_path = run_dir / shot["path"]
    image = _cached(cache, shot_path, lambda: png.read_png(shot_path))
    viewport = (snapshot.get("device") or {}).get("viewport_css") or [image.width, image.height]
    scale = image.width / max(1, viewport[0])
    x, y, w, h = (int(round(v * scale)) for v in (box["x"], box["y"], box["w"], box["h"]))
    pad = int(margin * scale)
    x0, y0 = max(0, x - pad), max(0, y - pad)
    if x0 >= min(image.width, x + w + pad) or y0 >= min(image.height, y + h + pad):
        return None  # the box lies outside the screenshot
    region = _crop(image, x - pad, y - pad, w + 2 * pad, h + 2 * pad)
    png.write_png(target, png.draw_rect(region, x - 2 - x0, y - 2 - y0, w + 4, h + 4, (230, 30, 30), thickness=max(2, int(scale))))
    return str(target)


def group_key(candidate: dict[str, Any]) -> str:
    """Candidates with one cause share a key: one contrast pair, one covering box. Other
    layout candidates stand alone; other checks group by check."""
    check, m = candidate["check_id"], candidate.get("measurement") or {}
    if check == "PC-01":
        return f"{check}|{m.get('fg')}|{m.get('bg')}"
    if check == "LY-02" and m.get("covered_by"):
        return f"{check}|{m['covered_by']}"
    if is_layout(check):
        return f"{check}|{candidate['element']}"
    return check


def run_scan(url: str, out: Path, devices: tuple[str, ...] = DEFAULT_DEVICES, tiles: int = 8, node: str = "node",
             timeout: int = 900, allow_origins: tuple[str, ...] = ()) -> dict[str, Any]:
    out = Path(out)
    runs, crops = out / "runs", out / "crops"
    crops.mkdir(parents=True, exist_ok=True)
    analyses: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    run_dirs: dict[str, Path] = {}
    # The devices record at the same time, each in its own browser: the scan takes about
    # as long as its slowest device.
    started = time.time()
    jobs = []
    for device_id in devices:
        profile = default_profile(device_id)
        scenario = scenario_for(url, device_id, tiles)
        scenario_path = out / "scenarios" / f"{scenario['scenario_id']}.json"
        profile_path = out / "profiles" / f"{device_id}.json"
        for path, doc in ((scenario_path, scenario), (profile_path, profile)):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        run_id = f"SCAN-{device_id}"
        command = [node, str(DRIVER), "run", "--scenario", str(scenario_path), "--profile", str(profile_path),
                   "--out", str(runs), "--run-id", run_id, "--continue-on-error"]
        for origin in allow_origins:
            command += ["--allow-origin", origin]
        log = out / f"driver-{device_id}.log"
        handle = log.open("w", encoding="utf-8")
        jobs.append((device_id, profile, scenario, run_id, log, handle,
                     subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT, text=True)))
    finished: dict[str, tuple[int, float]] = {}
    for device_id, *_, handle, proc in jobs:
        try:
            code = proc.wait(timeout=max(1, timeout - (time.time() - started)))
        except subprocess.TimeoutExpired:
            proc.kill()
            code = proc.wait()
        handle.close()
        finished[device_id] = (code, time.time() - started)
    for device_id, profile, scenario, run_id, log, _, _ in jobs:
        code, seconds = finished[device_id]
        driver_output = log.read_text(encoding="utf-8", errors="replace")
        run_dir = runs / run_id
        run_doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8")) if (run_dir / "run.json").is_file() else {}
        entry = {"device": device_id, "seconds": round(seconds, 1),
                 "recorded": bool(run_doc) and run_doc.get("status") != "blocked"}
        if not entry["recorded"]:
            entry["driver_exit"] = code
            # A run that never reached the page (refused connection, blocked navigation)
            # is a coverage gap, never an empty result. The first line of the driver's error
            # names the cause; the stack below it does not.
            stderr = driver_output
            first = next((line.strip() for line in stderr.splitlines() if line.strip()), "")
            entry["error"] = "; ".join(run_doc.get("blocked_reasons") or []) or first[:300] or stderr[-600:]
            fix = driver_fix(stderr)
            if fix:
                entry["fix"] = fix
            coverage.append(entry)
            continue
        profiles.append(profile)
        run_dirs[run_id] = run_dir
        result = analyze.analyze_run(run_dir, [profile], scenario, cross_profile=True, gaze_enabled=False)
        result["observations"] = [o for o in result["observations"] if o.get("basis") == "measured"]
        analyses.append(result)
        # The driver loads only the page's own origin unless told otherwise: blocked fonts,
        # styles or images change the layout, so the count is part of the coverage.
        policy = (run_doc.get("driver") or {}).get("network_policy") or {}
        entry["blocked_requests"] = policy.get("blocked_requests") or 0
        origins = []
        for item in policy.get("blocked_sample") or []:
            url_text = item.get("url") if isinstance(item, dict) else item
            if isinstance(url_text, str) and "://" in url_text:
                origin = "/".join(url_text.split("/", 3)[:3])
                if origin not in origins:
                    origins.append(origin)
        entry["blocked_origins"] = origins[:5]
        entry["checks_not_run"] = checks_not_run(run_doc.get("warnings") or [])
        scrolls = []
        for snap_path in sorted(run_dir.glob("*.json")):
            if snap_path.name == "run.json":
                continue
            doc = json.loads(snap_path.read_text(encoding="utf-8"))
            sc = (doc.get("surface") or {}).get("scroll") or {}
            if doc.get("device", {}).get("probe") != "adaptation" and isinstance(sc.get("y"), (int, float)):
                scrolls.append((sc["y"], sc.get("height")))
        if scrolls:
            height = max((h for _, h in scrolls if isinstance(h, (int, float))), default=None)
            screen = get_device(device_id).viewport_css[1]
            seen, gaps, edge = sorted({y for y, _ in scrolls}), [], 0.0
            for y in seen:
                if y > edge + 1:
                    gaps.append([round(edge), round(y)])
                edge = max(edge, y + screen)
            if isinstance(height, (int, float)) and height > edge + 1:
                gaps.append([round(edge), round(height)])
            entry.update({"screens": len(scrolls), "page_height_css": height, "deepest_scroll_css": max(seen),
                          "uncaptured_css": gaps})
        coverage.append(entry)
    findings = swarm.aggregate(analyses, profiles) if analyses else []
    observations = {o["id"]: (o, run_dirs.get(o["run_id"])) for a in analyses for o in a["observations"]}
    # One row per check and element: the same cut chip on the phone and the laptop is
    # one candidate seen on two devices, with the first device's crop.
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for finding in findings:
        row = merged.setdefault((finding["check_id"], finding["element_key"]), {**finding, "run_ids": [], "observation_ids": []})
        row["run_ids"] = sorted(set(row["run_ids"]) | set(finding.get("run_ids", [])))
        row["observation_ids"] = row["observation_ids"] + list(finding.get("observation_ids", []))
        if SEVERITY_RANK.get(finding.get("severity"), 4) < SEVERITY_RANK.get(row.get("severity"), 4):
            row["severity"] = finding.get("severity")
    candidates, sources = [], {}
    order = lambda f: (not is_layout(f["check_id"]), SEVERITY_RANK.get(f.get("severity"), 4), f["check_id"], f["element_key"])
    for n, finding in enumerate(sorted(merged.values(), key=order), 1):
        sources[n] = next((observations[i] for i in finding.get("observation_ids", []) if i in observations), (None, None))
        obs = sources[n][0]
        candidates.append({
            "n": n, "check_id": finding["check_id"], "severity": finding.get("severity"), "title_ko": finding.get("title_ko"),
            "devices": sorted({run_id.removeprefix("SCAN-") for run_id in finding.get("run_ids", [])}),
            "element": finding["element_key"], "selectors": finding.get("selectors") or [],
            "summary_ko": finding.get("summary_ko"), "measurement": finding.get("measurement"),
            "snapshot": obs.get("snapshot_id") if obs else None, "crop": None,
        })
    # Text cut by the screen edge on a device whose page is wider than the screen is one
    # defect, the page width (LY-08), whatever the number of cut texts.
    wide = {d for c in candidates if (c.get("measurement") or {}).get("name") == "page_overflow" for d in c["devices"]}
    for c in candidates:
        if c["check_id"] == "LY-01" and (c.get("measurement") or {}).get("clipped_by") == "viewport" and set(c["devices"]) <= wide:
            c["part_of"] = "LY-08 page_overflow"
    groups: dict[str, list[dict[str, Any]]] = {}
    for c in candidates:
        if not c.get("part_of"):
            c["group"] = group_key(c)
            groups.setdefault(c["group"], []).append(c)
    cache: dict[Path, Any] = {}
    for members in groups.values():
        for c in members[:EXAMPLES_PER_GROUP]:
            obs, run_dir = sources[c["n"]]
            if obs and run_dir:
                try:
                    c["crop"] = write_crop(run_dir, obs, crops / f"{c['n']:02d}-{c['check_id']}.png", cache=cache)
                except (OSError, ValueError, png.PNGError):
                    c["crop"] = None
    result = {"schema_version": "ergo-scan.v1", "url": url, "devices": list(devices), "coverage": coverage,
              "candidates": candidates, "status": "candidates_need_visual_confirmation"}
    (out / "scan.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "scan.md").write_text(render_markdown(result), encoding="utf-8")
    return result


def _slug(url: str) -> str:
    path = re.sub(r"[?#].*$", "", url).rstrip("/")
    parts = [p for p in path.split("/") if p and ":" not in p][-2:]
    return re.sub(r"[^A-Za-z0-9._-]+", "-", "-".join(parts))[:48].strip("-.") or "page"


def run_many(urls: list[str], out: Path, devices: tuple[str, ...] = DEFAULT_DEVICES, tiles: int = 8, node: str = "node",
             timeout: int = 900, allow_origins: tuple[str, ...] = (), jobs: int = 3) -> list[dict[str, Any]]:
    """Scan several pages, a few at a time, each into its own folder, and write one scan.md
    that lists every page's layout rows. Each page keeps its full scan.md and scan.json."""
    from concurrent.futures import ThreadPoolExecutor

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    folders = [out / f"{n:02d}-{_slug(url)}" for n, url in enumerate(urls, 1)]
    def one(pair: tuple[str, Path]) -> dict[str, Any]:
        try:
            return run_scan(pair[0], pair[1], devices=devices, tiles=tiles, node=node, timeout=timeout, allow_origins=allow_origins)
        except Exception as exc:  # one broken page must not stop the others; it is a coverage gap
            return {"url": pair[0], "candidates": [], "coverage": [{"device": ", ".join(devices), "recorded": False, "driver_exit": None,
                                                                    "error": f"{type(exc).__name__}: {exc}"[:300]}]}

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        results = list(pool.map(one, zip(urls, folders)))
    pages = []
    lines = ["# Layout scan: " + str(len(urls)) + " pages", "",
             "Each page's layout rows follow; its full scan.md (other checks by cause) and screenshots are in its folder.", ""]
    for folder, result in zip(folders, results):
        layout = [c for c in result["candidates"] if not c.get("part_of") and is_layout(c["check_id"])]
        recorded = all(c.get("recorded") for c in result["coverage"])
        pages.append({"url": result["url"], "folder": folder.name, "recorded": recorded, "candidates": len(result["candidates"]),
                      "layout_rows": len({c.get("group") for c in layout})})
        page_md = render_markdown(result, crop_prefix=folder.name + "/crops/", layout_only=True)
        lines += ["## " + folder.name + ": " + result["url"], ""] + page_md.split("\n", 2)[2:] + [""]
    (out / "scan.json").write_text(json.dumps({"schema_version": "ergo-scan-set.v1", "pages": pages}, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "scan.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return pages


def render_markdown(result: dict[str, Any], crop_prefix: str = "", layout_only: bool = False) -> str:
    lines = [f"# Layout scan: {result['url']}", "",
             "Measured candidates. Open each crop and the full screenshot before reporting one; dismiss what the pixels do not show.", ""]
    for c in result["coverage"]:
        if not c.get("recorded"):
            lines.append(f"- {c['device']}: not recorded (driver exit {c['driver_exit']}): {c.get('error', '')[:300]}"
                         + (f" To fix: {c['fix']}." if c.get("fix") else ""))
        else:
            lines.append(f"- {c['device']}: {c.get('screens', 0)} screens, page height {c.get('page_height_css')} CSS px, "
                         f"deepest scroll {c.get('deepest_scroll_css')} CSS px, {c['seconds']} s.")
            if c.get("uncaptured_css"):
                spans = ", ".join(f"{a}-{b}" for a, b in c["uncaptured_css"])
                lines.append(f"  Not captured: {spans} CSS px from the top; rerun with a larger --tiles.")
            if c.get("blocked_requests"):
                if str(result.get("url", "")).startswith("file:"):
                    lines.append(f"  Blocked {c['blocked_requests']} requests for frames or documents outside the page's folder "
                                 "(see run.json); serve the folder over http if the page needs them.")
                else:
                    lines.append(f"  Blocked {c['blocked_requests']} requests to other origins ("
                                 f"{', '.join(c.get('blocked_origins') or []) or 'see run.json'}); fonts, styles or images may be missing. "
                                 "Pass --allow-origin for origins the page needs.")
            for item in c.get("checks_not_run") or []:
                lines.append(f"  Did not run: {item}. Its candidates are missing from this scan.")
    rows = [c for c in result["candidates"] if not c.get("part_of")]
    layout = [c for c in rows if is_layout(c["check_id"])]
    other = [c for c in rows if not is_layout(c["check_id"])]
    folded = sum(1 for c in result["candidates"] if c.get("part_of"))

    def label(c: dict[str, Any]) -> str:
        element = c["element"].split("|", 1)
        return (element[0] + (f" ({element[1]})" if len(element) > 1 and element[1] else "")).replace("|", "/")

    def summary(c: dict[str, Any]) -> str:
        return (c.get("summary_ko") or c.get("title_ko") or "").replace("|", "/").replace("\n", " ")

    lines += ["", f"## Layout ({len(layout)})", "",
              "Confirm each row on its crop and the screenshot around it."
              + (f" {folded} texts cut by the screen edge are part of the page-width row (LY-08) and are not listed." if folded else ""),
              "", "| # | Severity | Check | Device | Element | What was measured | Crop |", "| --- | --- | --- | --- | --- | --- | --- |"]
    shown: set[Any] = set()
    for c in layout:
        if c.get("group") in shown:
            continue
        shown.add(c.get("group"))
        same = [m for m in layout if m.get("group") == c.get("group")] if c.get("group") else [c]
        more = f" ({len(same) - 1} more with the same cause: {', '.join(str(m['n']) for m in same[1:6])})" if len(same) > 1 else ""
        crop = crop_prefix + Path(c["crop"]).name if c.get("crop") else "-"
        lines.append(f"| {c['n']} | {c['severity']} | {c['check_id']} | {', '.join(c['devices'])} | {label(c)} | {summary(c)}{more} | {crop} |")
    if not layout:
        lines.append("| - | - | - | - | - | No measured layout candidate. The page still needs a visual pass. | - |")
    if other and layout_only:
        lines += ["", f"Other measured checks: {len({c.get('group') or c['check_id'] for c in other})} causes in this page's scan.md."]
    elif other:
        lines += ["", f"## Other measured checks ({len(other)}, grouped by cause)", "",
                  "One row per cause with up to three examples; scan.json lists every element.", "",
                  "| Check | Severity | Count | Device | Examples | What was measured | Crops |", "| --- | --- | --- | --- | --- | --- | --- |"]
        by_cause: dict[str, list[dict[str, Any]]] = {}
        for c in other:
            by_cause.setdefault(c.get("group") or c["check_id"], []).append(c)
        for members in sorted(by_cause.values(), key=lambda ms: (min(SEVERITY_RANK.get(m.get("severity"), 4) for m in ms), ms[0]["check_id"], -len(ms))):
            first = members[0]
            worst = min((m.get("severity") for m in members), key=lambda v: SEVERITY_RANK.get(v, 4))
            devices = sorted({d for m in members for d in m["devices"]})
            examples = "; ".join(f"{m['n']} {label(m)[:60]}" for m in members[:EXAMPLES_PER_GROUP])
            crops = ", ".join(Path(m["crop"]).name for m in members[:EXAMPLES_PER_GROUP] if m.get("crop")) or "-"
            lines.append(f"| {first['check_id']} | {worst} | {len(members)} | {', '.join(devices)} | {examples} | {summary(first)} | {crops} |")
    return "\n".join(lines) + "\n"

