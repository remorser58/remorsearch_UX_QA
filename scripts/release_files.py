#!/usr/bin/env python3
"""Print the files a user installs with the skill, and refuse internal notes.

The installed payload is the skills/remorsearch-ux-qa/ tree without what the skill
does not need at run time: the pinned node_modules of the web driver, Python and
editor caches and local run folders. Synthetic driver fixtures are included so
the documented installed quickstart and self-test can actually run.
Each file is printed with its size, followed by a total, so a release note can say
what an install weighs. The script exits 1 when any shipped file matches the
internal-notes denylist (coordination documents, evidence folders, agent state),
because none of those may ever ride along with an install.

Usage: python3 scripts/release_files.py [repository root]
The root argument defaults to the checkout this file lives in; tests use it to
point the same checks at a small fake tree.
"""
from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = Path("skills") / "remorsearch-ux-qa"

# Directory names pruned wherever they appear inside the skill tree: package
# installs, caches, and the scratch run folders the tools write next to the
# checkout (see .gitignore).
PRUNED_DIR_NAMES = frozenset({
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".ux-loop", ".ux-research", ".ergo-bench", ".ergo-runs",
})
PRUNED_FILE_NAMES = frozenset({".DS_Store"})
# Keep the small synthetic fixtures consumed by the shipped driver self-test.
PRUNED_SUBTREES = ()

# Internal documents and folders that must never be shipped. Names match any
# directory part of the path; patterns match the file name; the pair matches a
# directory anywhere below the skill tree.
DENIED_NAMES = ("HANDOFF.md", "COORDINATION.md")
DENIED_DIR_PARTS = frozenset({"_evidence", "_bench", ".omo", ".omc"})
DENIED_DIR_PATHS = (("docs", "handoff"),)
DENIED_FILE_PATTERNS = ("*-PROGRESS.md", "*-REPORT.md")


def release_files(skill_root):
    """(path relative to the repository root, size in bytes) of every installed file, sorted."""
    skill_root = Path(skill_root)
    if skill_root.is_symlink() or not skill_root.is_dir():
        raise ValueError(f"Skill root must be a real directory: {skill_root}")
    if not (skill_root / "SKILL.md").is_file():
        raise ValueError(f"Skill entrypoint is missing: {skill_root / 'SKILL.md'}")
    found = []
    def walk_error(error):
        raise error
    for dirpath, dirnames, filenames in os.walk(str(skill_root), onerror=walk_error):
        relative_dir = Path(dirpath).relative_to(skill_root)
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in PRUNED_DIR_NAMES
            and not any(Path(*relative_dir.parts + (name,)).as_posix() == sub for sub in PRUNED_SUBTREES)
        )
        for name in dirnames:
            if (Path(dirpath) / name).is_symlink():
                raise ValueError(f"Refusing release directory symlink: {Path(dirpath) / name}")
        for name in sorted(filenames):
            if name in PRUNED_FILE_NAMES:
                continue
            path = Path(dirpath) / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Release payload must contain regular files: {path}")
            relative = Path(*relative_dir.parts, name) if relative_dir.parts else Path(name)
            found.append(((SKILL / relative).as_posix(), path.stat().st_size))
    return sorted(found)


def denylist_problems(shipped_path):
    """Why a shipped path (relative to the repository root) may not be shipped; [] when it may."""
    parts = Path(shipped_path).parts
    name = parts[-1]
    problems = []
    if name in DENIED_NAMES:
        problems.append(f"{shipped_path}: internal coordination document")
    if any(fnmatch.fnmatch(name, pattern) for pattern in DENIED_FILE_PATTERNS):
        problems.append(f"{shipped_path}: progress or report note")
    if any(part in DENIED_DIR_PARTS for part in parts):
        problems.append(f"{shipped_path}: internal evidence or agent-state folder")
    if any(pair == parts[i:i + 2] for pair in DENIED_DIR_PATHS for i in range(len(parts) - 1)):
        problems.append(f"{shipped_path}: internal handoff folder")
    return problems


def main(argv=None):
    root = Path(argv[0]) if argv else REPO
    try:
        files = release_files(root / SKILL)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    for path, size in files:
        print(f"{size:>9}  {path}")
    total = sum(size for _, size in files)
    print(f"{len(files)} files, {total} bytes total")
    problems = [problem for path, _ in files for problem in denylist_problems(path)]
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
