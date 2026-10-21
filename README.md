# Remorsearch UX QA

English | [한국어](README.ko.md)

Remorsearch UX QA is a skill for Claude Code and Codex that checks and improves the UI and UX of a product you already have. Give it a URL or a repository. It scans the rendered pages on a phone and a laptop, shows each suspected defect as an outlined screenshot crop, exercises the tasks you name, researches related user experiences when you ask, and can apply small fixes and replay them.

## What it does

| Component | What it does | Needs |
| --- | --- | --- |
| **persona-qa** | Rendered UI QA. One command scans a page from top to end on a phone and a laptop and measures cut text, text a fixed bar keeps covering, overlapping text, near-miss alignment, uneven list spacing, contrast, target size and reflow. The agent confirms each candidate in the pixels, then checks tasks, forms, keyboard use and accessibility (KWCAG 2.2, WCAG 2.2). | A reachable URL, Node.js 22 and the bundled Playwright driver. |
| **research** | Finds task-related experiences, workarounds and counterexamples in communities, comments, reviews and official sources, keeping source context and gaps. | Sources you may read. YouTube comments use your own YouTube Data API key (`REMORSEARCH_YOUTUBE_API_KEY`). |
| **ergonomics** *(experimental)* | Screens reach, touch, perception and timing with simulated profiles. | Relevant scenarios. Model results stay separate from real-device evidence. |
| **loop** | Records scoped fixes, current-build replay, regression and preserved-intent checks. | Your browser and design tools. Works for Figma-first and code-first projects. |

You do not pick components. Ask for a UI check, a UX improvement, research or an accessibility review, and the skill loads only what that request needs.

On a benchmark of 28 rendered defects, 11 decoys and four clean twins written blind to the detector ([`visual-layout-20261018.md`](docs/validation/visual-layout-20261018.md)), the scan's measured checks found 19 defects on first contact, up from 3 before these checks, with no new finding on a decoy or clean page. The detector was then fixed on the misses and finds 25 on the same pages, so 25 is a fit to those pages; 19 is the held-out number. The same recall reproduced on Ubuntu 24.04 after the documented setup.

Whether an agent does better QA with the skill is still not shown by the rule registered before each comparison, which asks for more known defects in all three paired runs. In round 4 ([`real-layout-bugs-4`](docs/validation/real-layout-bugs-4/README.md)), 8 layout bugs from projects no earlier round used, DeepSeek 4.1 Flash found 12 of 16 known defects with the skill against 9 without: more in two runs and the same in the third, with 4 unsupported findings or alarms against 5. GPT-6.1 Sol found 13 against 14 and took 1.64 times as long. The scan alone matched 5 of the 8 bugs, against 3 for the version frozen for round 3, and nothing found a textarea 31 px narrower than the fields above it. In round 3 ([`real-layout-bugs-3`](docs/validation/real-layout-bugs-3/README.md)) both arms of both models found the same 2 of 8. On the round 1 and 2 pages that the round 3 measurements were built from, GPT-6.1 Sol found 25 of 34 and 7 of 8 known defects with that skill against 18 and 6 without, and DeepSeek 4.1 Flash 18 and 8 against 14 and 6; Sol took about twice as long on the round 1 pages. Earlier versions did not help: 1.0.0 found 13 of 34 with Sol and 15 with Flash ([`real-layout-bugs`](docs/validation/real-layout-bugs/README.md)), and 1.0.1 tied at 6 of 8 ([`real-layout-bugs-2`](docs/validation/real-layout-bugs-2/README.md)). On its own the scan matches 12 of the 16 round 1 and 2 defects (5 for 1.0.1) and records a page in a median 37 s on those pages and 45 s on the round 4 pages, against 117 s for 1.0.1. The earlier [agent comparison](docs/validation/agent-comparison-20261018/README.md) on the benchmark pages above found 28, 28 and 24 of 28 with the skill against 28, 27 and 22 without; it favours the skill, because the detector was tuned on those pages.

## Install

```sh
git clone https://github.com/remorser58/remorsearch_UX_QA.git
cd remorsearch_UX_QA
python3 scripts/install.py --target codex
```

`--target claude` installs into `~/.claude/skills/remorsearch-ux-qa`; the default `codex` installs into `~/.codex/skills/remorsearch-ux-qa`. `--destination /path/to/folder` picks an explicit folder.

After installing, the installer asks once which model and reasoning effort the skill's subagents use, in a menu you move through with the arrow keys; on Codex it lists the models your account offers. `--subagent-model` and `--subagent-effort` answer up front, `--no-prompt` skips the question, and `python3 scripts/subagents.py` in the skill folder changes the answer later. If the installer did not ask, the skill asks at its first run.

The installer needs Python 3.10+, Node.js 22 (>=22 <23) and npm on macOS, Linux or WSL, and checks them before writing anything. It prepares the pinned Playwright driver and Chromium in a staged copy, launches Chromium once, and only then activates the folder. A failed download leaves an existing installation untouched; an update first keeps the previous folder as `remorsearch-ux-qa.backup-<timestamp>.tar.gz`. Node.js 22 is required because the pinned Playwright 1.56.1 browser download hangs on Node.js 24.16 and later ([microsoft/playwright#40724](https://github.com/microsoft/playwright/issues/40724)). If your default `python3` is older than 3.10, run `python3 scripts/find_runtime.py` inside the skill folder; it lists usable Python and Node.js paths and installs nothing. On Linux, Chromium also needs system libraries: if the launch check fails, run `npx -y playwright@1.56.1 install-deps chromium` once (Debian or Ubuntu; it asks for sudo) and run the installer again.

In Claude Code you can also add this repository as a plugin marketplace and install the plugin: `/plugin marketplace add remorser58/remorsearch_UX_QA`, then `/plugin install remorsearch-ux-qa@remorsearch`. A plugin copy skips the installer's browser setup, so its first scan stops and prints the one-time command that prepares it (`npm ci` and `npx playwright install chromium` in the plugin's `drivers/web`).

Accounts stay yours: YouTube comments need your YouTube Data API key and Figma comparison needs your Figma access. Packaging and integrity checks for maintainers are in [build and release checks](docs/release.md).

## Use

Ask in plain words, or call the skill by name (`/remorsearch-ux-qa` in Claude Code, `$remorsearch-ux-qa` in Codex):

```text
/remorsearch-ux-qa Check the UI of https://app.example.test on a phone and a laptop.
/remorsearch-ux-qa 이 화면 UI QA해줘: https://app.example.test/checkout
/remorsearch-ux-qa Improve our app UX. Repository: /path/to/product
/remorsearch-ux-qa Find out why people abandon our checkout, from reviews and community posts.
/remorsearch-ux-qa 간편결제 실패 경험을 한국어 커뮤니티와 앱 리뷰에서 근거 붙여서 정리해 줘.
```

A UI check starts with one measured scan. You can run it yourself too:

```sh
python3 ~/.codex/skills/remorsearch-ux-qa/scripts/ergo_qa.py scan --url https://app.example.test --out scan-out
```

It records the page on `galaxy-s24` (360×780) and `laptop-1440` (1440×900) by default (`--device ID` changes them) and writes `scan-out/scan.md` with one row per candidate, `scan.json` and `crops/` with each suspected region outlined. Candidates are measurements. The agent opens every crop and the full screenshots before reporting one, and lists what it dismissed. A page that never loaded is a coverage gap, never a clean result.

The agent then exercises the tasks you name (happy path, a required omission, validation, recovery, keyboard), adds research only when you ask, and reports a verdict with at most three actions, findings with evidence and fixes, and what stayed untested.

## Evidence rules

- Every statement is observed, inferred or unknown. A verified finding links a completed run on the same build.
- A scan candidate counts only after the pixels confirm it. A saved capture is not a review.
- Synthetic personas and simulated profiles create test conditions. They never show real-user preference, prevalence or discomfort.
- Community posts show that a situation exists, never how often it happens.
- Research and review requests stay read-only. An improvement request allows ordinary reversible fixes in its scope; deployment, publication and account changes need their own permission.
- The skill follows your project's design source and rules and adds no house style of its own. When design lives in Figma, changes start there; a code-first project changes code and keeps before/after captures.

## Reading public pages

Research reads what anyone can read without an account.

- **Tools.** It uses the best browser tool your agent host has (an agentic browser, then an automation browser such as Playwright MCP or the bundled page reader `read_page.mjs`), then its own reader, and last plain search and fetch, whose results are leads only. It records which tool read each source.
- **The reader** (`scripts/ux_research.py`) climbs a short ladder only as far as needed: an official feed or API, one honestly identified request, the site's mobile or feed version, then a real-browser render.
- **Stops.** It stops at logins, paywalls, member-only groups, age checks, human checks such as CAPTCHAs, bot blocks, robots.txt and AI or TDM opt-outs, rate limits and removed posts, and reports each as a coverage gap. A stop ends that site for the run. It also stops where a platform's published terms restrict automated collection (`terms_restricted`). It never disguises itself, never reads search results pages, and reads one page at a time per host, at least 8 seconds apart by default.
- **Privacy.** Quotes are short, authors become salted keys, and temporary page text stays outside your project and is deleted when the run closes. Phone numbers, e-mail addresses, ID, card and account numbers and IP addresses are removed before the agent sees the text.

Details: [`public-page-access.md`](skills/remorsearch-ux-qa/references/research/public-page-access.md).

## Korean research

For a Korean product, Korean-speaking users or a report in Korean, research also follows the Korean pack, which starts at [`overview.md`](skills/remorsearch-ux-qa/references/research/korea/overview.md). Persona QA adds the accessibility notes in [`kwcag-2.2.md`](skills/remorsearch-ux-qa/references/persona-qa/kwcag-2.2.md). The pack is written in Korean and adds a map of 27 Korean channels with their access routes and terms status, Korean query craft, disclosure and review-reward markers, provenance cards for Korean statistics, a legal checklist (not legal advice) and a Korean report template.

Many Korean platforms restrict automated collection. DC Inside, Naver, Coupang, X, Daangn and Reddit need your current terms check and their written permission before the reader lifts a page; YouTube is read only through its Data API with your key, which follows YouTube's API terms (stored items expire 30 days after the fetch). See [the entries and checks](skills/remorsearch-ux-qa/references/research/public-page-access.md#171-entries).

## Repository layout

```text
skills/remorsearch-ux-qa/      the installable skill (installed by scripts/install.py)
  SKILL.md                     entry point
  references/                  mode workflows and reference cards, loaded per task
  scripts/                     CLIs: ergo_qa (scan and analysis), ux_research, ux_loop, validate_bundle
  drivers/web/                 Playwright driver (Node.js 22)
  ergoqa/ uxloop/ uxresearch/  Python packages behind the CLIs
scripts/                       installer and release checks
benchmarks/                    benchmark suites with answer keys
tests/                         unit tests and fixtures (offline)
docs/                          design notes, research notes and validation records
```

## Development

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium && node selftest.mjs)
python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/mobile-commerce --out .ergo-bench/mobile
python3 scripts/check_release.py --output dist/release-check
```

The tests never reach the network; reader tests serve their pages from 127.0.0.1. The loop CLI reference is [`references/loop/cli.md`](skills/remorsearch-ux-qa/references/loop/cli.md). [Validation records](docs/validation/README.md) describe how each published number was produced and how to rerun it.

## Limits

- The scan emulates devices in Chromium. Safari/WebKit and real devices need their own runs; Mobile Safari is checked through a documented host route (safaridriver with an iOS Simulator), and native iOS apps through imported XCUITest evidence.
- The scan loads only the page's own origin unless `--allow-origin` names more (a font or image CDN), and it lists blocked requests and any page interval it did not capture.
- Measured candidates cover geometry, contrast, target size and names. Hierarchy, wording, brand fit and Figma fidelity are judged by the agent from viewed pixels and a reference.
- Alignment and spacing checks compare sibling blocks of the same kind and report P3 candidates; an intended offset can appear and is dismissed after viewing.
- On a `file://` page the scan loads stylesheets, scripts, fonts, images and media from any local folder; frames and other documents load only from the page's folder and below. Under `REMORSEARCH_CHROMIUM_ARGS=--single-process` each pass that needs its own browser context runs in a browser process of its own. A pass that still cannot run is listed in `scan.md` as a check that did not run. Version 1.0.0 blocked parent-folder stylesheets and lost these passes without a note.
- RF-01 exempts tables and other two-dimensional content, as WCAG 1.4.10 does; LY-08 reports any page wider than the screen at the device width, tables included. The scan does not compare the widths of sibling form controls, measure the gap between adjacent links or notice menu items hanging below a fixed bar. A scan of eight pages takes several minutes and much longer on a busy machine; in two of three round 4 runs with the cheaper model it had not finished when the agent wrote its report.
- The ergonomics model is uncalibrated and its suites are small and agent-authored. Treat its findings as screening.
- The reader honours robots.txt and AI or TDM opt-outs and stops at bot checks, so some sites end as coverage gaps.

## License

MIT, see [`LICENSE`](LICENSE). Third-party material and references are listed in [`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md).

Credits: the public-page reader and the research gate were designed after studying fivetaku's [insane-search](https://github.com/fivetaku/insane-search) and [insane-research](https://github.com/fivetaku/insane-research) (both MIT). The original insane-search toolkit is bundled as reference material with its provenance and upstream license. The Korean pack and this README's bilingual layout draw ideas from [K-skill](https://github.com/NomaDamas/k-skill) (MIT), DaleSeo's [korean-skills](https://github.com/DaleSeo/korean-skills) (MIT), [SoDam-Persona-Codex](https://github.com/sodam-ai/SoDam-Persona-Codex) (Apache-2.0) and fivetaku's [gptaku_plugins](https://github.com/fivetaku/gptaku_plugins) (MIT), ideas only. Platform names are descriptive; there is no affiliation with any of them.
