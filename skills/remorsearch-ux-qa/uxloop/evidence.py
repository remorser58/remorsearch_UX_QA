"""Artifact integrity and scoped completion gates; never infer proof from a URL."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

from ergoqa import png

from .contracts import index
from .io import ContractError, GateStop, parse_json, read_artifact, timestamp
from .png_capture import PNGValidationError, validate_png

VISUAL_ASPECTS = ("alignment", "spacing", "typography", "text_clipping",
                  "component_occlusion", "figma_fidelity")
MAX_DIFF_PIXELS = 10_000_000


class Evidence:
    def __init__(self, packet: dict, root: Path):
        self.packet = packet
        self.root = root
        self.artifacts = index(packet["artifacts"])
        self.runs = index(packet["browser_runs"])
        self.scenarios = index(packet["scenarios"])
        self.records = {key: index(value) for key, value in packet["bundle"]["records"].items()}

    def artifact(self, artifact_id: str | None) -> bytes:
        if artifact_id not in self.artifacts:
            raise GateStop("blocked", f"Required artifact is not supplied: {artifact_id}")
        record = self.artifacts[artifact_id]
        if self.packet["mode"] == "live":
            captured = timestamp(record["created_at"])
            current = datetime.now(timezone.utc)
            if captured > current + timedelta(minutes=5) or captured < current - timedelta(days=self.packet["policy"]["retention_days"]):
                raise GateStop("unknown", f"Artifact is future-dated or outside retention/freshness window: {artifact_id}")
        return read_artifact(self.root, record)

    def payload(self, artifact_id: str | None) -> dict:
        raw = self.artifact(artifact_id)
        try:
            value = parse_json(raw)
        except ContractError as exc:
            raise GateStop("unknown", f"Malformed evidence payload {artifact_id}: {exc}") from exc
        if not isinstance(value, dict):
            raise GateStop("unknown", f"Evidence payload must be an object: {artifact_id}")
        return value

    def identity(self, payload: dict, run: dict, kind: str) -> None:
        expected = {"run_id": run["id"], "scenario_digest": run["scenario_digest"],
                    "code_revision": run["code_revision"], "kind": kind}
        if any(payload.get(k) != v for k, v in expected.items()):
            raise GateStop("unknown", f"Cross-run/stale {kind} evidence for {run['id']}")

    def capture_time(self, artifact_id: str, run: dict) -> None:
        at = timestamp(self.artifacts[artifact_id]["created_at"])
        if not timestamp(run["started_at"]) <= at <= timestamp(run["ended_at"]):
            raise GateStop("unknown", f"Capture {artifact_id} is not from run interval {run['id']}")

    def compared_after_inputs(self, check: dict) -> None:
        # A comparison may postdate its run, e.g. a target drawn in Figma after baseline QA,
        # but it cannot precede the capture or reference export it compares.
        compared = timestamp(self.artifacts[check["comparison_artifact_id"]]["created_at"])
        inputs = max(timestamp(self.artifacts[check[key]]["created_at"])
                     for key in ("actual_artifact_id", "reference_artifact_id"))
        if compared < inputs:
            raise GateStop("unknown", f"Comparison {check['comparison_artifact_id']} predates its capture or reference export")

    def research(self) -> None:
        for evidence_id in self.packet["goal"]["evidence_ids"]:
            evidence = self.records["evidence"][evidence_id]
            source = self.records["sources"][evidence["source_id"]]
            if evidence["epistemic_status"] != "observed":
                raise GateStop("unknown", f"Required research evidence is not observed: {evidence_id}")
            if source["retention_status"] in {"withdrawn", "deleted", "redacted"}:
                raise GateStop("unknown", f"Required evidence uses unavailable source: {source['id']}")

    def figma(self, figma_id: str) -> None:
        figma = self.records["figma"][figma_id]
        if figma["design_status"] not in {"comparison_ready", "approved", "implemented"}:
            raise GateStop("blocked", f"Editable Figma baseline is not ready: {figma_id}")
        if figma.get("defect_class") in {"spec_conflict", "design_defect"}:
            raise GateStop("blocked", f"Resolve Figma design/spec decision before implementation: {figma_id}")
        payload = self.payload(figma["readback_artifact_ref"])
        fields = ("file_key", "branch_key", "baseline_version", "readback_version", "node_ids", "read_at")
        if payload.get("editable") is not True or any(payload.get(k) != figma.get(k) for k in fields):
            raise GateStop("unknown", f"Missing/mismatched editable Figma readback: {figma_id}")
        if self.artifacts[figma["readback_artifact_ref"]]["created_at"] != figma["read_at"]:
            raise GateStop("unknown", f"Figma readback timestamp mismatch: {figma_id}")

    def screenshot(self, artifact_id: str, viewport: dict) -> None:
        raw = self.artifact(artifact_id)
        expected = (round(viewport["width"] * viewport["device_scale_factor"]),
                    round(viewport["height"] * viewport["device_scale_factor"]))
        if self.packet["mode"] == "fixture" and raw.lstrip().startswith(b"<svg"):
            try:
                root = ElementTree.fromstring(raw)
                actual = (int(root.attrib["width"]), int(root.attrib["height"]))
                valid = root.attrib.get("data-ux-fixture") == "true"
            except (ElementTree.ParseError, ValueError, KeyError):
                actual, valid = None, False
            if actual != expected or not valid:
                raise GateStop("unknown", f"Malformed synthetic capture: {artifact_id}")
            return
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise GateStop("unknown", f"Live capture must be PNG, not a URL/mock: {artifact_id}")
        try:
            validate_png(raw, expected)
        except PNGValidationError as exc:
            raise GateStop("unknown", f"Corrupt/wrong-size PNG capture: {artifact_id}: {exc}") from exc

    def inspection(self, payload: dict, check: dict) -> None:
        inspection = payload.get("inspection")
        if not isinstance(inspection, dict):
            raise GateStop("unknown", f"Missing image inspection: {check['id']}")
        if inspection.get("viewed_artifact_ids") != [check["actual_artifact_id"], check["reference_artifact_id"]]:
            raise GateStop("unknown", f"Inspection must name the actual and reference artifacts: {check['id']}")
        tool = inspection.get("image_tool")
        if not isinstance(tool, str) or not tool.strip():
            raise GateStop("unknown", f"Inspection requires a host image tool name: {check['id']}")
        observations = inspection.get("observations")
        if not isinstance(observations, list) or not 1 <= len(observations) <= 500:
            raise GateStop("unknown", f"Inspection requires 1-500 regional observations: {check['id']}")
        viewport = check["viewport"]
        width, height = (round(viewport[key] * viewport["device_scale_factor"]) for key in ("width", "height"))
        covered = set()
        for observation in observations:
            if not isinstance(observation, dict) or any(
                not isinstance(observation.get(key), str) or not observation[key].strip()
                for key in ("region", "observed", "expected")
            ):
                raise GateStop("unknown", f"Inspection requires region, observed and expected detail: {check['id']}")
            aspect, status = observation.get("aspect"), observation.get("status")
            if not isinstance(aspect, str) or aspect not in check["checks"]:
                raise GateStop("unknown", f"Unknown inspection aspect: {check['id']}")
            if status not in ("passed", "failed", "unknown", "blocked"):
                raise GateStop("unknown", f"Invalid inspection status: {check['id']}")
            for key in ("actual_box", "reference_box"):
                box = observation.get(key)
                if not isinstance(box, list) or len(box) != 4 or any(type(n) is not int for n in box):
                    raise GateStop("unknown", f"Inspection {key} must be integer [x, y, width, height]: {check['id']}")
                x, y, w, h = box
                if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
                    raise GateStop("unknown", f"Inspection {key} is outside its screenshot: {check['id']}")
            if status != "passed" and "passed" in (check["checks"][aspect], check["status"]):
                raise GateStop(status, f"Visual pass contradicts {aspect} observation: {check['id']}")
            covered.add(aspect)
        if not set(VISUAL_ASPECTS) <= covered:
            raise GateStop("unknown", f"Inspection is missing required aspect coverage: {check['id']}")
        if check["status"] == "passed" and any(value != "passed" for value in check["checks"].values()):
            raise GateStop("unknown", f"Visual pass contradicts aspect checks: {check['id']}")

    def pixel_diff(self, check: dict) -> None:
        tolerance = check.get("tolerance", {"channel_delta": 0, "max_changed_fraction": 0})
        if not isinstance(tolerance, dict):
            raise GateStop("unknown", f"Invalid pixel tolerance: {check['id']}")
        delta, maximum = tolerance.get("channel_delta"), tolerance.get("max_changed_fraction")
        if (type(delta) is not int or not 0 <= delta <= 64
                or type(maximum) not in (int, float) or not 0 <= maximum <= 0.1):
            raise GateStop("unknown", f"Pixel tolerance requires channel_delta 0-64 and max_changed_fraction 0-0.1: {check['id']}")
        try:
            images = []
            for key in ("actual_artifact_id", "reference_artifact_id"):
                raw = self.artifact(check[key])
                image = png.decode(raw, max_pixels=MAX_DIFF_PIXELS)
                # The decoder ignores tRNS on grey/RGB; do not discard that transparency.
                if image.channels in (1, 3) and any(kind == b"tRNS" for kind, _ in png._chunks(raw)):
                    raise png.PNGError("non-palette tRNS transparency is not supported")
                images.append(image)
            actual, reference = images
        except png.PNGError as exc:
            raise GateStop("unknown", f"Pixel comparison unavailable: {check['id']}: {exc}") from exc
        with_alpha = actual.channels in (2, 4) or reference.channels in (2, 4)
        convert = png.to_rgba if with_alpha else png.to_rgb
        actual, reference = convert(actual), convert(reference)
        if (actual.width, actual.height) != (reference.width, reference.height):
            raise GateStop("unknown", f"Pixel comparison dimensions disagree: {check['id']}")
        channels = (abs(a - b) > delta for a, b in zip(actual.data, reference.data))
        if with_alpha:
            changed = sum(r or g or b or a for r, g, b, a in zip(channels, channels, channels, channels))
        else:
            changed = sum(r or g or b for r, g, b in zip(channels, channels, channels))
        fraction = changed / (actual.width * actual.height)
        if fraction > maximum and check["status"] == "passed":
            raise GateStop("failed", f"Pixel comparison changed fraction {fraction:.6f} exceeds {maximum}: {check['id']}")

    def visual(self, run: dict, must_pass: bool) -> None:
        checks = [x for x in self.packet["visual_checks"] if x["run_id"] == run["id"]]
        if not checks:
            raise GateStop("blocked", f"No versioned visual comparison for run {run['id']}")
        for check in checks:
            if check["status"] in {"unknown", "blocked"}:
                raise GateStop(check["status"], f"Visual comparison {check['id']}: {check['reason']}")
            if check["figma_id"] is not None:
                self.figma(check["figma_id"])
            self.screenshot(check["actual_artifact_id"], check["viewport"])
            self.screenshot(check["reference_artifact_id"], check["viewport"])
            self.capture_time(check["actual_artifact_id"], run)
            payload = self.payload(check["comparison_artifact_id"])
            self.compared_after_inputs(check)
            self.identity(payload, run, "visual_report")
            if payload.get("comparison") != check:
                raise GateStop("unknown", f"Visual report disagrees with declared comparison: {check['id']}")
            self.inspection(payload, check)
            if check["method"] == "pixel_diff":
                self.pixel_diff(check)
            if must_pass and check["status"] != "passed":
                raise GateStop("failed", f"Visual comparison failed: {check['id']}: {check['reason']}")

    def browser(self, run_id: str, revision: str, must_pass: bool,
                grants: dict[str, dict], after: str | None = None) -> None:
        run = self.runs[run_id]
        if run["outcome"] in {"unknown", "blocked"}:
            raise GateStop(run["outcome"], f"Browser run {run_id}: {run['reason']}")
        if run["code_revision"] != revision:
            raise GateStop("unknown", f"Browser run {run_id} captured a different scoped code revision")
        if after and self.packet["mode"] == "live" and timestamp(run["started_at"]) < timestamp(after):
            raise GateStop("unknown", f"Replay {run_id} predates the last code change")
        scenario = self.scenarios[run["scenario_id"]]
        for step in scenario["steps"]:
            capability = step["requires"]
            if capability not in grants:
                raise GateStop("blocked", f"Scenario {scenario['id']} requires ungranted {capability}")
            if capability != "read_only" and self.packet["mode"] == "live" and timestamp(grants[capability]["at"]) > timestamp(run["started_at"]):
                raise GateStop("blocked", f"{capability} was not granted before live run {run_id}")
        for kind, artifact_id in run["evidence"].items():
            payload = self.payload(artifact_id)
            self.identity(payload, run, kind)
            self.capture_time(artifact_id, run)
            if not isinstance(payload.get("unexpected_errors"), list):
                raise GateStop("unknown", f"{kind} must explicitly record unexpected_errors")
            if must_pass and payload["unexpected_errors"]:
                raise GateStop("failed", f"Unexpected {kind} errors in replay {run_id}")
        for step in run["steps"]:
            for artifact_id in step["artifact_ids"]:
                payload = self.payload(artifact_id)
                self.identity(payload, run, "steps")
                self.capture_time(artifact_id, run)
                if payload.get("results") != run["steps"]:
                    raise GateStop("unknown", f"Step transcript mismatch for {run_id}")
        for check in run["accessibility"]:
            if check["artifact_id"] is None:
                raise GateStop(check["status"], f"Accessibility {check['name']} has no evidence")
            payload = self.payload(check["artifact_id"])
            self.identity(payload, run, "accessibility")
            self.capture_time(check["artifact_id"], run)
            if payload.get("results") != run["accessibility"]:
                raise GateStop("unknown", f"Accessibility report mismatch for {run_id}")
            if must_pass and check["status"] != "passed":
                raise GateStop(check["status"], f"Accessibility {check['name']} did not pass for {run_id}")
        self.visual(run, must_pass)
        if must_pass and run["outcome"] != "passed":
            raise GateStop("failed", f"Original scenario replay failed: {run_id}")

    def regression(self, replay: dict, revision: str) -> None:
        check = replay["regression"]
        if check["status"] != "passed":
            raise GateStop(check["status"], f"Regression is {check['status']}: {check['detail']}")
        payload = self.payload(check["artifact_id"])
        expected = {"kind": "regression", "replay_id": replay["id"], "code_revision": revision,
                    "run_ids": replay["run_ids"], "scenario_ids": check["scenario_ids"],
                    "status": "passed", "failed_checks": []}
        if check["code_revision"] != revision or any(payload.get(k) != v for k, v in expected.items()):
            raise GateStop("unknown", "Regression receipt is stale, incomplete or contradicts pass")
        capture_at = timestamp(self.artifacts[check["artifact_id"]]["created_at"])
        if capture_at < max(timestamp(self.runs[x]["ended_at"]) for x in replay["run_ids"]):
            raise GateStop("unknown", "Regression report predates its scenario runs")
