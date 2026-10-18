"""Fill explicit bookkeeping sentinels; preflight everything before writing.

The packet/payload dictionaries follow the existing schema, not a second model.
Filled pointers address /packet and /payloads/<artifact id> in the staged input.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import TypeAlias

from .contracts import SCHEMA, validate_packet
from .io import ContractError, atomic_bytes, code_snapshot, digest, load_json, parse_json, safe_relative, sha, within
from .patching import apply_text_patch
from .schema import validate

KINDS = {"console", "network", "runtime", "steps", "accessibility", "visual_report"}
REVISIONS = ("before_revision", "after_revision", "changed_paths")
Json: TypeAlias = str | int | float | bool | None | list["Json"] | dict[str, "Json"]
JsonRecord: TypeAlias = dict[str, Json]


def object_value(value: Json) -> JsonRecord:
    if not isinstance(value, dict):
        raise ContractError("Needed fill value must be an object")
    return value


def array(value: Json) -> list[Json]:
    if not isinstance(value, list):
        raise ContractError("Needed fill value must be an array")
    return value


def text(value: Json) -> str:
    if not isinstance(value, str):
        raise ContractError("Needed fill value must be a string")
    return value


def pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def sentinels(value: Json, path: str = "") -> set[str]:
    if value == "@auto":
        return {path}
    if isinstance(value, dict):
        if "@auto" in value:
            raise ContractError(f"Sentinel cannot be an object key: {path}")
        return set().union(*(sentinels(v, path + "/" + pointer(k)) for k, v in value.items()))
    if isinstance(value, list):
        return set().union(*(sentinels(v, path + "/" + str(i)) for i, v in enumerate(value)))
    return set()


def indexed(value: Json) -> dict[str, JsonRecord]:
    items = [object_value(item) for item in array(value)]
    result = {text(item["id"]): item for item in items}
    if len(result) != len(items):
        raise ContractError("Ambiguous duplicate record id")
    return result


def replace(record: JsonRecord, expected: Mapping[str, Json], path: str) -> list[str]:
    filled = []
    for key, value in expected.items():
        if record.get(key) == "@auto":
            record[key] = value
            filled.append(path + "/" + pointer(key))
    return filled


def safe_path(path: Path) -> Path:
    if ".git" in path.parts or ".." in path.parts:
        raise ContractError(f"Unsafe fill path: {path}")
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ContractError(f"Symlink is not allowed: {path}")
    if any(p.exists() and not p.is_dir() for p in path.parents):
        raise ContractError(f"Fill path traverses a file: {path}")
    return path.resolve()


def stage(packet: JsonRecord, root: Path, workspace: Path | None) -> tuple[dict[Path, bytes], list[str]]:
    """Resolve only marked fields and return all payload writes, without I/O writes."""
    maps = {key: indexed(packet[key]) for key in ("scenarios", "browser_runs", "artifacts", "fixes", "rounds", "visual_checks")}
    records = indexed(object_value(object_value(packet["bundle"])["records"])["runs"])
    fields = {"browser_runs": ("scenario_digest",), "artifacts": ("sha256",), "fixes": REVISIONS}
    allowed = {f"/{group}/{i}/{field}" for group, names in fields.items()
               for i, item in enumerate(maps[group].values()) for field in names
               if group != "fixes" or item["kind"] == "code_write"}
    allowed.update(f"/bundle/records/runs/{i}/{field}" for i in range(len(records))
                   for field in ("scenario_id", "surface_ref"))
    forbidden = sentinels(packet) - allowed
    if forbidden:
        raise ContractError(f"Forbidden packet sentinel: {sorted(forbidden)}")
    schema = load_json(SCHEMA)
    for group, definition in (("scenarios", "scenario"), ("visual_checks", "visual_check")):
        errors = validate(packet[group], {"type": "array", "items": {"$ref": "#/$defs/" + definition}}, schema)
        if errors:
            raise ContractError(f"Malformed fill source: {errors}")
    filled: list[str] = []
    owners: dict[str, set[tuple[str, str, str | None]]] = {}
    for i, run in enumerate(maps["browser_runs"].values()):
        scenario = maps["scenarios"][text(run["scenario_id"])]
        filled.extend(replace(run, {"scenario_digest": digest(scenario)}, f"/packet/browser_runs/{i}"))
        errors = validate(run, {"$ref": "#/$defs/browser_run"}, schema)
        if errors:
            raise ContractError(f"Malformed owning run: {errors}")
        refs = list(object_value(run["evidence"]).items())
        refs += [("steps", a) for step in array(run["steps"]) for a in array(object_value(step)["artifact_ids"])]
        refs += [("accessibility", object_value(check)["artifact_id"]) for check in array(run["accessibility"])]
        for kind, artifact_id in refs:
            if artifact_id is not None:
                if kind not in KINDS or maps["artifacts"][text(artifact_id)]["kind"] != kind:
                    raise ContractError("Artifact kind disagrees with its owner")
                owners.setdefault(text(artifact_id), set()).add((text(run["id"]), kind, None))
    for check in maps["visual_checks"].values():
        artifact_id = check["comparison_artifact_id"]
        if artifact_id is not None:
            if text(check["run_id"]) not in maps["browser_runs"] or maps["artifacts"][text(artifact_id)]["kind"] != "visual_report":
                raise ContractError("Malformed visual report owner")
            owners.setdefault(text(artifact_id), set()).add((text(check["run_id"]), "visual_report", text(check["id"])))
    for i, record in enumerate(records.values()):
        run = maps["browser_runs"][text(record["id"])]
        scenario = maps["scenarios"][text(run["scenario_id"])]
        filled.extend(replace(record, {"scenario_id": run["scenario_id"],
                                      "surface_ref": text(scenario["origin"]).rstrip("/") + text(scenario["route"])},
                              f"/packet/bundle/records/runs/{i}"))
    staged: dict[Path, bytes] = {}
    raw_artifacts: dict[str, bytes] = {}
    paths: set[Path] = set()
    for i, artifact in enumerate(maps["artifacts"].values()):
        path = within(root, text(artifact["path"]))
        if path in paths or (workspace and path.is_relative_to(workspace)):
            raise ContractError("Artifact path collision with evidence or product workspace")
        paths.add(path)
        if not path.is_file() or path.stat().st_size > 32 * 1024 * 1024 or path.stat().st_nlink != 1:
            raise ContractError(f"Missing, oversized or linked artifact: {artifact['id']}")
        raw = path.read_bytes()
        if not raw or (artifact["sha256"] != "@auto" and artifact["sha256"] != sha(raw)):
            raise ContractError(f"Artifact hash/content mismatch: {artifact['id']}")
        if artifact["kind"] not in {"screenshot", "code_patch"}:
            payload = object_value(parse_json(raw))
            expected: JsonRecord = {}
            if artifact["kind"] in KINDS:
                owned = owners.get(text(artifact["id"]), set())
                if len(owned) != 1:
                    raise ContractError(f"Missing/ambiguous artifact owner: {artifact['id']}")
                run_id, kind, check_id = next(iter(owned))
                run = maps["browser_runs"][run_id]
                expected = {"run_id": run_id, "kind": kind, "scenario_digest": run["scenario_digest"],
                            "code_revision": run["code_revision"]}
                if kind in {"steps", "accessibility"}:
                    expected["results"] = run[kind]
                if kind == "visual_report":
                    expected["comparison"] = maps["visual_checks"][text(check_id)]
            marks = sentinels(payload)
            if marks - {"/" + key for key in expected}:
                raise ContractError(f"Forbidden semantic payload sentinel: {artifact['id']}")
            if marks:
                if artifact["sha256"] != "@auto":
                    raise ContractError("Cannot rewrite hash-bound evidence")
                filled.extend(replace(payload, expected, "/payloads/" + pointer(text(artifact["id"]))))
                raw = (json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
                staged[path] = raw
        raw_artifacts[text(artifact["id"])] = raw
        filled.extend(replace(artifact, {"sha256": sha(raw)}, f"/packet/artifacts/{i}"))
    requested = any(fix.get(key) == "@auto" for fix in maps["fixes"].values() for key in REVISIONS)
    if requested and workspace is None:
        raise ContractError("Patch derivation requires --workspace")
    if workspace is not None:
        before = code_snapshot(workspace, [text(name) for name in array(object_value(packet["goal"])["code_paths"])])
        positions = {fix_id: i for i, fix_id in enumerate(maps["fixes"])}
        attempted: set[str] = set()
        for round_ in maps["rounds"].values():
            for value in array(round_["fix_ids"]):
                fix_id = text(value)
                fix = maps["fixes"][fix_id]
                if fix_id in attempted:
                    raise ContractError("Ambiguous repeated fix in declared round order")
                attempted.add(fix_id)
                if fix["kind"] != "code_write":
                    continue
                patch_id = text(fix["patch_artifact_id"])
                if maps["artifacts"][patch_id]["kind"] != "code_patch":
                    raise ContractError("Code fix requires a code_patch artifact")
                after = apply_text_patch(before, raw_artifacts[patch_id].decode("utf-8"))
                expected = {"before_revision": digest(before), "after_revision": digest(after),
                            "changed_paths": list[Json](sorted(k for k in before if before[k] != after[k]))}
                filled.extend(replace(fix, expected, f"/packet/fixes/{positions[fix_id]}"))
                if (fix["before_revision"] != expected["before_revision"] or fix["after_revision"] != expected["after_revision"]
                        or sorted(text(name) for name in array(fix["changed_paths"])) != expected["changed_paths"]):
                    raise ContractError(f"Concrete patch metadata mismatch: {fix_id}")
                before = after
    if sentinels(packet):
        raise ContractError("Unresolved sentinel: missing declared fix ownership")
    return staged, filled


def fill(source: Path, evidence_root: Path, out: Path, *, workspace: Path | None = None) -> dict[str, bool | list[str]]:
    """The four paths are independent CLI boundaries, not a new configuration model."""
    source, root, out = safe_path(source), safe_path(evidence_root), safe_path(out)
    workspace = safe_path(workspace) if workspace is not None else None
    if not root.is_dir() or not out.is_relative_to(root) or out == root or out.exists():
        raise ContractError("Output must be a new file inside the evidence root")
    if ".ux-loop" in out.relative_to(root).parts:
        raise ContractError("Output cannot occupy a checkpoint path")
    if out == source or (workspace and out.is_relative_to(workspace)):
        raise ContractError("Output collides with input or product workspace")
    packet = object_value(load_json(source))
    try:
        for name in array(object_value(packet["goal"])["code_paths"]):
            safe_relative(text(name))
        artifacts = indexed(packet["artifacts"])
        protected = {within(root, text(a["path"])) for a in artifacts.values()}
        if source in protected or out in protected:
            raise ContractError("Input/output collides with an artifact")
        staged, filled = stage(packet, root, workspace)
        errors = validate_packet(packet)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        raise ContractError(f"Malformed needed fill structure: {exc}") from exc
    raw = ((json.dumps(packet, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
           if filled else source.read_bytes())
    # No writes above this line, including serialization and strict validation.
    for path, content in staged.items():
        atomic_bytes(path, content)
    atomic_bytes(out, raw)
    return {"written": [str(path) for path in (*staged, out)], "filled": filled,
            "valid": not errors, "errors": errors}
