#!/usr/bin/env python3
"""Build the self-contained Remorsearch UX QA skill with its search toolkit.

The checked-in toolkit is the default input; maintainers may supply an explicit
local skill instead. Builds use only the standard library, perform no network calls,
and never modify the supplied skill or an installed skills directory. All
generated paths, file inventories and ZIP timestamps are deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
from pathlib import Path, PurePosixPath
import re
import runpy
import shutil
import stat
import sys
import tempfile
import zipfile

import release_files

REPO = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = REPO / release_files.SKILL
OVERLAY = REPO / "integrations" / "insane-search"
SKILL_NAME = "remorsearch-ux-qa"
SEARCH_TARGET = PurePosixPath("references/insane-search")
SEARCH_SOURCE = ENGINE_SOURCE / SEARCH_TARGET
ARCHIVE_NAME = "remorsearch-ux-qa.zip"
MANIFEST = "manifest.remorsearch.json"
SOURCE_COPY = (SEARCH_TARGET / "SOURCE.md").as_posix()
INTEGRATION_VERSION = 2
BASE_PRUNED = release_files.PRUNED_DIR_NAMES | {".git", ".hg", ".svn"}
OVERLAY_FILES = ("scripts/remorsearch.py",)
RESERVED = {MANIFEST, "SOURCE.md", "PROVENANCE.json", "upstream-LICENSE"}
LICENSE_NAME = re.compile(r"^(?:license|licence|copying)(?:[._-].*)?$", re.IGNORECASE)


class BuildError(ValueError):
    pass


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       indent=2, allow_nan=False) + "\n").encode("utf-8")


def helper() -> dict:
    # run_path executes a file without installing or importing a sibling package.
    return runpy.run_path(str(OVERLAY / "scripts" / "remorsearch.py"))


def within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def source_files(root: Path) -> list[Path]:
    """Sorted regular skill files; do not dereference links or carry local state."""
    if not root.is_dir():
        raise BuildError("Source is not a directory: " + str(root))
    result = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        dirs[:] = sorted(name for name in dirs if name not in BASE_PRUNED)
        for name in dirs:
            if (parent / name).is_symlink():
                raise BuildError("Source contains a directory symlink: " + str(parent / name))
        for name in sorted(files):
            if name in release_files.PRUNED_FILE_NAMES:
                continue
            path = parent / name
            if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
                raise BuildError("Source contains a non-regular file: " + str(path))
            relative = path.relative_to(root).as_posix()
            problems = release_files.denylist_problems(relative)
            if problems:
                raise BuildError("; ".join(problems))
            result.append(path)
    return sorted(result)


def validate_search_entrypoint(original: bytes) -> None:
    try:
        text = original.decode("utf-8")
    except UnicodeError as exc:
        raise BuildError("Search entrypoint must be UTF-8") from exc
    if text.startswith("\ufeff"):
        raise BuildError("Search entrypoint must not have a byte-order mark")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError("Search entrypoint must begin with YAML frontmatter")
    closing = next((index for index, line in enumerate(lines[1:], 1)
                    if line.strip() == "---"), None)
    if closing is None:
        raise BuildError("Search entrypoint has unclosed YAML frontmatter")
    front = lines[1:closing]
    names = [line for line in front if re.match(r"^name\s*:", line)]
    if len(names) != 1 or not re.fullmatch(
            r'name\s*:\s*(?:insane-search|"insane-search"|\'insane-search\')\s*(?:#.*)?',
            names[0].strip()):
        raise BuildError("Search toolkit name must be insane-search")
    if len([line for line in front if re.match(r"^description\s*:", line)]) != 1:
        raise BuildError("Search entrypoint must have one description field")


def build_payload(base: Path | None = None) -> tuple[dict[str, bytes], dict]:
    base = (base or SEARCH_SOURCE).expanduser().resolve(strict=True)
    vendored = base == SEARCH_SOURCE.resolve()
    entrypoint = "SOURCE.md" if vendored else "SKILL.md"
    if not (base / entrypoint).is_file():
        raise BuildError("Search input must contain " + entrypoint)
    engine_list = release_files.release_files(ENGINE_SOURCE)
    if not engine_list:
        raise BuildError("The Remorsearch release list is empty")
    payload, origins, base_receipts, engine_receipts = {}, {}, {}, {}

    def add(relative: str, raw: bytes, origin: str) -> None:
        if relative in payload:
            raise BuildError("Payload path collision: " + relative)
        payload[relative] = raw
        origins[relative] = origin

    for path in source_files(base):
        relative = path.relative_to(base).as_posix()
        if vendored and relative in {"PROVENANCE.json", "upstream-LICENSE"}:
            continue
        if relative == entrypoint:
            relative = "SKILL.md"
        elif relative in RESERVED:
            raise BuildError("Search input occupies an integration path: " + relative)
        if path.name == "SKILL.md" and relative != "SKILL.md":
            raise BuildError("Search input contains a nested discoverable SKILL.md: " + relative)
        raw = path.read_bytes()
        base_receipts[relative] = {"sha256": digest(raw), "bytes": len(raw)}
        if relative == "SKILL.md":
            validate_search_entrypoint(raw)
            add(SOURCE_COPY, raw, "toolkit-source")
        else:
            add((SEARCH_TARGET / relative).as_posix(), raw, "toolkit")

    for shipped_path, _ in engine_list:
        problems = release_files.denylist_problems(shipped_path)
        if problems:
            raise BuildError("; ".join(problems))
        source = REPO / shipped_path
        relative = source.relative_to(ENGINE_SOURCE).as_posix()
        if source.is_symlink() or not source.is_file():
            raise BuildError("Remorsearch contains a non-regular file: " + relative)
        if relative.startswith(str(SEARCH_TARGET) + "/"):
            continue  # Explicit inputs replace the toolkit, never the primary skill.
        if source.name == "SKILL.md" and relative != "SKILL.md":
            raise BuildError("Remorsearch contains a nested discoverable SKILL.md: " + relative)
        raw = source.read_bytes()
        engine_receipts[relative] = {"sha256": digest(raw), "bytes": len(raw)}
        add(relative, raw, "remorsearch")

    for relative in OVERLAY_FILES:
        add(relative, (OVERLAY / relative).read_bytes(), "integration")
    if "LICENSE" not in payload:
        add("LICENSE", (REPO / "LICENSE").read_bytes(), "remorsearch-license")
    upstream_license = (OVERLAY / "upstream-LICENSE").read_bytes()
    add((SEARCH_TARGET / "upstream-LICENSE").as_posix(), upstream_license, "upstream-license-reference")
    recorded = json.loads((SEARCH_SOURCE / "PROVENANCE.json").read_text(encoding="utf-8"))
    license_files = sorted(path for path in base_receipts if LICENSE_NAME.fullmatch(Path(path).name))
    source_receipts = {path: receipt for path, receipt in base_receipts.items() if path not in license_files}
    matches_snapshot = source_receipts == recorded["files"]
    license_note = (
        "The supplied toolkit's license files are preserved under its reference directory. "
        "Review those terms before redistributing the artifact."
        if license_files else
        "The supplied toolkit contains no LICENSE, LICENCE or COPYING file. The separately "
        "retained upstream license documents the attributed fivetaku project; this bundle "
        "does not grant or assert redistribution rights for unrelated or modified input."
    )
    provenance = {
        "source_repository": recorded["source_repository"] if matches_snapshot else None,
        "snapshot_date": recorded["snapshot_date"] if matches_snapshot else None,
        "matches_recorded_snapshot": matches_snapshot,
        "files": base_receipts,
        "entrypoint_remap": {"SKILL.md": "SOURCE.md"},
        "upstream_license": recorded["upstream_license"],
        "supplied_license_files": license_files,
        "redistribution_note": license_note,
        "source_note": recorded["source_note"] if matches_snapshot else
            "Explicit maintainer input differs from the recorded upstream-attributed snapshot. "
            "The original bytes and supplied licenses are retained; no upstream license is assigned to it.",
    }
    add((SEARCH_TARGET / "PROVENANCE.json").as_posix(), canonical(provenance), "toolkit-provenance")
    notice = (
        "# Bundle provenance and rights\n\n"
        "Remorsearch UX QA is the only installed skill. Its engine, workflows and discovery "
        "metadata retain their normal paths. The original search toolkit is bundled under "
        "references/insane-search/, with its SKILL.md retained unchanged as SOURCE.md.\n\n"
        + license_note + "\n\n"
        "The separately retrieved fivetaku upstream MIT notice is retained verbatim as "
        "references/insane-search/upstream-LICENSE. PROVENANCE.json records original hashes "
        "and whether the input matches the checked-in attributed snapshot. A match proves "
        "local byte identity, not current upstream authenticity. Review source provenance "
        "before redistribution. Remorsearch code is MIT licensed; see LICENSE and "
        "THIRD_PARTY_NOTICES.md. Its license does not replace the toolkit's terms.\n\n"
        "The search toolkit is reference material invoked during research, after URL discovery "
        "and before capture. Remorsearch access, provenance and privacy controls apply to "
        "every selected method and output. Unsupported outputs remain leads.\n\n"
        "Dependencies, caches and run state are excluded. manifest.remorsearch.json detects "
        "accidental changes; it is not a publisher signature. The offline builder neither "
        "installs nor publishes the skill.\n"
    )
    add("NOTICE.remorsearch.md", notice.encode("utf-8"), "integration-notice")
    # Renaming the entrypoint must keep every original local method link usable.
    for relative, raw in payload.items():
        if not relative.startswith(str(SEARCH_TARGET) + "/") or not relative.endswith(".md"):
            continue
        for link in re.findall(r"\]\(([^)\s]+)\)", raw.decode("utf-8")):
            target = link.split("#", 1)[0]
            if not target.endswith(".md") or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(relative), target))
            if not resolved.startswith(str(SEARCH_TARGET) + "/") or resolved not in payload:
                raise BuildError("Missing or outside search reference: " + relative + " -> " + link)

    files = {path: {"sha256": digest(raw), "bytes": len(raw), "origin": origins[path]}
             for path, raw in sorted(payload.items())}
    shared = helper()
    manifest = {
        "schema_version": shared["SCHEMA_VERSION"],
        "integration_version": INTEGRATION_VERSION,
        "toolkit": {"name": "insane-search", "directory": str(SEARCH_TARGET),
                    "input_sha256": shared["payload_digest"](base_receipts),
                    "files": base_receipts, "license_files": license_files,
                    "matches_recorded_snapshot": matches_snapshot,
                    "redistribution_note": license_note,
                    "entrypoint_remap": {"SKILL.md": "SOURCE.md"}},
        "engine": {"name": SKILL_NAME, "directory": ".", "license": "MIT",
                   "repository": "remorser58/remorsearch_UX_QA",
                   "input_sha256": shared["payload_digest"](engine_receipts),
                   "files": engine_receipts, "entrypoint": "SKILL.md",
                   "agents_metadata": "preserved"},
        "files": files, "payload_sha256": shared["payload_digest"](files),
    }
    payload[MANIFEST] = canonical(manifest)
    return payload, manifest


def write_zip(payload: dict[str, bytes], archive: Path) -> None:
    # Stored members avoid compression-library drift. No host timestamps,
    # absolute paths, directory entries or platform-dependent permissions enter.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as target:
        for relative, raw in sorted(payload.items()):
            info = zipfile.ZipInfo(SKILL_NAME + "/" + relative, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            target.writestr(info, raw)


def build(base: Path | None, output: Path) -> dict:
    try:
        base = (base or SEARCH_SOURCE).expanduser().resolve(strict=True)
    except OSError as exc:
        raise BuildError("Cannot read --base-skill: " + str(exc)) from exc
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise BuildError("--output must be a new directory; existing results are never overwritten")
    resolved_output = output.resolve()
    if within(resolved_output, base) or within(resolved_output, ENGINE_SOURCE.resolve()) or within(resolved_output, OVERLAY.resolve()):
        raise BuildError("--output must be outside the base skill, engine and integration source trees")
    payload, manifest = build_payload(base)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".remorsearch-build-", dir=output.parent))
    try:
        skill = temporary / SKILL_NAME
        for relative, raw in payload.items():
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            path.chmod(0o644)
        write_zip(payload, temporary / ARCHIVE_NAME)
        # Verification precedes publication of the local build directory.
        result = verify_output(temporary)
        if not result["valid"]:
            raise BuildError("Generated bundle failed verification: " + "; ".join(result["problems"]))
        if output.exists() or output.is_symlink():
            raise BuildError("--output appeared during the build; refusing to overwrite it")
        temporary.rename(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {"built": True, "skill_directory": str(output / SKILL_NAME),
            "archive": str(output / ARCHIVE_NAME), "file_count": len(manifest["files"]),
            "payload_sha256": manifest["payload_sha256"]}


def verify_archive(archive: Path, skill: Path) -> list[str]:
    problems = []
    if archive.is_symlink() or not archive.is_file():
        return ["Missing regular archive: " + ARCHIVE_NAME]
    shared = helper()
    try:
        manifest = json.loads((skill / MANIFEST).read_text(encoding="utf-8"),
                              object_pairs_hook=shared["unique_object"])
        paths = [*manifest["files"], MANIFEST]
        if any(not shared["safe_relative"](path) for path in paths):
            raise ValueError("Unsafe manifest path")
        expected = {SKILL_NAME + "/" + path: skill / path for path in paths}
        with zipfile.ZipFile(archive) as source:
            names = source.namelist()
            if len(names) != len(set(names)):
                problems.append("Archive contains duplicate paths")
            for info in source.infolist():
                if not shared["safe_relative"](info.filename):
                    problems.append("Unsafe archive path: " + info.filename)
                    continue
                path = expected.get(info.filename)
                if path is None:
                    problems.append("Unexpected archive member: " + info.filename)
                    continue
                if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                    problems.append("Archive symlink: " + info.filename)
                    continue
                if info.file_size != path.stat().st_size or source.read(info) != path.read_bytes():
                    problems.append("Archive content mismatch: " + info.filename)
            for missing in sorted(set(expected) - set(names)):
                problems.append("Missing archive member: " + missing)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as exc:
        problems.append("Archive verification: " + str(exc))
    return problems


def verify_output(path: Path) -> dict:
    root = path.expanduser().absolute()
    if root.is_symlink():
        return {"valid": False, "problems": ["Verification root must not be a symlink"]}
    is_tree = (root / MANIFEST).exists()
    skill = root if is_tree else root / SKILL_NAME
    result = helper()["verify_bundle"](skill)
    if not is_tree:
        archive_problems = verify_archive(root / ARCHIVE_NAME, skill)
        result["problems"] = sorted(result["problems"] + archive_problems)
        result["valid"] = not result["problems"]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-skill", type=Path, help="Optional maintainer input; defaults to the checked-in search toolkit")
    parser.add_argument("--output", type=Path, help="New output directory for the skill and deterministic ZIP")
    parser.add_argument("--verify", type=Path, help="Verify an output directory or an extracted skill directory")
    args = parser.parse_args(argv)
    if args.verify:
        if args.base_skill or args.output:
            parser.error("--verify cannot be combined with build arguments")
        result = verify_output(args.verify)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
        return 0 if result["valid"] else 1
    if not args.output:
        parser.error("building requires --output")
    try:
        result = build(args.base_skill, args.output)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
        return 0
    except (BuildError, OSError, UnicodeError, ValueError) as exc:
        print("build_insane_search_bundle: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
