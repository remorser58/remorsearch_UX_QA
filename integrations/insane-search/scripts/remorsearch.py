#!/usr/bin/env python3
"""Portable command entrypoint for the Remorsearch UX QA release."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

SCHEMA_VERSION = "remorsearch-ux-qa-bundle.v1"
MANIFEST = "manifest.remorsearch.json"
ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT
RUN_DIRECTORIES = (".ux-loop", ".ux-research", ".ergo-bench", ".ergo-runs")
GENERATED_DIRECTORIES = {"drivers/web/node_modules", *RUN_DIRECTORIES}

COMMANDS = {
    "research": "scripts/ux_research.py",
    "ref": "scripts/ref.py",
    "loop": "scripts/ux_loop.py",
    "ergonomics": "scripts/ergo_qa.py",
    "validate": "scripts/validate_bundle.py",
}


def payload_digest(files: dict) -> str:
    raw = json.dumps(files, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return (not path.is_absolute() and ".." not in path.parts
            and path.as_posix() == value and value != ".")


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate manifest key: " + key)
        result[key] = value
    return result


def generated_directory(relative: str) -> bool:
    """Documented dependency, bytecode and run-output directories are not shipped code."""
    return (Path(relative).name == "__pycache__"
            or relative in GENERATED_DIRECTORIES)


def verify_bundle(root: Path) -> dict:
    """Check file content against the packaged inventory, without importing the engine."""
    problems = []
    if root.is_symlink() or not root.is_dir():
        return {"valid": False, "problems": ["Bundle root must be a regular directory"]}
    manifest_path = root / MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        return {"valid": False, "problems": ["Missing regular " + MANIFEST]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Unsupported manifest schema")
        files = manifest.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("Manifest has no file inventory")
        if any(not safe_relative(path) or path == MANIFEST for path in files):
            raise ValueError("Manifest contains an unsafe or self-referencing path")
        if manifest.get("payload_sha256") != payload_digest(files):
            raise ValueError("Manifest inventory digest mismatch")
        for path, receipt in files.items():
            if (not isinstance(receipt, dict)
                    or not isinstance(receipt.get("bytes"), int)
                    or isinstance(receipt.get("bytes"), bool)
                    or receipt["bytes"] < 0
                    or not isinstance(receipt.get("sha256"), str)
                    or len(receipt["sha256"]) != 64
                    or any(char not in "0123456789abcdef" for char in receipt["sha256"])):
                raise ValueError("Malformed file receipt: " + path)
        actual = set()
        def walk_error(error: OSError) -> None:
            problems.append("Unreadable bundle directory: " + str(error.filename))

        for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
            parent = Path(directory)
            for name in dirs[:]:
                child = parent / name
                if child.is_symlink():
                    problems.append("Symlink: " + child.relative_to(root).as_posix())
                    dirs.remove(name)
                elif generated_directory(child.relative_to(root).as_posix()):
                    dirs.remove(name)
            for name in names:
                child = parent / name
                relative = child.relative_to(root).as_posix()
                if child.is_symlink() or not child.is_file():
                    problems.append("Non-regular file: " + relative)
                    continue
                actual.add(relative)
                if relative == MANIFEST:
                    continue
                receipt = files.get(relative)
                if receipt is None:
                    problems.append("Unexpected file: " + relative)
                    continue
                raw = child.read_bytes()
                if len(raw) != receipt["bytes"] or hashlib.sha256(raw).hexdigest() != receipt["sha256"]:
                    problems.append("Changed file: " + relative)
        for missing in sorted(set(files) - actual):
            problems.append("Missing file: " + missing)
        if sorted(path for path in actual if Path(path).name == "SKILL.md") != ["SKILL.md"]:
            problems.append("Bundle must expose exactly one SKILL.md")
        return {"valid": not problems, "file_count": len(files),
                "payload_sha256": manifest["payload_sha256"], "problems": sorted(problems),
                "excluded_runtime_directories": ["**/__pycache__", *sorted(GENERATED_DIRECTORIES)]}
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        return {"valid": False, "problems": ["Manifest verification: " + str(exc)]}


def emit(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


def help_text() -> str:
    return ("Usage: python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py COMMAND [ARGS...]\n"
            "Commands: paths, verify, research, ref, loop, ergonomics, validate, smoke\n"
            "Python 3.10+ on macOS/Linux/WSL. Engine arguments and exit codes are preserved.\n"
            "smoke uses invented fixtures only, without browser or network integration.\n")


def run_engine(script: str, arguments: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    # Keep installed files immutable so ordinary use does not invalidate their inventory.
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(ENGINE / script), *arguments],
                          env=environment, capture_output=capture, text=True)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in {"--help", "-h", "help"}:
        print(help_text(), end="")
        return 0
    command, arguments = args[0], args[1:]
    if command not in {*COMMANDS, "paths", "verify", "smoke"}:
        print("Unknown command: " + command, file=sys.stderr)
        return 2
    if command in {"paths", "verify", "smoke"} and arguments:
        print(command + " does not accept arguments", file=sys.stderr)
        return 2
    verification = verify_bundle(ROOT)
    if command == "verify":
        emit(verification)
        return 0 if verification["valid"] else 1
    if not verification["valid"]:
        emit(verification)
        return 2
    if command == "paths":
        emit({"skill_directory": str(ROOT), "engine_directory": str(ENGINE),
              "entrypoint": str(ROOT / "SKILL.md"),
              "search_directory": str(ROOT / "references/insane-search"),
              "search_source": str(ROOT / "references/insane-search/SOURCE.md"),
              "workflows": {mode: str(ENGINE / "references" / mode / "workflow.md")
                            for mode in ("research", "persona-qa", "ergonomics", "loop")},
              "runtime_required": "Python 3.10+ on macOS/Linux/WSL"})
        return 0
    if sys.version_info < (3, 10):
        print("Python 3.10 or newer is required; found " + sys.version.split()[0], file=sys.stderr)
        return 2
    try:
        if command == "smoke":
            checks = []
            for script in ("examples/research/run_fixture.py", "scripts/smoke_loop.py"):
                result = run_engine(script, [], capture=True)
                checks.append({"script": script, "exit": result.returncode,
                               "stdout": result.stdout, "stderr": result.stderr})
                if result.returncode:
                    emit({"passed": False, "checks": checks,
                          "invented_content": True, "live_integrations_executed": False})
                    return 1
            emit({"passed": True, "checks": checks, "invented_content": True,
                  "live_integrations_executed": False})
            return 0
        return run_engine(COMMANDS[command], arguments).returncode
    except OSError as exc:
        print("Cannot run bundled engine: " + str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
