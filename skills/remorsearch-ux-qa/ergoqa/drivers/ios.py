"""Convert an existing XCUITest evidence export to ergo run documents."""
from __future__ import annotations

import hashlib
import json
import plistlib
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

from ..devices import Device, get_device
from ..png import read_header
from ..snapshot import SnapshotError, is_number, load_json, resolve_within, safe_relative_path, sha256_file, validate_run, validate_snapshot

CAPTURE_SCHEMA = "xcuitest-capture.v1"
UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}")
TYPE_VALUE = re.compile(r"XCUIElementType\(rawValue: ([0-9]+)\)")
TYPE_ROLES = {
    2: "application", 3: "group", 4: "window", 7: "alert", 9: "button", 10: "radio",
    12: "checkbox", 14: "button", 15: "combobox", 16: "button", 17: "button", 20: "button",
    21: "navigation", 22: "navigation", 26: "list", 27: "row", 29: "list", 30: "row",
    32: "list", 33: "slider", 35: "progressbar", 36: "progressbar", 38: "combobox",
    39: "spinbutton", 40: "switch", 41: "switch", 42: "link", 43: "img", 45: "searchbox",
    46: "scrollview", 48: "text", 49: "textbox", 50: "textbox", 52: "textbox", 53: "menu",
    58: "document", 73: "grid", 75: "row",
}
INTERACTIVE = {"button", "checkbox", "combobox", "radio", "searchbox", "slider", "switch", "textbox"}


class Capture(NamedTuple):
    doc: dict[str, Any]
    json_path: Path
    png: Path
    json_attachment: dict[str, Any]
    png_attachment: dict[str, Any]


def _err(path: str, message: str) -> None:
    raise SnapshotError(path + ": " + message)


def _obj(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _err(path, "must be an object")
    return value


def _text(obj: dict[str, Any], key: str, path: str, *, empty: bool = False) -> str:
    value = obj.get(key)
    ok = isinstance(value, str) and (empty or value) and len(value) <= 4096
    if not ok:
        _err(path + "." + key, "must be a bounded string")
    return value


def _time(value: Any, path: str) -> datetime:
    if not isinstance(value, str):
        _err(path, "must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SnapshotError(path + ": invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        _err(path, "must include a timezone")
    return parsed


def _epoch(value: Any, path: str) -> datetime:
    if not is_number(value):
        _err(path, "must be a finite timestamp")
    return datetime.fromtimestamp(value, timezone.utc)


def _frame(value: Any, path: str) -> tuple[float, float, float, float]:
    obj = _obj(value, path)
    if set(obj) != {"x", "y", "width", "height"} or not all(is_number(obj[k]) for k in obj):
        _err(path, "must contain four finite numbers")
    if obj["width"] < 0 or obj["height"] < 0:
        _err(path, "width and height must not be negative")
    return float(obj["x"]), float(obj["y"]), float(obj["width"]), float(obj["height"])


def _metadata_value(lines: list[str], key: str) -> str:
    prefix = key + "="
    values = [line[len(prefix):] for line in lines if line.startswith(prefix)]
    if len(values) != 1 or not values[0]:
        _err("metadata.txt", "requires exactly one " + key)
    return values[0]


def _device(evidence: Path, device_id: str) -> tuple[Device, dict[str, Any], dict[str, Any]]:
    catalog = get_device(device_id)
    summary = load_json(resolve_within(evidence, "test-summary.json"))
    results = load_json(resolve_within(evidence, "test-results.json"))
    summary_devices = summary.get("devicesAndConfigurations")
    result_devices = results.get("devices") if isinstance(results, dict) else None
    if not isinstance(summary_devices, list) or len(summary_devices) != 1 or not isinstance(result_devices, list) or len(result_devices) != 1:
        _err("test results", "must identify exactly one device")
    summary_device = _obj(summary_devices[0].get("device"), "test-summary.device")
    actual = _obj(result_devices[0], "test-results.devices[0]")
    for key in ("deviceId", "deviceName", "modelName", "osVersion", "platform"):
        if summary_device.get(key) != actual.get(key):
            _err("test results." + key, "summary and detailed results differ")
    expected_model = catalog.label.removeprefix("Apple ")
    if str(actual.get("modelName", "")).strip().lower() != expected_model.lower():
        _err("test-results.devices[0].modelName", "does not match " + catalog.id + "; nearest-device mapping is not allowed")
    return catalog, summary, actual


def _all_test_cases(node: Any, found: list[dict[str, Any]]) -> None:
    obj = _obj(node, "test node")
    if obj.get("nodeType") == "Test Case":
        found.append(obj)
    children = obj.get("children")
    if isinstance(children, list):
        for child in children:
            _all_test_cases(child, found)


def _test(results: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for node in results.get("testNodes", []):
        _all_test_cases(node, cases)
    if len(cases) != 1:
        _err("test-results.testNodes", "import currently requires exactly one actual test case")
    case = cases[0]
    identifier = case.get("nodeIdentifier")
    if not isinstance(identifier, str) or not identifier:
        _err("test-results.testNodes.nodeIdentifier", "is required")
    raw = case.get("result")
    result = {"Passed": "pass", "Failed": "fail", "Skipped": "skip"}.get(raw)
    if result is None:
        _err("test-results.testNodes.result", "has an unsupported result")
    expected_count = summary.get("failedTests") if result == "fail" else summary.get("skippedTests") if result == "skip" else summary.get("passedTests")
    if expected_count != 1 or summary.get("result") != raw:
        _err("test-summary.json", "counts/result do not bind the single detailed test case")
    return {"identifier": identifier, "name": case.get("name"), "result": result, "raw_result": raw}


def _app_plist(evidence: Path, application_id: str) -> tuple[dict[str, Any], str]:
    matches: list[tuple[dict[str, Any], str]] = []
    for path in evidence.rglob("Info.plist"):
        relative = path.relative_to(evidence).as_posix()
        if not relative.endswith(".app/Info.plist") or not safe_relative_path(relative):
            continue
        resolved = resolve_within(evidence, relative)
        with resolved.open("rb") as stream:
            doc = plistlib.load(stream)
        if doc.get("CFBundleIdentifier") == application_id:
            matches.append((doc, relative))
    if len(matches) != 1:
        _err("application Info.plist", "requires exactly one built app matching " + application_id)
    return matches[0]


def _xcresult_plist(evidence: Path) -> tuple[dict[str, Any], str]:
    matches = list(evidence.glob("*.xcresult/Info.plist"))
    if len(matches) != 1:
        _err("xcresult Info.plist", "requires exactly one result bundle")
    relative = matches[0].relative_to(evidence).as_posix()
    path = resolve_within(evidence, relative)
    with path.open("rb") as stream:
        doc = plistlib.load(stream)
    root_id = _obj(doc.get("rootId"), "xcresult Info.plist.rootId")
    if not isinstance(root_id.get("hash"), str) or not root_id["hash"]:
        _err("xcresult Info.plist.rootId.hash", "is required")
    return doc, relative


def _artifact_hashes(evidence: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in resolve_within(evidence, "artifact-sha256.txt").read_text(encoding="utf-8").splitlines():
        digest, separator, path = line.partition("  ")
        if separator and re.fullmatch(r"[0-9a-f]{64}", digest):
            entries[path] = digest
    if not entries:
        _err("artifact-sha256.txt", "contains no hashes")
    return entries


def _verify_artifact(hashes: dict[str, str], path: Path, label: str) -> None:
    if hashes.get(str(path.resolve())) != sha256_file(path):
        _err(label, "SHA-256 is absent or mismatched in artifact-sha256.txt")


def _elements(value: Any, viewport: tuple[float, float]) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value or len(value) > 4096:
        _err("$.elements", "must be a non-empty array of at most 4096 flattened nodes")
    seen: set[str] = set()
    converted: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        path = f"$.elements[{index}]"
        node = _obj(item, path)
        allowed = {"id", "parent_id", "type", "identifier", "label", "value", "enabled", "frame"}
        if not set(node) <= allowed:
            _err(path, "fields must be exactly " + repr(sorted(allowed)))
        element_id = _text(node, "id", path)
        if element_id != f"xcui-{index + 1}" or element_id in seen:
            _err(path + ".id", "must be sequential and unique")
        seen.add(element_id)
        parent_id = node.get("parent_id")
        if parent_id is not None and (not isinstance(parent_id, str) or parent_id not in seen or parent_id == element_id):
            _err(path + ".parent_id", "must be null or reference an earlier element")
        element_type = _text(node, "type", path)
        type_match = TYPE_VALUE.fullmatch(element_type)
        type_value = int(type_match.group(1)) if type_match else None
        role = TYPE_ROLES.get(type_value, "unknown") if type_value is not None else "unknown"
        identifier = _text(node, "identifier", path, empty=True)
        label = _text(node, "label", path, empty=True)
        value = node.get("value")
        if value is not None and not isinstance(value, str):
            _err(path + ".value", "must be a string or null")
        if not isinstance(node["enabled"], bool):
            _err(path + ".enabled", "must be a boolean")
        x, y, width, height = _frame(node["frame"], path + ".frame")
        converted.append({
            "id": element_id, "role": role, "name": label or identifier, "text": label or None,
            "tag": element_type, "selector": "identifier=" + identifier if identifier else ("label=" + label if label else "type=" + element_type),
            "box": {"x": round(x, 3), "y": round(y, 3), "w": round(width, 3), "h": round(height, 3)},
                "interactive": role in INTERACTIVE, "visible": None, "enabled": node["enabled"],
                "in_viewport": width > 0 and height > 0 and x < viewport[0] and y < viewport[1] and x + width > 0 and y + height > 0,
                "visible_geometry": "unsupported", "visible_box": None,
            "font_size_px": None, "font_weight": None, "color_fg": None, "color_bg": None,
            "border_color": None, "roles": [], "source": "a11y",
            "native": {"xcui_type": element_type, "xcui_type_value": type_value,
                       "identifier": identifier or None, "value": value,
                       "frame_points": node["frame"], "parent_id": parent_id},
        })
    return converted


def _validate_capture(doc: Any, attachments: list[dict[str, Any]], evidence: Path, device: Device,
                      actual_device: dict[str, Any], interval: tuple[datetime, datetime], requested_capture_id: str) -> tuple[Capture, list[dict[str, Any]]]:
    capture = _obj(doc, "$")
    required = {"schema_version", "capture_id", "capture_name", "png_attachment_name", "application_id",
                "application_id_source", "captured_at_start", "captured_at_end", "viewport", "image", "elements"}
    allowed = required | {"image_source"}
    if not required <= set(capture) or set(capture) - allowed or capture.get("schema_version") != CAPTURE_SCHEMA:
        _err("$", "must be exactly " + CAPTURE_SCHEMA + " with the frozen producer fields")
    capture_id = _text(capture, "capture_id", "$")
    if not UUID.fullmatch(capture_id):
        _err("$.capture_id", "must be a UUID")
    if capture_id != requested_capture_id:
        _err("$.capture_id", f"differs from requested capture {requested_capture_id!r}")
    image_source = capture.get("image_source", "application")
    if "image_source" in capture and image_source != "device_screen":
        _err("$.image_source", "must be device_screen, or omitted for an application screenshot")
    _text(capture, "capture_name", "$")
    expected_prefix = "rq-native-" + capture_id
    json_name = expected_prefix + ".json"
    png_name = _text(capture, "png_attachment_name", "$")
    if png_name != expected_prefix + ".png":
        _err("$.png_attachment_name", "must be " + json_name.replace(".json", ".png"))
    def exported_name(item: dict[str, Any], extension: str) -> bool:
        name = str(item.get("suggestedHumanReadableName", ""))
        return bool(re.fullmatch(re.escape(expected_prefix) + r"(?:_[0-9A-Za-z-]+)*\." + extension, name))

    json_attachments = [item for item in attachments if exported_name(item, "json")]
    png_attachments = [item for item in attachments if exported_name(item, "png")]
    if len(json_attachments) != 1 or len(png_attachments) != 1:
        _err("$.capture_id", "JSON and PNG are not uniquely joined in the attachment manifest")
    if _text(capture, "application_id_source", "$") != "test-target-configuration":
        _err("$.application_id_source", "must be test-target-configuration")
    app, _relative = _app_plist(evidence, _text(capture, "application_id", "$"))
    for key in ("CFBundleShortVersionString", "CFBundleVersion"):
        if not isinstance(app.get(key), str) or not app[key]:
            _err("application Info.plist." + key, "is required")
    start = _time(capture.get("captured_at_start"), "$.captured_at_start")
    end = _time(capture.get("captured_at_end"), "$.captured_at_end")
    if end < start or not interval[0] <= start <= end <= interval[1]:
        _err("$.captured_at_end", "capture interval must be ordered and inside the exported test run")
    for item in json_attachments + png_attachments:
        timestamp = _epoch(item.get("timestamp"), "attachment manifest.timestamp")
        if not end <= timestamp <= interval[1]:
            _err("attachment manifest.timestamp", "must follow capture completion inside the test interval")
        for key in ("deviceId", "deviceName"):
            if item.get(key) != actual_device.get(key):
                _err("attachment manifest." + key, "differs from exported device")
    viewport = _frame(capture.get("viewport"), "$.viewport")
    if viewport[:2] != (0.0, 0.0) or viewport[2] <= 0 or viewport[3] <= 0 or viewport[2:] != tuple(device.viewport_css):
        _err("$.viewport", "does not exactly match " + device.id + " point geometry")
    image = _obj(capture.get("image"), "$.image")
    if set(image) != {"width_px", "height_px", "scale"}:
        _err("$.image", "must contain width_px, height_px and scale")
    width, height, scale = image["width_px"], image["height_px"], image["scale"]
    if not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in (width, height)):
        _err("$.image", "pixel dimensions must be positive integers")
    if scale is True or not isinstance(scale, (int, float)) or not is_number(scale) or scale != device.dpr:
        _err("$.image.scale", "must exactly match " + device.id + " DPR")
    if (width, height) != (round(viewport[2] * scale), round(viewport[3] * scale)):
        _err("$.image", "pixel dimensions must equal viewport * scale")
    json_path = resolve_within(evidence / "screenshots", _text(json_attachments[0], "exportedFileName", "attachment manifest"))
    png = resolve_within(evidence / "screenshots", _text(png_attachments[0], "exportedFileName", "attachment manifest"))
    header = read_header(png)
    if (header.width, header.height) != (width, height):
        _err("$.image", "differs from the exported PNG header")
    elements = _elements(capture.get("elements"), viewport[2:])
    capture_record = Capture(capture, json_path, png, json_attachments[0], png_attachments[0])
    return capture_record, elements


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def import_ios_export(evidence: str | Path, out: str | Path, *, device_id: str, capture_id: str,
                      scenario_id: str, profile_id: str, route: str, fixture_id: str,
                      fixture_kind: str) -> dict[str, Any]:
    root = Path(evidence)
    if root.is_symlink() or not root.is_dir():
        _err(str(root), "evidence directory not found or is a symlink")
    if fixture_kind not in {"synthetic_app_data", "runtime_app_data"}:
        _err("fixture_kind", "must be synthetic_app_data or runtime_app_data")
    if not UUID.fullmatch(capture_id):
        _err("capture_id", "must be the producer UUID")
    if not route.startswith("/") or route.endswith("/..") or "/../" in route or "\\" in route:
        _err("route", "must be an explicit safe path route")
    device, summary, actual_device = _device(root, device_id)
    results = load_json(resolve_within(root, "test-results.json"))
    test = _test(results, summary)
    start, end = _epoch(summary.get("startTime"), "test-summary.startTime"), _epoch(summary.get("finishTime"), "test-summary.finishTime")
    if end < start:
        _err("test-summary.finishTime", "must be >= startTime")
    manifest_path = resolve_within(root, "screenshots/manifest.json")
    manifest = load_json(manifest_path)
    if not isinstance(manifest, list):
        _err("screenshots/manifest.json", "must be the xcresult test attachment array")
    test_groups = [item for item in manifest if isinstance(item, dict) and item.get("testIdentifier") == test["identifier"]]
    if len(test_groups) != 1:
        _err("screenshots/manifest.json", "requires exactly one attachment group for the exported test")
    attachments = test_groups[0].get("attachments")
    if not isinstance(attachments, list):
        _err("screenshots/manifest.json", "test attachments must be an array")
    capture_pattern = re.compile("rq-native-" + re.escape(capture_id) + r"(?:_[0-9A-Za-z-]+)*\.json")
    typed_entries = [item for item in attachments if isinstance(item.get("suggestedHumanReadableName"), str)
                     and capture_pattern.fullmatch(item["suggestedHumanReadableName"])]
    if not typed_entries:
        _err("screenshots/manifest.json", f"selected capture {capture_id!r} has no typed JSON attachment")
    if len(typed_entries) != 1:
        _err("screenshots/manifest.json", f"selected capture {capture_id!r} is ambiguous")
    hashes = _artifact_hashes(root)
    _verify_artifact(hashes, manifest_path, "attachment manifest")
    for relative, label in (("test-summary.json", "test summary"), ("test-results.json", "test results"),
                            ("metadata.txt", "run metadata"), ("fixture-origin.txt", "fixture origin")):
        _verify_artifact(hashes, resolve_within(root, relative), label)
    captures: list[tuple[Capture, list[dict[str, Any]]]] = []
    for entry in typed_entries:
        json_path = resolve_within(root / "screenshots", _text(entry, "exportedFileName", "attachment manifest"))
        _verify_artifact(hashes, json_path, "typed capture")
        doc = load_json(json_path)
        captures.append(_validate_capture(doc, attachments, root, device, actual_device, (start, end), capture_id))
    for capture, _ in captures:
        _verify_artifact(hashes, capture.png, "capture PNG")
    captures.sort(key=lambda item: (item[0].doc["captured_at_start"], item[0].doc["capture_id"]))
    app, app_relative = _app_plist(root, captures[0][0].doc["application_id"])
    xcresult, xcresult_relative = _xcresult_plist(root)
    app_path = resolve_within(root, app_relative)
    xcresult_path = resolve_within(root, xcresult_relative)
    _verify_artifact(hashes, app_path, "application Info.plist")
    _verify_artifact(hashes, xcresult_path, "xcresult Info.plist")
    if any(item[0].doc["application_id"] != captures[0][0].doc["application_id"] for item in captures):
        _err("$.application_id", "all captures must target the same app")
    metadata_lines = resolve_within(root, "metadata.txt").read_text(encoding="utf-8").splitlines()
    xcode_version = _metadata_value(metadata_lines, "xcode_version")
    fixture_origin = resolve_within(root, "fixture-origin.txt").read_text(encoding="utf-8").strip()
    if not fixture_origin:
        _err("fixture-origin.txt", "is empty")
    run_identity = "\0".join((test["identifier"], xcresult["rootId"]["hash"], captures[0][0].doc["capture_id"]))
    run_id = "R-ios-" + hashlib.sha256(run_identity.encode()).hexdigest()[:16]
    run_dir = Path(out) / run_id
    if run_dir.exists():
        _err(str(run_dir), "run output already exists")
    started = start.isoformat().replace("+00:00", "Z")
    ended = end.isoformat().replace("+00:00", "Z")
    run_device = {"id": device.id, "viewport_css": list(device.viewport_css), "dpr": device.dpr,
                  "orientation": "portrait" if device.viewport_css[1] >= device.viewport_css[0] else "landscape"}
    run = {"schema_version": "ergo-run.v1", "run_id": run_id, "scenario_id": scenario_id, "profile_id": profile_id,
           "driver": {"name": "XCUITest", "version": xcode_version, "browser": None}, "device": run_device,
           "mode": "scripted", "started_at": started, "ended_at": ended, "status": "completed",
           "success": None, "steps": [],
           "ios_import": {"test": test, "application_plist": app_relative,
                          "application_plist_sha256": sha256_file(resolve_within(root, app_relative)),
                          "bundle_version": app.get("CFBundleShortVersionString"), "build_number": app.get("CFBundleVersion"),
                          "fixture": {"id": fixture_id, "kind": fixture_kind, "origin": fixture_origin, "ref": fixture_id},
                          "device": actual_device, "route": route,
                          "result_bundle": {"id": xcresult["rootId"]["hash"], "info_plist": xcresult_relative,
                                            "info_plist_sha256": sha256_file(xcresult_path)},
                          "selected_capture_only": True,
                          "source_manifest": "screenshots/manifest.json", "source_manifest_sha256": sha256_file(manifest_path)}}
    snapshots = []
    for index, (capture, elements) in enumerate(captures):
        snapshot_id = f"S-{run_id}-{index:03d}"
        shot = capture.doc["image"]
        snapshots.append({"schema_version": "ergo-snapshot.v1", "snapshot_id": snapshot_id, "run_id": run_id,
                          "step_index": index, "captured_at": capture.doc["captured_at_end"],
                          "surface": {"kind": "ios", "url": "ios-app://" + capture.doc["application_id"] + route,
                                      "title": capture.doc["capture_name"], "app_id": capture.doc["application_id"]},
                          "device": run_device,
                          "screenshot": {"path": snapshot_id + ".png", "sha256": sha256_file(capture.png),
                                         "width_px": shot["width_px"], "height_px": shot["height_px"]},
                          "elements": elements, "focus_point": None,
                          "notes": ["geometry: XCUIElement frames measured in app points; signed offscreen coordinates are preserved",
                                    "font, colours, console errors, accessibility order, VoiceOver, intent, action/task outcome, and screenshot receipt were not measured by this importer",
                                    "visible=null means visual visibility is unassessed, not an observed hidden state; xcresult attachment timestamps follow capture completion",
                                    "fixture_kind=" + fixture_kind],
                          "geometry_basis": "measured",
                          "ios_source": {"capture_id": capture.doc["capture_id"], "test_id": test["identifier"],
                                         "json_attachment": capture.json_attachment, "png_attachment": capture.png_attachment,
                                         "image_source": capture.doc.get("image_source", "application"),
                                         "png_sha256": sha256_file(capture.png)}})
    if validate_run(run) or any(validate_snapshot(snapshot) for snapshot in snapshots):
        _err("converted documents", "failed an existing ergo validator")
    run_dir.mkdir(parents=True)
    for index, (capture, _) in enumerate(captures):
        shutil.copyfile(capture.png, run_dir / f"S-{run_id}-{index:03d}.png")
    _write(run_dir / "run.json", run)
    for snapshot in snapshots:
        _write(run_dir / (snapshot["snapshot_id"] + ".json"), snapshot)
    result = {"run_id": run_id, "test_id": test["identifier"], "xcuitest_result": test["result"],
              "captures": [capture.doc["capture_id"] for capture, _ in captures],
              "manifest_sha256": sha256_file(manifest_path)}
    _write(Path(out) / "import.json", result)
    return result
