#!/usr/bin/env python3
"""Install the complete Remorsearch UX QA skill with one command.

The installer reuses the deterministic bundle builder, so the tree it lands is
byte-identical to the release payload, carries manifest.remorsearch.json, and is
verified with the same bundled verifier before activation. The pinned Node.js 22
driver dependencies and Chromium are prepared on the staged copy first, so a
failed download leaves any working installation untouched. Updates archive the
complete previous folder, including run records and symlinks, as a compressed
tar file beside the skill, never as a second folder a host could discover.
Python 3.10+ and Node.js 22 are required up front; the command installs no
global runtime and touches no account. npm dependencies land inside the
destination, while Chromium downloads into Playwright's browser cache.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_insane_search_bundle as builder

SKILL_NAME = builder.SKILL_NAME
MANIFEST = builder.MANIFEST
LAUNCHER = Path("scripts") / "remorsearch.py"
SUBAGENTS = Path("scripts") / "subagents.py"
DRIVER = Path("drivers") / "web"
PLAYWRIGHT_CLI = Path("node_modules") / "playwright" / "cli.js"
NODE_MAJOR = 22
DRIVER_TIMEOUT = 1800
TARGETS = ("codex", "claude")
LAUNCH_CHECK = (
    "(async()=>{const pw=require('playwright');"
    "console.log(pw.chromium.executablePath());"
    "const args=(process.env.REMORSEARCH_CHROMIUM_ARGS||'').split(/\\s+/).filter(Boolean);"
    "const b=await pw.chromium.launch({headless:true,args});"
    "const p=await b.newPage();await p.goto('about:blank');await b.close();})()"
    ".catch(e=>{console.error(String(e&&e.message||e));process.exit(2);})"
)


class InstallError(ValueError):
    """A request the installer refuses before or while acting on it."""


class DriverError(RuntimeError):
    """Driver preparation failed; nothing was activated."""


def emit(record: dict) -> None:
    print(json.dumps(record, sort_keys=True, ensure_ascii=False), flush=True)


def parse_node_version(output: str) -> int | None:
    match = re.fullmatch(r"v?(\d+)\.\d+\.\d+\S*", output.strip())
    return int(match.group(1)) if match else None


def find_node() -> tuple[str | None, str | None, str | None]:
    """(path, version, problem). The check runs before any destination write."""
    node = shutil.which("node")
    if node is None:
        return None, None, (
            "Node.js 22 (>=22 <23) is required for the pinned Playwright web driver; "
            "no node executable was found in PATH. Put Node.js 22 first in PATH. "
            "The skill's runtime probe lists installed candidates without installing "
            "anything: python3 skills/remorsearch-ux-qa/scripts/find_runtime.py")
    try:
        result = subprocess.run([node, "--version"], text=True,
                                capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        return node, None, "Cannot run node: " + str(error)
    version = result.stdout.strip() if result.returncode == 0 else None
    if parse_node_version(version or "") != NODE_MAJOR:
        return node, version, (
            f"Node.js 22 (>=22 <23) is required for the pinned Playwright web driver; "
            f"found {version or 'an unreadable version'} at {node}. Put Node.js 22 "
            "first in PATH. The skill's runtime probe lists installed candidates "
            "without installing anything: "
            "python3 skills/remorsearch-ux-qa/scripts/find_runtime.py")
    return node, version, None


def target_destination(target: str, home: Path | None = None) -> Path:
    home = Path.home() if home is None else home
    root = ".codex" if target == "codex" else ".claude"
    return home / root / "skills" / SKILL_NAME


def find_npm_cli(node: str) -> tuple[Path | None, str | None]:
    """Resolve npm to its JavaScript CLI so the verified Node.js 22 runs it."""
    candidates = []
    found = shutil.which("npm")
    if found is not None:
        candidates.append(Path(found))
    sibling = Path(node).parent / "npm"
    if sibling not in candidates:
        candidates.append(sibling)
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError):
            continue
        if resolved.is_file() and resolved.name == "npm-cli.js":
            return resolved, None
    seen = ", ".join(str(candidate) for candidate in candidates) or "none"
    return None, (
        "npm must resolve to the npm CLI JavaScript entry (npm-cli.js) so the "
        "verified Node.js 22 runs it; PATH npm candidates: " + seen + ". Put a "
        "Node.js 22 installation's npm first in PATH and rerun.")


def absolute_destination(destination: Path) -> Path:
    expanded = destination.expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    return Path(os.path.normpath(str(expanded)))


def is_owned_installation(path: Path) -> bool:
    """True only for a folder this skill's manifest can vouch for."""
    skill = path / "SKILL.md"
    manifest = path / MANIFEST
    if skill.is_symlink() or manifest.is_symlink() or not skill.is_file() or not manifest.is_file():
        return False
    try:
        recorded = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return False
    engine = recorded.get("engine") if isinstance(recorded, dict) else None
    return isinstance(engine, dict) and engine.get("name") == SKILL_NAME


def destination_problems(destination: Path, *, home: Path, repo: Path) -> list[str]:
    """Why a destination is refused; empty when it is safe to own."""
    destination = absolute_destination(destination)
    problems: list[str] = []
    if destination == Path(destination.anchor):
        problems.append("the destination is the filesystem root")
    if destination == home:
        problems.append("the destination is the home directory itself")
    if destination == repo or repo in destination.parents or destination in repo.parents:
        problems.append("the destination overlaps the source repository " + str(repo))
    parts = destination.parts
    for index in range(1, len(parts)):
        candidate = Path(*parts[:index])
        if candidate.is_symlink():
            problems.append("symlinked path component: " + str(candidate))
        elif candidate.exists() and not candidate.is_dir():
            problems.append("path component is not a directory: " + str(candidate))
    if destination.is_symlink():
        problems.append("the destination itself is a symlink")
    elif destination.exists():
        if not destination.is_dir():
            problems.append("the destination exists and is not a directory")
        elif any(destination.iterdir()):
            if not is_owned_installation(destination):
                problems.append(
                    "the destination already holds an unrelated folder; "
                    "only an empty folder or an existing Remorsearch installation "
                    "can be used")
    return problems


def stage_payload(destination: Path, *, home: Path | None = None,
                  repo: Path | None = None, progress=emit) -> tuple[Path, dict]:
    """Write and verify the payload in a hidden staging folder beside the destination."""
    home = Path.home() if home is None else home
    repo = builder.REPO if repo is None else repo
    destination = absolute_destination(destination)
    problems = destination_problems(destination, home=home, repo=repo)
    if problems:
        raise InstallError("Unsafe destination " + str(destination) + ": "
                           + "; ".join(problems))
    payload, manifest = builder.build_payload(None)
    progress({"step": "payload", "destination": str(destination),
              "file_count": len(manifest["files"]),
              "payload_sha256": manifest["payload_sha256"]})
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise InstallError("Cannot create the destination parent: " + str(error)) from error
    staging = Path(tempfile.mkdtemp(prefix=".remorsearch-install-",
                                    dir=destination.parent))
    try:
        for relative in sorted(payload):
            target = staging / relative
            if not target.resolve().is_relative_to(staging.resolve()):
                raise InstallError("Unsafe payload path: " + relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload[relative])
            target.chmod(0o644)
        verification = builder.verify_output(staging)
        if not verification["valid"]:
            raise InstallError("Staged payload failed verification: "
                               + "; ".join(verification["problems"]))
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return staging, {"destination": str(destination),
                     "file_count": len(manifest["files"]),
                     "payload_sha256": manifest["payload_sha256"]}


def backup_archive(destination: Path) -> Path:
    """A tar archive beside the skill; hosts discover folders, not archive files."""
    stamp = time.strftime("%Y%m%dT%H%M%S")
    archive = destination.with_name(f"{destination.name}.backup-{stamp}.tar.gz")
    order = 2
    while archive.exists() or archive.is_symlink():
        archive = destination.with_name(f"{destination.name}.backup-{stamp}-{order}.tar.gz")
        order += 1
    return archive


def write_backup(destination: Path) -> Path:
    """Archive the entire installation: files, run records and symlinks."""
    archive = backup_archive(destination)
    handle, name = tempfile.mkstemp(prefix=".remorsearch-backup-",
                                    suffix=".tar.gz.partial", dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "wb") as stream:
            with tarfile.open(fileobj=stream, mode="w:gz", dereference=False) as target:
                for child in sorted(destination.iterdir()):
                    target.add(child, arcname=child.name, recursive=True)
        if archive.exists() or archive.is_symlink():
            raise InstallError("The backup path appeared during the update: "
                               + str(archive))
        temporary.rename(archive)
    except (OSError, RuntimeError, tarfile.TarError) as error:
        raise InstallError("Cannot write the update backup " + str(archive)
                           + ": " + str(error)) from error
    finally:
        if temporary.exists():
            temporary.unlink()
    return archive


def activate(staging: Path, destination: Path, *, progress=emit) -> dict:
    """Move a verified staging folder into place, keeping a rollback copy."""
    destination = absolute_destination(destination)
    backup = None
    previous = None
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise InstallError("The destination changed during installation: " + str(destination))
    if destination.exists():
        if any(destination.iterdir()):
            if not is_owned_installation(destination):
                raise InstallError("The destination now holds an unrelated folder: "
                                   + str(destination))
            backup = write_backup(destination)
            previous = destination.with_name(".remorsearch-previous-"
                                             + time.strftime("%Y%m%dT%H%M%S"))
            destination.rename(previous)
        else:
            destination.rmdir()
    try:
        staging.rename(destination)
    except OSError:
        if previous is not None and not destination.exists():
            previous.rename(destination)
        raise
    finally:
        if previous is not None and destination.exists():
            shutil.rmtree(previous, ignore_errors=True)
    progress({"step": "activated", "destination": str(destination),
              "backup": str(backup) if backup else None})
    return {"skill_directory": str(destination),
            "backup": str(backup) if backup else None}


def driver_environment(node: str) -> dict:
    environment = os.environ.copy()
    node_directory = str(Path(node).parent)
    path = environment.get("PATH", "")
    if node_directory not in path.split(os.pathsep):
        environment["PATH"] = node_directory + os.pathsep + path
    return environment


def prepare_driver(skill_root: Path, node: str, npm_cli: str, *, runner=None,
                   timeout: int = DRIVER_TIMEOUT, progress=emit) -> dict:
    """Prepare the pinned driver dependencies and a working Chromium launch."""
    driver = skill_root / DRIVER
    if not (driver / "package.json").is_file():
        raise DriverError("The staged web driver is incomplete: "
                          + str(driver / "package.json") + " is missing")
    environment = driver_environment(node)

    if runner is None:
        def runner(command, cwd, env):
            try:
                return subprocess.run(command, cwd=cwd, env=env, text=True,
                                      capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired as error:
                raise DriverError(f"driver command timed out after {timeout}s: "
                                  + " ".join(command)) from error
            except OSError as error:
                raise DriverError("driver command could not run: " + str(error)) from error

    def check(label: str, command: list[str]) -> str:
        result = runner([str(part) for part in command], driver, environment)
        if result.returncode != 0:
            tail = "\n".join((result.stdout + result.stderr).splitlines()[-12:])
            raise DriverError(f"{label} failed with exit code {result.returncode}:\n{tail}")
        return (result.stdout or "").strip()

    check("npm ci (pinned driver dependencies)",
          [node, npm_cli, "ci", "--no-audit", "--no-fund"])
    version = check("Playwright version check", [node, "-e",
        "const p=require('./package.json');"
        "const v=require('./node_modules/playwright/package.json').version;"
        "console.log(v); if(v!==p.dependencies.playwright) process.exit(2)"])
    check("Chromium install", [node, PLAYWRIGHT_CLI, "install", "chromium"])
    try:
        chromium = check("Chromium launch check (about:blank)", [node, "-e", LAUNCH_CHECK])
    except DriverError as error:
        if not sys.platform.startswith("linux"):
            raise
        raise DriverError(f"{error}\nOn Linux, Chromium also needs system libraries. Run "
                          f"'npx -y playwright@{version} install-deps chromium' once (Debian or "
                          "Ubuntu; it asks for sudo) or install the equivalent packages, then run "
                          "the installer again.") from error
    result = {"node": node, "playwright": version,
              "chromium": chromium.splitlines()[0] if chromium else None}
    progress({"step": "driver", **result})
    return result


def install_skill(destination: Path, *, node: str, npm_cli: str, home: Path | None = None,
                  repo: Path | None = None, runner=None, progress=emit) -> dict:
    """Stage, prepare and re-verify the driver, then activate only on success."""
    staging, staged = stage_payload(destination, home=home, repo=repo, progress=progress)
    try:
        driver = prepare_driver(staging, node, npm_cli, runner=runner, progress=progress)
        verify_staged(staging, progress=progress)
        activated = activate(staging, destination, progress=progress)
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    return {**staged, **activated, "driver": driver}


def launcher_paths(root: Path, *, staged: bool = False) -> dict:
    """Run the launcher's own paths report as an integrity check."""
    launcher = root / LAUNCHER
    label = "staged" if staged else "installed"
    try:
        result = subprocess.run([sys.executable, str(launcher), "paths"],
                                text=True, capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise InstallError(f"Cannot run the {label} launcher: " + str(error)) from error
    if result.returncode != 0:
        tail = "\n".join((result.stdout + result.stderr).splitlines()[-12:])
        raise InstallError(f"The {label} launcher failed its integrity check:\n" + tail)
    try:
        return json.loads(result.stdout)
    except ValueError as error:
        raise InstallError(f"The {label} launcher printed an unreadable report: "
                           + str(error)) from error


def verify_staged(staging: Path, *, progress=emit) -> dict:
    """Verify the staged skill again after dependencies land, before activation."""
    verification = builder.verify_output(staging)
    if not verification["valid"]:
        raise InstallError("The staged payload changed during driver preparation: "
                           + "; ".join(verification["problems"]))
    paths = launcher_paths(staging, staged=True)
    progress({"step": "staged-verified", "payload_sha256": verification["payload_sha256"]})
    return paths


def choose_subagents(destination: Path, args: argparse.Namespace) -> dict:
    """First run: the model and reasoning effort for the skill's subagents.

    Flags save a choice without asking. In a terminal the skill's selection menu asks
    once, unless a choice is already saved. Without a terminal nothing is asked; the
    skill then asks at its first run.
    """
    script = destination / SUBAGENTS
    host = "claude-code" if args.target == "claude" else ("codex" if args.target in (None, "codex") else "other")
    command = [sys.executable, str(script), "--host", host]
    if args.subagent_model or args.subagent_effort:
        command += ["--model", args.subagent_model or "inherit", "--effort", args.subagent_effort or "inherit"]
    elif args.no_prompt or not (sys.stdin.isatty() and sys.stdout.isatty()):
        return {"asked": False, "change_with": f"python3 {script}"}
    else:
        command.append("--first-run")
    result = subprocess.run(command)
    return {"asked": True, "exit": result.returncode, "change_with": f"python3 {script}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install the complete Remorsearch UX QA skill, including the "
                    "pinned Node.js 22 web driver and Chromium, into one folder.")
    parser.add_argument("--target", choices=TARGETS,
                        help="skills directory of the host agent (default: codex)")
    parser.add_argument("--destination", type=Path,
                        help="explicit destination folder, for test isolation")
    parser.add_argument("--subagent-model",
                        help="model for the skill's subagents, or 'inherit' (saved without asking)")
    parser.add_argument("--subagent-effort",
                        help="reasoning effort for the skill's subagents, or 'inherit'")
    parser.add_argument("--no-prompt", action="store_true",
                        help="do not ask for the subagent model and effort; the skill asks at its first run")
    args = parser.parse_args(argv)
    if args.target and args.destination:
        parser.error("--target and --destination are mutually exclusive")
    try:
        if sys.version_info < (3, 10):
            raise InstallError("Python 3.10 or later is required; found "
                               + sys.version.split()[0])
        node, node_version, problem = find_node()
        if problem:
            raise InstallError(problem)
        npm_cli, npm_problem = find_npm_cli(node)
        if npm_problem:
            raise InstallError(npm_problem)
        destination = (args.destination if args.destination is not None
                       else target_destination(args.target or "codex"))
        installed = install_skill(destination, node=node, npm_cli=str(npm_cli))
    except InstallError as error:
        print("install: " + str(error), file=sys.stderr)
        return 2
    except DriverError as error:
        print("install: " + str(error), file=sys.stderr)
        print("install: the staged copy was discarded before activation, so any "
              "existing installation is unchanged; fix Node.js/npm/network and rerun",
              file=sys.stderr)
        return 3
    destination = Path(installed["skill_directory"])
    driver = installed["driver"]
    try:
        paths = launcher_paths(destination)
    except InstallError as error:
        print("install: the skill tree is installed at " + str(destination)
              + ", but the launcher integrity check failed: " + str(error),
              file=sys.stderr)
        return 3
    summary = {
        "installed": True,
        "skill_directory": str(destination),
        "entrypoint": str(destination / "SKILL.md"),
        "launcher": str(destination / LAUNCHER),
        "file_count": installed["file_count"],
        "payload_sha256": installed["payload_sha256"],
        "backup": installed["backup"],
        "node": node_version,
        "playwright": driver["playwright"],
        "chromium": driver["chromium"],
        "workflows": paths["workflows"],
        "bundled_search": paths["search_source"],
        "components": "research, persona-qa, ergonomics, loop and the bundled "
                      "insane-search toolkit are all installed; no feature selection exists",
    }
    emit({"step": "installed", **summary})
    emit({"step": "subagents", **choose_subagents(destination, args)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
