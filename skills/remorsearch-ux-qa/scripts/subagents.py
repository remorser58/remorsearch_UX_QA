#!/usr/bin/env python3
"""Choose the model and reasoning effort the skill's subagents run with.

In a terminal this shows a selection menu: arrow keys or j/k to move, Enter to choose,
a number to jump. --model and --effort save a choice without asking; --show prints the
saved choice and exits 3 when there is none, so an agent can tell that this is the
first run and ask the user once; --options prints the choices for that question.

The choice is stored in ${XDG_CONFIG_HOME:-~/.config}/remorsearch-ux-qa/config.json
(references/agent-setup.md) and applies to persona agents, research readers and
verifiers. It holds no secret. Codex models and their effort levels are read from the
Codex model cache when it exists.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

INHERIT = "inherit"
ROLES = ("operator", "judge")
HOSTS = ("codex", "claude-code", "other")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,119}$")
CLAUDE_MODELS = (("sonnet", "Sonnet", "best reports in the skill's subagent benchmark at max effort"),
                 ("opus", "Opus", "about as many defects, faster at high effort"),
                 ("fable", "Fable", "fewer defects in the benchmark"))
CLAUDE_EFFORTS = ("low", "medium", "high", "xhigh", "max")
OTHER_EFFORTS = ("low", "medium", "high")
AGENT_FILE = """---
name: {name}
description: {role} subagent of the Remorsearch UX QA skill ({what}). Use only when that skill starts one.
model: {model}
effort: {effort}
---
Follow the task prompt you are given. It comes from the Remorsearch UX QA skill.
"""


def config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "remorsearch-ux-qa" / "config.json"


def detect_host() -> str:
    here = str(Path(__file__).resolve())
    if "/.claude/" in here or os.environ.get("CLAUDECODE"):
        return "claude-code"
    if "/.codex/" in here or any(k.startswith("CODEX_") for k in os.environ):
        return "codex"
    return "other"


def codex_models() -> list[dict]:
    """Listed models from the Codex model cache, with their effort levels; [] without it."""
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    try:
        doc = json.loads((home / "models_cache.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for m in doc.get("models") or []:
        if not isinstance(m, dict) or m.get("visibility") not in (None, "list") or not ID_RE.match(str(m.get("slug", ""))):
            continue
        efforts = [e.get("effort") for e in m.get("supported_reasoning_levels") or [] if isinstance(e, dict) and e.get("effort")]
        out.append({"id": m["slug"], "label": m.get("display_name") or m["slug"], "efforts": efforts,
                    "default_effort": m.get("default_reasoning_level"), "hint": ""})
    return out


def host_options(host: str) -> dict:
    if host == "codex":
        models, efforts = codex_models(), []
        for m in models:
            efforts += [e for e in m["efforts"] if e not in efforts]
        return {"host": host, "models": models, "efforts": efforts or list(OTHER_EFFORTS)}
    if host == "claude-code":
        return {"host": host, "efforts": list(CLAUDE_EFFORTS), "models": [
            {"id": i, "label": label, "efforts": list(CLAUDE_EFFORTS), "default_effort": None, "hint": hint}
            for i, label, hint in CLAUDE_MODELS]}
    return {"host": host, "models": [], "efforts": list(OTHER_EFFORTS)}


def load_config(path: Path | None = None) -> dict | None:
    try:
        doc = json.loads((path or config_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("version") != 1 or not isinstance(doc.get("roles"), dict):
        return None
    if not all(isinstance(doc["roles"].get(r), dict) for r in ROLES):
        return None
    return doc


def save_config(host: str, model: str, effort: str, roles=ROLES, agent_types: dict | None = None,
                path: Path | None = None) -> Path:
    for value in (model, effort):
        if value != INHERIT and not ID_RE.match(value):
            raise ValueError(f"not a model or effort identifier: {value!r}")
    path = path or config_path()
    doc = load_config(path) or {"version": 1, "roles": {r: {"model": INHERIT, "effort": INHERIT, "agent_type": None} for r in ROLES}}
    for role in roles:
        doc["roles"][role] = {"model": model, "effort": effort, "agent_type": (agent_types or {}).get(role)}
    doc.update({"source": "user", "host": host, "decided_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".config.", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)
    return path


def write_agent_files(model: str, effort: str, folder: Path | None = None) -> dict:
    """Claude Code applies an effort only through an agent definition; never overwrite one."""
    folder = folder or Path.home() / ".claude" / "agents"
    folder.mkdir(parents=True, exist_ok=True)
    written = {}
    for role, name, what in (("operator", "remorsearch-operator", "persona agents, research readers"),
                             ("judge", "remorsearch-judge", "verifiers and judges")):
        target = folder / f"{name}.md"
        text = AGENT_FILE.format(name=name, role=role.capitalize(), what=what,
                                 model=model if model != INHERIT else "inherit", effort=effort)
        if target.exists() and target.read_text(encoding="utf-8") != text:
            print(f"kept the existing {target}; it differs from this choice", file=sys.stderr)
            continue
        target.write_text(text, encoding="utf-8")
        written[role] = name
    return written


# ---------------------------------------------------------------- selection menu

def step(index: int, key: str, count: int) -> tuple[int, bool]:
    """Apply one key to the highlighted row; True when the choice is made."""
    if key in ("up", "k"):
        return (index - 1) % count, False
    if key in ("down", "j", "tab"):
        return (index + 1) % count, False
    if key == "home":
        return 0, False
    if key == "end":
        return count - 1, False
    if key.isdigit() and 1 <= int(key) <= count:
        return int(key) - 1, False
    if key == "enter":
        return index, True
    return index, False


def read_key(fd: int) -> str:
    import select
    data = os.read(fd, 1)
    if data in (b"\r", b"\n"):
        return "enter"
    if data == b"\x03":
        raise KeyboardInterrupt
    if data == b"\t":
        return "tab"
    if data == b"\x1b":
        seq = b""
        while select.select([fd], [], [], 0.03)[0] and len(seq) < 4:
            seq += os.read(fd, 1)
        return {b"[A": "up", b"OA": "up", b"[B": "down", b"OB": "down", b"[H": "home", b"[F": "end"}.get(seq, "escape")
    return data.decode("utf-8", "ignore")


def select_tty(title: str, rows: list[tuple[str, str]], default: int, out=None) -> int:
    import termios
    import tty
    out = out or sys.stdout
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    index, count = default, len(rows)
    width = max(len(label) for label, _ in rows)

    def draw(first: bool) -> None:
        if not first:
            out.write(f"\x1b[{count}F")
        for i, (label, hint) in enumerate(rows):
            line = f"{'>' if i == index else ' '} {label.ljust(width)}" + (f"  {hint}" if hint else "")
            out.write("\x1b[2K" + (f"\x1b[36;1m{line}\x1b[0m" if i == index else line) + "\n")
        out.flush()

    out.write(f"? {title}  (arrows or j/k, Enter; a number jumps)\n\x1b[?25l")
    draw(True)
    try:
        tty.setcbreak(fd)
        while True:
            key = read_key(fd)
            if key == "escape":
                index = default
                break
            index, done = step(index, key, count)
            if done:
                break
            draw(False)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        out.write("\x1b[?25h")
    out.write(f"\x1b[{count + 1}F\x1b[J? {title}  {rows[index][0]}\n")
    out.flush()
    return index


def select_numbered(title: str, rows: list[tuple[str, str]], default: int, ask=input, out=None) -> int:
    out = out or sys.stdout
    out.write(f"{title}\n")
    for i, (label, hint) in enumerate(rows, 1):
        out.write(f"  {i}) {label}" + (f"  {hint}" if hint else "") + "\n")
    for _ in range(3):
        answer = ask(f"Choose 1-{len(rows)} [{default + 1}]: ").strip()
        if not answer:
            return default
        if answer.isdigit() and 1 <= int(answer) <= len(rows):
            return int(answer) - 1
    return default


def select(title: str, rows: list[tuple[str, str]], default: int = 0) -> int:
    if sys.stdin.isatty() and sys.stdout.isatty() and os.environ.get("TERM") != "dumb":
        try:
            return select_tty(title, rows, default)
        except (ImportError, OSError):
            pass
    return select_numbered(title, rows, default)


def ask_choice(host: str) -> tuple[str, str, bool]:
    """(model, effort, write Claude agent files) from the menus."""
    opts = host_options(host)
    models = opts["models"]
    rows = [("Same as the main session", "no setting; subagents inherit the session's model")]
    rows += [(m["label"] + (f" ({m['id']})" if m["label"] != m["id"] else ""), m["hint"]) for m in models]
    rows.append(("Another model id", "type one the host accepts"))
    picked = select("Model for this skill's subagents (persona agents, research readers, verifiers)", rows)
    if picked == 0:
        model, efforts, default_effort = INHERIT, opts["efforts"], None
    elif picked == len(rows) - 1:
        model = ""
        while not ID_RE.match(model):
            model = input("Model id: ").strip()
        efforts, default_effort = opts["efforts"], None
    else:
        m = models[picked - 1]
        model, efforts, default_effort = m["id"], m["efforts"] or opts["efforts"], m["default_effort"]
    effort_rows = [("Same as the main session", "no setting")] + [
        (e, "the model's default" if e == default_effort else "") for e in efforts]
    effort = INHERIT
    picked = select("Reasoning effort for those subagents", effort_rows)
    if picked:
        effort = efforts[picked - 1]
    files = False
    if host == "claude-code" and effort != INHERIT:
        files = select("Claude Code applies an effort only through an agent definition. Create two in ~/.claude/agents?",
                       [("Create them (recommended)", "remorsearch-operator.md and remorsearch-judge.md; existing files are kept"),
                        ("No, use the session's effort", "")]) == 0
    return model, effort, files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Choose the model and reasoning effort of this skill's subagents.")
    parser.add_argument("--host", choices=HOSTS, help="agent host (default: guessed from where the skill is installed)")
    parser.add_argument("--model", help=f"model id, or '{INHERIT}' for the session's model")
    parser.add_argument("--effort", help=f"reasoning effort, or '{INHERIT}'")
    parser.add_argument("--role", choices=("all",) + ROLES, default="all", help="which subagents the choice applies to")
    parser.add_argument("--show", action="store_true", help="print the saved choice; exit 3 when there is none")
    parser.add_argument("--options", action="store_true", help="print the choices to offer, as JSON")
    parser.add_argument("--first-run", action="store_true", help="ask only when nothing is saved yet")
    parser.add_argument("--reset", action="store_true", help="forget the saved choice")
    args = parser.parse_args(argv)
    host = args.host or detect_host()
    saved = load_config()
    if args.show:
        if saved is None:
            print(json.dumps({"saved": False, "path": str(config_path())}))
            return 3
        print(json.dumps({"saved": True, "path": str(config_path()), **saved}, ensure_ascii=False))
        return 0
    if args.options:
        print(json.dumps(host_options(host), ensure_ascii=False, indent=1))
        return 0
    if args.reset:
        config_path().unlink(missing_ok=True)
        print(f"Forgot the saved choice ({config_path()}).")
        return 0
    roles = ROLES if args.role == "all" else (args.role,)
    if args.model or args.effort:
        try:
            path = save_config(host, args.model or INHERIT, args.effort or INHERIT, roles)
        except ValueError as error:
            print(f"subagents: {error}", file=sys.stderr)
            return 2
        print(f"Saved: subagents use {args.model or INHERIT} at {args.effort or INHERIT} effort ({path}).")
        return 0
    if args.first_run and saved is not None:
        return 0
    if not sys.stdin.isatty():
        print("subagents: no terminal to ask in; pass --model and --effort, or run this in a terminal", file=sys.stderr)
        return 2
    try:
        model, effort, files = ask_choice(host)
    except (KeyboardInterrupt, EOFError):
        print("\nNothing saved; subagents inherit the session's model until you choose.")
        return 1
    agent_types = write_agent_files(model, effort) if files else {}
    path = save_config(host, model, effort, roles, agent_types)
    print(f"Saved: subagents use {model} at {effort} effort ({path}).")
    print(f"Change it any time: python3 {Path(__file__).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
