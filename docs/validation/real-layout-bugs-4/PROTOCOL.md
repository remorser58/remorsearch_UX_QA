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

1. Screening closed, 2026-10-20, before any round 4 run, with 8 cases from 226 screened candidates in the 14 sources: 2 of 40 from simple.css, 2 of 9 from mvp, 3 from picnic (the source closed at three accepted after 27 candidates; its other 13 were not judged), 1 of 40 from mini.css and none from the other ten. Every candidate is listed with its verdict and reason in `screening.json`. Each defect was re-measured on the saved pages over `file://` with the network blocked: present when broken, gone when fixed. One candidate failed that re-measure: picnic 90a917a6 looked 669 px wide on the screening render, but the width came from an external comments script that the saved page cannot load, and both saved states are 366 px wide. It was rejected, and picnic screening went on in order to ec6a3d0d. The stop rule allows 12 cases, so the round runs 4 short.
2. Two pairs of cases share a page. The simple.css cases are consecutive commits of `index.html`, so both states of 36144b34 still carry the squeezed aside that c6af6463 fixes; the answer key lists it under `also_present`, and a report of it on that item counts as a valid extra. The two mvp cases are `index.html` at different commits with different defects.
3. The seeded shuffle (seed 2026102002) put picnic 8ae635b1, picnic 8bb0d652 and mvp 66ec5a39 in group A, mvp 11722ccc, mini.css 0ed75ca8 and simple.css c6af6463 in group B, and picnic ec6a3d0d and simple.css 36144b34 in group C, so runs 1, 2 and 3 show 6, 5 and 5 known defects among 8 pages. Sealed SHA-256 before any run: answer key 532bd0e6697d5857c6495645c46714f18e65bd56958ea3544e30f8485a704cc5, page assignment dfeaf27d6ec2609531b4d9d8ce8d72a9f5dee5d75c736ff5ff73b9190dbafe91, run pages a68d01bfd2bc6ccce55437034c07d06c15437f838ae653c161b7510d686a5b04 (165 files, hash of sorted path and file-hash lines), prompt templates as registered for round 2. The frozen skill folder was checked against its manifest before sealing.
