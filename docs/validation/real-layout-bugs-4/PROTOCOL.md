# Real layout bugs, round 4: preregistered protocol

Written 2026-10-20, after the candidate lists of the sources below were generated and their pages rendered for screening, and before any candidate was judged or any agent ran on these sources. Changes after this point are listed at the end with their reason.

## Question

Round 3 showed that the scan did not measure offsets between different kinds of elements side by side, and that all four arms missed those bugs. The scan now has LY-09 (a choice control against its label, a field against a separate button, items of a header or toolbar bar) and LY-10 (a squeezed content column on a phone). Those checks were built after seeing the round 3 misses, so rounds 1 to 3 are development pages. On new real layout bugs from projects no round used, does an agent with the skill find more of them than the same agent without it, without more false alarms and within the time budget?

## Skill under test

Commit 51240ed of branch `codex/v1.0.1`, installed once with `scripts/install.py --no-prompt` into an isolated folder (payload SHA-256 `ebbc8b542f3df48b74ed45693df31e501f878a49486556ad38d1a45bdcc05d4f`). No skill or detector file changes until every round 4 run is scored.

## Sources

Sixteen repositories cloned on 2026-10-20 for this round, none used in rounds 1 to 3. Fourteen have HTML pages and built CSS committed next to each other and are screened in this order: kevquirk/simple.css, andybrewer/mvp, kognise/water.css, oxalorg/sakura, xz/new.css, jenil/chota, franciscop/picnic, mblode/marx, yegor256/tacit, dhg/Skeleton, milligram/milligram, Chalarangelo/mini.css, DesignRevision/shards-dashboard, creativetimofficial/now-ui-kit. egoist/hack and creativetimofficial/argon-design-system were dropped before screening: hack commits no HTML page and argon-design-system has no commit matching the candidate rule.

## Rules

Candidate rule, inclusion rule (with the 2 px floor for geometry faults), per-source limits (3 accepted or 40 screened), stop rule (12 cases), page items, the seeded split and three-run rotation, arms (GPT-6.1 Sol and DeepSeek 4.1 Flash at reasoning effort `high`, each arm once per run index in fresh sessions), the round 1 prompt templates byte for byte, the 30-minute budget, scoring blind to arm and model, and the decision rule are as registered for rounds 2 and 3. The scan alone runs on every state as the agents would run it.

## Changes after registration
