# Local release candidate

The distribution installs one `remorsearch-ux-qa/` folder with exactly one
discoverable `SKILL.md`. The engine, workflows, discovery metadata and scripts
keep their normal paths. The original insane-search toolkit is included under
`references/insane-search/`; its SKILL.md is retained unchanged as `SOURCE.md`.
Both the repository-folder installation and the release ZIP include the toolkit.
Users need no separate search-skill installation.

## Install

Users install the whole skill with one command. The builder and checker below
remain maintainer tools for producing and validating the distribution.

```sh
python3 scripts/install.py --target codex
```

Use `--target claude` for `~/.claude/skills/remorsearch-ux-qa`, or
`--destination /path/to/folder` for an explicit path. The installer requires
Python 3.10+, Node.js 22 (>=22 <23) and npm up front, and checks them before
writing anything. It stages the deterministic payload from this builder,
verifies it against `manifest.remorsearch.json`, runs `npm ci` and the
Chromium install inside the staged copy's `drivers/web`, confirms an actual
Chromium launch, verifies the staged payload again after the dependencies land,
and only then activates the destination. A failure at any point before
activation discards the staged copy and leaves an existing installation
unchanged.

The installer refuses symlinked destination paths, destinations overlapping
this repository, the filesystem root, the home directory and unrelated existing
folders. Updating an owned installation first archives the complete previous
folder, including run records and symlinks, as
`remorsearch-ux-qa.backup-<timestamp>.tar.gz` beside the skill folder; hosts
discover folders, not archive files. npm dependencies live inside the
destination's `drivers/web/node_modules`; Chromium downloads into Playwright's
browser cache (`~/Library/Caches/ms-playwright` by default on macOS, overridable
with `PLAYWRIGHT_BROWSERS_PATH`). External accounts stay user prerequisites.

## Build and verify

Use Python 3.10+ on macOS, Linux or WSL. Run from this repository. The default
input is the checked-in toolkit; no network or installed-skill lookup is needed.

```sh
python3 scripts/build_insane_search_bundle.py --output dist/remorsearch-rc
python3 scripts/build_insane_search_bundle.py --verify dist/remorsearch-rc
python3 dist/remorsearch-rc/remorsearch-ux-qa/scripts/remorsearch.py smoke
```

The output contains the installable `remorsearch-ux-qa/` tree and
`remorsearch-ux-qa.zip`. SHA-256 receipts record the original inputs and shipped
content. Identical inputs produce identical ZIP bytes. Verification detects
missing, changed and extra files; it is an integrity check, not a publisher signature.

Maintainers may explicitly replace the toolkit with an existing local input:

```sh
python3 scripts/build_insane_search_bundle.py --base-skill /path/to/insane-search --output dist/remorsearch-custom
```

This option reads the input without changing it. The output keeps Remorsearch as
the installed skill and records whether the input matches the checked-in snapshot.
It retains supplied licenses and does not assign the upstream license to
unrelated or independently modified input.

After extracting the ZIP elsewhere, use the launcher's absolute path from any
working directory:

```sh
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py paths
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py verify
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py research --help
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py ref references/insane-search/SOURCE.md phase-0-특수-엔드포인트-인덱스
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py ref references/insane-search/references/public-api.md stack-exchange-v23
python3 /path/to/remorsearch-ux-qa/scripts/remorsearch.py smoke
```

An omitted section ID lists headings only. The two reference commands above
load the source index body and an actual linked platform method body.

## Complete local check

Prepare the source tree's pinned web driver dependencies and Chromium using
Node.js 22. An installation made with `scripts/install.py` already carries its
own copy; these commands prepare the checkout the checker copies from:

```sh
(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium)
python3 scripts/check_release.py --output dist/release-check
```

The checker runs the Python suite, release-file checks, the offline build,
tree/ZIP verification, extraction, relocated CLI and reference reads, both
synthetic smoke workflows, and the Chromium driver selftest from the extracted
installation. It copies already prepared driver dependencies into that disposable
installation and performs no downloads or install hooks. It verifies package
integrity again after the browser test and compares the candidate with current
inputs. `validation.json` records each check and its log.

The output must be a new directory. Failed checks return nonzero. `--skip-web`
produces a partial report with `ready: false`. Synthetic tests establish local
behavior and packaging; live community access, real-user preferences, Figma access
and accessibility certification remain outside this check.

## Research and distribution boundary

Research plans its questions and discovers candidate URLs, then loads the bundled
search source and appropriate linked method for acquisition. Every selected method
follows Remorsearch's access, provenance and privacy controls. Supported captures
enter the existing reader/ingest checks; unsupported output remains a lead.
A site/run stop stays final across every toolkit method.

The build excludes dependencies, caches, local run state and internal handoff
records. It preserves Remorsearch's MIT license and third-party notices.
`references/insane-search/PROVENANCE.json` records the attributed original snapshot.
The installed original contained no license. The separately retrieved
[upstream MIT license](https://github.com/fivetaku/insane-search/blob/main/LICENSE)
is retained verbatim as `references/insane-search/upstream-LICENSE` and in the
repository at `integrations/insane-search/upstream-LICENSE`. Its retrieval date is
2026-10-02 (Asia/Seoul). Local hash matches prove byte identity with the recorded
snapshot; they do not prove current upstream authenticity or confer rights on a
different maintainer input.

These commands create local artifacts. Publishing, pushing commits and changing
installed skills are separate actions. Internal source-checkout records are
excluded from the distribution.
