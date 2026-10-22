# Real layout bugs, round 7: preregistered protocol

Written 2026-10-23, after the candidate lists of the sources below were generated and before any candidate page was rendered or judged, and before any agent ran on these sources. Changes after this point are listed at the end with their reason.

## Question

In round 6 GPT-6.1 Sol found 8 of 16 known defects with the skill and 8 without, and took 1.15 times as long with it. Four of the eight cases were kinds the review prompt does not ask for, and both arms missed all four. After the round, commit 1de6620 added LY-16 (three or more texts within 1.5 px of the screen edge), LY-17 (a phone page laid out 30 % wider than the screen without a device-width viewport) and a words-per-line rule to LY-10, and stopped the scan from scrolling pages that cannot scroll. On the round 6 pages, which those changes were built from, the scan recorded the 16 states in 58 s instead of 94 s, and in a rerun scored without blinding the skill arm's median time fell below the plain arm's (6.45 against 6.94 minutes) with 8 of 16 found in both arms. Pull request #2 merged these changes into \`main\`. On new real layout bugs from projects no round used, limited to the kinds the prompt asks for, does GPT-6.1 Sol with the skill find more of them than without it, without more false alarms and in less time?

## Skill under test

Commit f7f00301615e64d0d808cd42fe3ca0fc644d1d43 on \`main\`, the merge of pull request #2, installed once with \`scripts/install.py --no-prompt\` into an isolated folder (payload SHA-256 \`bd2bc7963d6948a6b122b5966d98ed1188b375226ac481479de54d4e81724435\`). No skill or detector file changes until every round 7 run is scored.

## Sources

Sixty-five repositories cloned on 2026-10-23 for this round, none used in rounds 1 to 6, chosen from GitHub searches for small CSS frameworks and libraries with a demo page and for free admin and page templates. lowlighter/matcha was considered in round 5 and dropped then; it is dropped again below for the same reason.

Thirty-eight have HTML pages next to committed CSS in the history of their default branch and are screened in this order: adoahr/8.bit-css, bonsaicss/bonsai.css, puikinsh/Bootstrap-Admin-Template (the pages in \`dist/\` with \`dist/assets/\`, committed until 2016), cardinalcss/cardinalcss, 720kb/checkbox.css, moesaid/cleopatra (\`dist/\`), codyhouse/codyframe (\`main/\`), puikinsh/CoolAdmin, jackdomleo7/Cooltipz.css, ArunMichaelDsouza/CSS-Mint, dropways/deskapp, puikinsh/ElaAdmin (before its pages became templates), kanbanize/eve (the documentation pages in \`docs/\` without their partials), kenangundogan/flexible-grid, aaroniker/framy-css, puikinsh/kiaalap (before its pages became templates), p3yman/koochak, joexn/LegacyCSS, zuramai/mazer (\`dist/\` and \`demo/\`), mazipan/milligram-admin-dashboard-template, OshekharO/Neubrutalism, sreeram-venkitesh/notion.css, ionited/particle, getpavilion/pavilion, PlainAdmin/plain-free-bootstrap-admin-template, xriley/portal-theme-bs5, ummahusla/PotatoCSS, micah5/PSone.css, StartBootstrap/startbootstrap-full-slider, oltdaniel/skeleton-plus, themefisher/sleek-bootstrap (\`dist/\`), snack-ui/snack, puikinsh/srtdash-admin-dashboard, secondtruth/startmin, jeroenoomsNL/the-flex-grid, smakosh/unnamed-css-framework, zuramai/voler (\`dist/\`) and themesberg/windows-95-ui-kit. Their candidate lists (\`candidates.json\`), newest first and cut at 40 per source, hold 403 candidates, 326 of them with a page to render. Mazer gives 40 candidates and none with a page: its 40 newest matching commits came after it removed \`dist/\` in 2022.

Twenty-seven were dropped before screening:

- No HTML page in the history of the default branch: outboxcraft/beauter, Avalojandro/Catto-CSS, lazaronixon/css-zero, johannschopplich/duecss, bansal/filters.css, Dreamer-Paul/Kico-Style, ghosh/microtip, frontaid/natural-selection, chris-pearce/scally and ThinkUniform/uniformcss. The history of frameable/knopf.css holds only Storybook fragments and a test page removed on the day it was added.
- Pages that are templates of a site generator or an application: jgthms/bulma (Jekyll documentation), bigskysoftware/missing (pages for its site builder), knadh/oat (documentation templates), codeship/shipyard (a Jekyll style guide), TorstenDittmann/launch.css (a Svelte application), ingram-projects/animxyz (React and Vue examples and a test page whose stylesheet is built), conedevelopment/sprucecss (preview pages that link a root-absolute stylesheet inside their build folder) and puikinsh/Adminator-admin-dashboard (pages built by webpack, with no CSS committed).
- torch2424/aesthetic-css: its demo pages are fragments without a stylesheet.
- MarkusJohansen/ChimeraCSS and jfet97/strawberry: their pages load the library's own stylesheet from a CDN.
- lowlighter/matcha: its page links a stylesheet that a build step produces.
- No commit matching the candidate rule: admincast/admincast, themefisher/focus-bootstrap, BootstrapDash/Kapella-Free-Bootstrap-Admin-Template and omerimzali/uiterminal.

## Rules

Candidate rule, per-source limits (3 accepted or 40 screened), stop rule (12 cases), page items, the seeded split and three-run rotation, the round 1 prompt templates byte for byte, the 30-minute budget, scoring blind to arm and the decision rule are as registered for rounds 2 to 6. As in round 6, only GPT-6.1 Sol runs, at reasoning effort \`high\`, each arm once per run index in fresh sessions started about half a minute apart. Each accepted defect is measured again on the saved pages over \`file://\` with the network blocked, present when broken and gone when fixed, before the round is sealed.

One change to the inclusion rule. Round 6 accepted four cases of kinds the prompt does not ask for. In this round an accepted defect must be one of the kinds the prompt lists, and the answer key records which:

- content or text that is cut off, covered or overlapping;
- content that runs outside the screen or makes the page scroll sideways;
- a component that breaks into the wrong rows;
- an element misaligned with the siblings or container it belongs to;
- an element whose size does not match the element it is attached to;
- an icon or glyph off the centre of its control.

The 2 px floor for geometry faults stays, and the defect must be visible at a size the prompt names, 360 by 780 with touch emulation or 1440 by 900. The screening rejects text that reaches the screen edge without running past it, pages shrunk because they lack a viewport tag, tap target size and spacing, colour, contrast, wording, image content, faults that appear only on hover, focus or another interaction, and refinements after which the broken state still looks intended.

Two targets are registered for Sol, as in round 6: the registered rule (more known defects in all three paired runs, no more alarms plus unsupported findings, and at most 1.5 times the median time), and the skill arm's median time to the written report below the plain arm's.

The scan alone runs on every state as the agents would run it (\`--tiles 40\`), with the frozen skill and with the skill frozen for round 6 (commit e72a71c), on an otherwise idle machine.

## Changes after registration
1. Screening closed, 2026-10-23, before any round 7 run, with 9 cases from 403 judged candidates in 38 sources: 2 of 11 from Neubrutalism, 2 of 6 from PSone.css, 1 of 3 from cleopatra, 1 of 2 from notion.css, 1 of 6 from particle, 1 of 4 from the PlainAdmin template, 1 of 1 from startmin and none from the other 31. No source reached three accepted cases. Every candidate is listed with its verdict and reason in \`screening.json\`. All nine are one kind from the prompt's list, content that runs outside the screen or makes the page scroll sideways, all on a phone: no candidate of the other kinds survived the rule against refinements and design changes. Each defect was measured again on the saved pages over \`file://\` with the network blocked: present when broken, gone when fixed. The stop rule allows 12 cases, so the round runs 3 short. Four notes for scoring: the fixed state of PSone.css d368ab3f carries the 6 px title overflow that 047ad598 later fixed; on the startmin page the heading 'Buttons' is partly covered by the fixed navbar in both states; pictures from other sites are missing in both states; and the PlainAdmin page links \`LineIcons.css\`, which its repository stores as \`lineicons.css\`, so its icons are missing in both states. The answer key lists the first two under \`also_present\` and the last two among its notes.
2. The seeded shuffle (seed 2026102301) put cleopatra 1d67f504, PSone.css d368ab3f and startmin 00dfc439 in group A, PlainAdmin 7b537082, notion.css ff2c2912 and particle 891c4249 in group B, and Neubrutalism 3b935b37, PSone.css 047ad598 and Neubrutalism af223018 in group C, so each run shows 6 known defects among 9 pages. Sealed SHA-256 before any run: answer key 52a5285762e2bf1496d45a1e77d588c5d70ea12d1cc559a3e6cd53d940249916, page assignment 90109ab0b1ae53d2ad41b17ecbca5e7cf3a03451550e022d488236224659d3c7, run pages 4cc8a07ee8d9d1490aabac22f6e59688bad7e4931fb91a3ac357279f2d95a75a (285 files, hash of sorted path and file-hash lines), prompt templates as registered for round 2. Both frozen skill folders, this round's and round 6's, were checked against their manifests before sealing.
