#!/usr/bin/env python3
"""Find existing supported runtimes without installing anything (Python 3.9+)."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Final, Optional, TypedDict

PYTHON_NAMES: Final = ("python3",) + tuple("python3." + str(n) for n in range(10, 21))
SYSTEM_BINS: Final = (
    Path("/usr/bin"), Path("/usr/local/bin"), Path("/opt/homebrew/bin"),
    Path("/usr/local/opt/node@22/bin"), Path("/opt/homebrew/opt/node@22/bin"),
)
LAYOUTS: Final = (
    ("python", ".local/bin"),
    ("python", ".local/share/uv/python/*/bin"),
    ("python", ".pyenv/versions/*/bin"),
    ("python", ".local/share/mise/installs/python/*/bin"),
    ("python", ".asdf/installs/python/*/bin"),
    ("node22", ".local/bin"),
    ("node22", ".nvm/versions/node/v22*/bin"),
    ("node22", ".volta/bin"),
    ("node22", ".volta/tools/image/node/22*/bin"),
    ("node22", ".fnm/node-versions/v22*/installation/bin"),
    ("node22", ".local/share/fnm/node-versions/v22*/installation/bin"),
    ("node22", ".local/share/mise/installs/node/22*/bin"),
    ("node22", ".asdf/installs/nodejs/22*/bin"),
)


@dataclass(frozen=True)
class Search:
    """Candidate roots are injectable so tests never search the user's HOME."""

    home: Path
    path: tuple[Path, ...]
    system_bins: tuple[Path, ...] = SYSTEM_BINS
    timeout: float = 1.0


class Runtime(TypedDict):
    path: str
    version: str


class Check(TypedDict, total=False):
    runtime: str
    path: str
    status: str
    version: str
    output: str
    returncode: int


class Gap(TypedDict):
    runtime: str
    required: bool
    reason: str


class Report(TypedDict):
    python: Optional[Runtime]
    node22: Optional[Runtime]
    checked: list[Check]
    gaps: list[Gap]


def discover(search: Search) -> Report:
    """Probe shallow trusted layouts; choose version descending, path ascending."""
    checked: list[Check] = []
    gaps: list[Gap] = []
    directories: list[tuple[str, Path, bool]] = []
    for directory in search.path[:32]:
        directories.extend((kind, directory, True) for kind in ("python", "node22"))
    for directory in search.system_bins:
        directories.extend((kind, directory, False) for kind in ("python", "node22"))
    for kind, pattern in LAYOUTS:
        directories.extend((kind, directory, False) for directory in
                           sorted(search.home.glob(pattern))[:64])
    for directory in search.system_bins:
        if directory == Path("/usr/local/bin") or directory == Path("/opt/homebrew/bin"):
            directories.extend(("python", path, False) for path in
                               sorted(directory.parent.glob("opt/python@3.*/bin"))[:64])

    selected: dict[str, list[tuple[tuple[int, int, int], str, Runtime]]] = {
        "python": [], "node22": []}
    seen: set[tuple[str, Path]] = set()
    workspace = Path.cwd().resolve()
    count = 0
    for kind, directory, from_path in directories:
        # PATH's relative entries and target-workspace binaries are not trusted installs.
        if not directory.is_absolute():
            continue
        names = PYTHON_NAMES if kind == "python" else ("node", "node22")
        for name in names:
            candidate = directory / name
            if not candidate.is_file():
                continue
            path = candidate.resolve()
            if (from_path and path.is_relative_to(workspace)) or (kind, path) in seen:
                continue
            seen.add((kind, path))
            if count >= 512:
                gaps.append({"runtime": "discovery", "required": False,
                             "reason": "Candidate limit (512) reached"})
                break
            count += 1
            fact: Check = {"runtime": kind, "path": str(path)}
            checked.append(fact)
            try:
                result = subprocess.run(
                    [str(path), "--version"], capture_output=True, text=True, errors="replace",
                    timeout=search.timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            except subprocess.TimeoutExpired:
                fact["status"] = "timeout"
                continue
            except OSError as error:
                fact.update(status="unavailable", output=str(error))
                continue
            output = (result.stdout.strip() or result.stderr.strip())
            fact.update(returncode=result.returncode, output=output)
            if result.returncode != 0:
                fact["status"] = "failed"
                continue
            pattern = r"Python (\d+)\.(\d+)\.(\d+)" if kind == "python" else r"v(\d+)\.(\d+)\.(\d+)"
            match = re.fullmatch(pattern, output)
            if match is None:
                fact["status"] = "invalid-version"
                continue
            major, minor, patch = (int(part) for part in match.groups())
            version = ".".join(match.groups())
            supported = (major == 3 and minor >= 10) if kind == "python" else major == 22
            fact.update(version=version, status="supported" if supported else "unsupported")
            if supported:
                selected[kind].append(((major, minor, patch), str(path),
                                       {"path": str(path), "version": version}))
        if count >= 512:
            break

    choices: dict[str, Optional[Runtime]] = {}
    for kind in ("python", "node22"):
        ordered = sorted(selected[kind], key=lambda item: (
            tuple(-component for component in item[0]), item[1]))
        choices[kind] = ordered[0][2] if ordered else None
        if not ordered:
            gaps.append({
                "runtime": kind, "required": kind == "python",
                "reason": ("No Python >=3.10 found in bounded install locations"
                           if kind == "python" else
                           "No Node 22 found; optional bundled browser driver unavailable"),
            })
    return {"python": choices["python"], "node22": choices["node22"],
            "checked": checked, "gaps": gaps}


def main(search: Optional[Search] = None) -> int:
    if search is None:
        search = Search(home=Path.home(),
                        path=tuple(Path(part) for part in os.environ.get("PATH", "").split(os.pathsep)))
    report = discover(search)
    print(json.dumps(report, indent=2))
    return 0 if report["python"] is not None else 3


if __name__ == "__main__":
    raise SystemExit(main())
