# Real layout bugs, round 5: preregistered protocol

Written 2026-10-21, after the candidate lists of the sources below were generated and before any candidate page was rendered or judged, and before any agent ran on these sources. Changes after this point are listed at the end with their reason.

## Question

Round 4 left three kinds of bug unmeasured and a slow scan. The scan did not compare the widths of fields stacked in one form, did not measure the gap between adjacent links and did not notice menu items hanging below a fixed bar. No run of either model found the textarea narrower than the field above it, with or without the skill, and the other two bugs were each missed in some runs. A scan of eight pages took several minutes on an idle machine and much longer while six agents ran; in two of three runs the cheaper model wrote its report before the scan finished. The scan now has LY-11 (stacked fields of different widths), LY-12 (labels of adjacent links or buttons that touch) and LY-13 (an item of a header bar hanging past its edge). It records a page about three times faster than before and with less than half the CPU time, mainly because the in-page measurement no longer calls the font check once per text, crops are cut by the Node driver, the phone scrolls with the wheel, the scan skips the keyboard focus walk unless asked, and its steps stop at the end of the page. The new checks were built after seeing the round 4 misses, so rounds 1 to 4 are development pages. On new real layout bugs from projects no round used, does an agent with the skill find more of them than the same agent without it, without more false alarms and in less time?

## Skill under test

Commit ac1a1876bd0fc44c0c7bdfd9f3f242bac0ad09b0 of branch `codex/v1.0.1`, installed once with `scripts/install.py --no-prompt` into an isolated folder (payload SHA-256 `5ad5c82dda227ae2bc400d780f77ec055fc545a4989ca1ad66f2b646688cf7ae`). No skill or detector file changes until every round 5 run is scored.

## Sources

Twenty-one repositories cloned on 2026-10-21 for this round, none used in rounds 1 to 4. Each has HTML pages and built CSS committed next to each other. Round 4 found its cases in small CSS frameworks with demo pages, so this round takes more of those; the choice was made after seeing round 4's yield and is stated here for that reason. Screened in this order: edwardtufte/tufte-css, GumbyFramework/Gumby, topcoat/topcoat, ajusa/lit, rilwis/bamboo, programble/writ, alvaromontoro/almond.css, kristoferjoseph/flexboxgrid, stisla/stisla, emareg/classlesscss, Kimeiga/bahunya, bootflat/bootflat.github.io, vincentdoerig/latex-css, vladocar/Basic.css, StartBootstrap/startbootstrap-stylish-portfolio, StartBootstrap/startbootstrap-modern-business, StartBootstrap/startbootstrap-simple-sidebar, creativetimofficial/material-kit, creativetimofficial/paper-kit-2, adminkit/adminkit and sindresorhus/github-markdown-css.

Ten more repositories were considered and dropped before screening. jdan/98.css, botoxparty/XP.css, Spiderpig86/Cirrus and kbrsh/wing hold no HTML page in their current tree; twbs/ratchet and turretcss/turretcss keep their pages as site-generator templates; the lowlighter/matcha page links a stylesheet that a build step produces; the nostalgic-css/NES.css demo page loads the framework's stylesheet from a CDN at its latest version, so an old commit does not render its own CSS. igoradamenko/awsm.css and vasanthv/stylize.css could not be cloned (repository not found).

## Rules

Candidate rule, inclusion rule (with the 2 px floor for geometry faults), per-source limits (3 accepted or 40 screened), stop rule (12 cases), page items, the seeded split and three-run rotation, arms (GPT-6.1 Sol and DeepSeek 4.1 Flash at reasoning effort `high`, each arm once per run index in fresh sessions), the round 1 prompt templates byte for byte, the 30-minute budget, scoring blind to arm and model, and the decision rule are as registered for rounds 2 to 4. Each accepted defect is measured again on the saved pages over `file://` with the network blocked, present when broken and gone when fixed, before the round is sealed.

One secondary target is registered for this round: for each model, the skill arm's median time to the written report is below the plain arm's. It is reported next to the registered rule and does not change it.

The scan alone runs on every state as the agents would run it, with the frozen skill and with the skill frozen for round 4 (commit 51240ed), once while agents run and once on an otherwise idle machine for timing.

## Changes after registration

