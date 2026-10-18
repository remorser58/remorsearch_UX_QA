# Research engine contract

Contract revision: `research-engine-2026-10-01.1`. This is the normative contract
for the implementing package. This package implements the engine, documentation and schemas. Agents check command help before use. An absent command means
a labelled manual assessment with unverified research claims; a manual assessment
cannot produce a gate pass or composable research audience.

## 1. Scope and decisions

Implement merge, gate, gate --write-bundle, report-check, export-audience,
minimize and audience-check --gate --bundle. Keep the existing reader access
policy, fit table, claim kinds, thresholds and status names. Cut discovery APIs
and automatic team-export scrubbing. The agent logs each allowed host search
call and asks the producer for a reviewed sanitized export. Stops remain gaps.

Choose the stricter reading for privacy and evidence integrity: refuse unknown
provenance, do not invent independence, do not establish currency without dates,
retain contrary evidence, and keep population bounds separate from product shares.
Corrections to the previous references:

- Conflict and currency precede support, including product observations.
- Empty non-product support is lead_only; it is not vacuously all E.
- Single-institution B is medium only for statistical sources. Other single
  institutional B evidence is lead_only.
- Observation-only product_behavior needs no dummy source or evidence.
- Original support inputs survive output partitioning, allowing idempotent regrade.
- Export produces ux-audience-draft.v1, never an incomplete ergo-audience.v1.
- bundle_ref remains a source-ID string; typed value joins carry claim provenance.
  News remains secondary research context and is withheld from automatic export.
- Personal protected attributes are refused over their connected graph, even
  when keys have been removed from the excerpt itself.

## 2. Files and ownership

Paths are relative to an existing run unless explicitly supplied. The engine
makes no network request and does not modify hashed reader policy. It verifies
run.json, brief.json, routes.json, agent-tokens.json, hosts.json and
access-ledger.jsonl using the existing reader policy.

| File | Writer and meaning |
| --- | --- |
| axes.json | Agent, before dispatch: ux-research-axes.v1 manifest below |
| axis-acknowledgements.json | Agent: missing/partial/excluded coverage acknowledgement |
| search-ledger.jsonl | Agent: actual search invocation receipts, including failures |
| returns/*.json | Reader: ux-reader-return.v1, original and expansion returns |
| sanitized-imports.json | Producer-reviewed provenance and sanitized text paths |
| bundle.json | Merge; agent input annotations; gate derived verification |
| query_log.json, expansion_log.json, merge_receipt.json | Merge counts, coverage and provenance proof |
| gate.json or gate_failed.json | Gate only; never two current results |
| audience.draft.json, audience.todo.md | Exporter: supported values and explicit missing data |
| report-claims.json | Agent/reviewer: statement mapping |
| report_check.json | Checker: mechanical report results |
| bundle.min.json, minimize.json | Minimizer: loop projection and removal manifest |
| engine-state.json, .engine/ | Atomic manifest, committed snapshot and staged snapshot |

axes.json is `{schema_version: ux-research-axes.v1, run_id, axes, segments,
question_gaps}`. A question gap is `{question, reason, acknowledged_by,
acknowledged_at}` with a brief question name and agent/owner acknowledgement.
No unrequested questions or implicit coverage; question_gaps can be empty.
Each axis is `{axis_id, audience_questions, excluded, reason, assignments}`.
axis_id is a slug; questions are the eight string names from the brief, not
display numbers. Assignment is `{assignment_id, reader_id, round, purpose}`; globally
unique assignment IDs, rounds 0–2. Included axes have a round-0 assignment;
excluded axes have a reason and no assignments. Requested questions not covered
need explicit question gaps. Freeze original assignments at first merge;
expansion and counter-search assignments are append-only and frozen at the next merge.
Purpose is discovery/expansion/counter_search. Discovery is round 0; expansion
rounds 1–2. Counter assignments use round 0 and do not create a third expansion
round. For new counter sources after merge, declare a new counter assignment,
return its checked evidence, and remerge with all prior returns before gating.
Unchanged receipt-checked quotes can be reused in an open-run remerge after page
TTL; new/changed quotes always require the actual captured text.

Segments are `{segment_id, priority, decision_ref, summary}`; priority is
primary/secondary/edge and comes from an owner/product-brief decision, never
post volume. No default primary. Unknown segments can be explored, not exported.
Priority changes need a manifest revision and new gate, not a reader-policy edit.

Acknowledgements use the single discriminated definition in section 18.
Unacknowledged missing/partial assignments exit 1; excluded/unexpected returns,
changed assignments or incompatible acknowledgements exit 2.

## 3. Reader returns and sanitized imports

### 3.1 Return model

Use ux-reader-return.v1.schema.json. Required fields: schema_version, run_id,
return_id, axis, queries_run, search_count, sources, excerpts, candidate_claims,
expand_leads, dead_ends, tail_reason, gaps and budget_used. Reject extra fields.
axis contains axis_id, assignment_id, reader_id, round, part_index, part_count,
completion and audience_questions. Parts start at 1; complete harvest needs every
part and all completion values complete. Partial evidence can contribute after
acknowledgement, but coverage stays partial. Local IDs are namespaced by assignment
and part. Identical repeated returns count once. Same return_id with changed
canonical bytes, overlapping different parts or changed part_count exits 2.

Sources require local_id, title, url (null for imports), item_key (null for whole
page), source_type, source_family, producer_stake, platform_family, org, author_key, thread_key,
published_at, observed_at, valid_at, version, access_method, access_basis,
public_scope, retention_status, retention_until, privacy_class, promo_check,
flags, provenance and access. Unknown dates/identities are null. published_at and
valid_at are dates; observed_at/deadlines are UTC timestamps. Family must match
the source-type mapping in source-grading; none covers llm_output/synthetic.
platform_family is the route's channel family or the source type outside routes.
org is a normalized producing institution key, not a person's name.
producer_stake is official/independent/vendor; survey with vendor stake is estimate,
otherwise measured. The field does not change other source-type mappings.

Reader provenance is `{kind: reader, fetch_id, content_sha256}`; access copies
rung, presentation, verdict, stop_class, fetched_at, robots, context and terms.
Normalize ledger null stop to none. Import provenance is `{kind: import,
import_id, content_sha256}` with access null. These alternatives are exclusive;
never invent a fetch_id for a team export. item_key selects an actual captured comment/review/table only when capture-bound
item attestations bind its scrubbed excerpt and author key. Without that attestation,
record item_key and author_key as null, identity unknown, and use the whole page or
thread as one independence unit. `[author]` and `---` are hints, never identity proof.

Flags explicitly contain booleans secondhand, unclear_context, count_only,
seller_managed, own_brand, community_modelled_demographics,
protected_attribute_cue, polarity_uncertain; lead_kind full_text/snippet/teaser/summarizing_fetch;
and typed promotion_hits, incentive_hits, virtual_person_hits, injection_flags.
Hits have id, code and position lead/body/tail/unknown. They are candidates, not
verifier decisions. Combine source and excerpt flags; excerpts cannot subtract.

Excerpts require local_id, source_local_id, capture_ref, exact scrubbed excerpt,
authored summary, evidence_type (firsthand/quantitative/statistic/official/inference),
epistemic_status, flags, scope, cues and nullable denominator. Cues have nullable
segment/context/task/condition/device. Scope is `{product_relation, population,
period_start, period_end, version, segment_id, context_id}`; relation is
product_users/general_population/comparable_product/product_surface/product_intent/
unknown. Quantitative support needs the denominator in section 6.

Candidate claims require local_id, claim_kind, statement, excerpt_ids,
counter_excerpt_ids, context_excerpt_ids, observation_ids, subject, scope,
about_current_version, stakes, scenario_priorities, audience_values and nullable
counter_search. Subject has nullable segment_id/task_id/condition_id/context_id/
pain_point_id; stakes normal/high, scenario priorities P0–P3. Empty evidence is
legal. Readers cannot choose verification, grade, status or confidence.

### 3.2 Import model and refusal

sanitized-imports.json is `{schema_version: ux-sanitized-imports.v1, run_id,
imports: [...]}`. Each import is `{import_id, artifact_ref, content_sha256,
source_type, producer_org, acquisition, sanitization, retention_until}`. artifact_ref
is a safe run-relative mode-0600 UTF-8 text file, not a raw spreadsheet, absolute
path or symlink. import_id is IMP- plus the full SHA-256 of canonical sanitized
bytes hash and acquisition metadata excluding import_id. content_sha256 hashes
the exact sanitized bytes.

Acquisition requires kind (voc_export/analytics_export/store_console_export/
support_export/survey_export/document), product, nullable app_id/territory,
exported_at, period_start, period_end and permission_ref. Own-app console exports
require app_id, territory and permission for that app. VOC keeps its real source
type: curated store reviews remain app_store_reviews, not measured analytics.
Anonymous ticket counts remain count_only without a neutral sampling frame.

Sanitization requires performed_by producer/owner, method producer_redaction,
reviewed_at, removed_categories and review_attestation true. Producer removes
names, handles, profiles, contact/payment/account/government identifiers, full
and partial IPs, reverse-lookup row IDs and unneeded private data. Human review
covers plain names. Aggregates expose no individual rows. Justified run-specific
pseudonymous keys have no supplied reverse map.

The engine never repairs a raw team export. It scans sanitized text and metadata
with reader identifier/injection rules, then refuses residual identifiers,
unreviewed sanitization or protected individual attributes. Privacy process
errors exit 1; malformed/invented provenance exits 2. Never print refused text.
Check quotes/flags against the sanitized artifact. Source_ref is
team-import://<run_id>/<import_id>, basis team_provided, method team_export.
Imports have independent provenance receipts and consume no page/search budget.

## 4. Deterministic merge

### 4.1 Authoritative provenance

Require an open unchanged reader run with fresh user terms checks. Snapshot the
ledger under state.lock. A fetch_id must identify a successful outcome from read
or ingest, bucket read, verdict ok_strong/ok_weak, no stop, with captured text.
Policy request IDs, unread/refused/deferred outcomes and an earlier HTTP 200
before a later stop are insufficient. Validate request/ingest and redirect trail.

Match masked requested URL to return URL; validate final URL and every hop under
policy. Tracking normalization does not permit relabelling a capture. Match basis,
capture tool/context, rung/presentation, fetched_at/observed_at, robots and terms.
Official_api requires a packaged adapter success; signed-in requires applicable
brief authorization. lift_requires alone decides liftability; status records
evidence quality. Every overlapping terms entry must allow the route.

Hash exact scrubbed UTF-8 page bytes and match ledger/provenance content_sha256.
Rescan pinned markers. Returns cannot omit injection/disclosure flags or alter
retention. Complete safe capture metadata must be retained or reconstructed from
scrubbed page and reader result before merge: ledger flag counts alone cannot
clear candidates. Capture receipts record authoritative metadata and effective
flags. Inferred secondhand/context flags need verifier review if disputed.

Normalize quote/page to NFC; collapse Unicode whitespace to one ASCII space and
trim. After reapplying the reader identifier scrubber as a backstop, quote must
be a contiguous substring of that captured item. Preserve placeholders and record
replacements. At most 300 normalized Unicode code points per quote, five distinct
excerpts per resource per run. Paraphrases belong in summary. Invented quotes,
unknown capture/changed hashes exit 2; length/privacy violations exit 1. New
quotes cannot merge after page purge/close. Existing receipt-checked quotes can
be regraded without retaining page text forever.

### 4.2 URLs, captures and conflicts

Normalize scheme and IDNA host case, trailing host dot/default port, percent
escape case; decode unreserved characters and drop fragment. Preserve path case,
trailing slash, query order and duplicate keys. Remove only case-insensitive
utm_*, fbclid, gclid, dclid, msclkid, mc_cid, mc_eid. Preserve id/page/ref/search
and other routing parameters. Reject credentials/unmasked secret parameters;
masked secret collisions never prove identity.

Use final URL only when the successful ledger trail proves it. Do not equate
http/https, www/apex, m./desktop or canonical HTML hints automatically. Mobile
twins merge only with an exact pinned route resource-ID rule or proven redirect.
Retain aliases; identical text alone never merges sources.

Resource identity is `(run_id, normalized resource URL or import_id, item_key)`.
Keep successful captures separately. Latest fetched_at wins the whole source
header; tie-break by smallest capture_ref. Do not choose convenient fields from
different captures. Evidence retains its exact capture_ref and that capture's
dates/flags/access for grading. Rereading cannot launder old flags/currency or
erase counters. Confirmed gone/deleted/withdrawn/policy-revoked resource makes
all captures ineligible; network failure alone is not deletion. Different metadata
for the same capture exits 2. Two different non-null author/producer identities
for one resource in one run are refused; investigate in a new run. A later known
identity does not fill an earlier capture's unknown identity. Date changes across
captures remain separately visible with a warning.

### 4.3 Stable IDs and independence copies

Use SRC-/EV-/CLM- plus eight lowercase hex characters from SHA-256 of canonical
identity tuples. Source: resource identity. Evidence: `(run_id, source_id,
capture_ref, capture content_sha256, normalized quote, item_key)`. Claim: `(run_id, claim_kind,
normalized statement, subject, scope, audience joins and values)`. Scope/wording/value changes
create a new claim ID; support additions do not. Sort audience_values by join.
Receipt stores the full SHA-256 digest of the canonical identity tuple.
Compare actual tuples before coalescing. Proof references and value checks are
excluded from claim identity and included in the input hash. Unequal tuples with
the same short ID refuse the whole merge, exit 2 id_collision. No suffix,
renaming, additional commitment or collision migration is permitted. Equal tuples
coalesce only when other metadata agrees; union compatible reference sets,
preserve histories, refuse conflicting metadata.

SHA-256 of normalized quote text defines copypaste_group. Exact normalized copies
count once even across authors/channels; punctuation/language changes are not
automatically duplicates. Preserve all original records/links. Union shared
identity and copy-paste into independence components; each supplies its best
eligible grade. One component cannot supply two channels. Representative selection:
best grade, then earliest capture, then evidence ID. Others become context.

### 4.4 Harvest, queries and expansion

Search receipt shape: call_id, tool, called_at, phase discovery/expansion/
counter_search, queries array of `{q, lang}`, results_n nullable, outcome
completed/failed/interrupted, assignment_id. queries_run and search-ledger.jsonl
use the same shape. Agent assigns Q- plus 16 lowercase hex before each actual
call. A multi-query batch is one invocation; retries/pagination/failures/interruptions
count separately. Record each query string within a batch. Merge never searches.

Union all part/round/counter call IDs, compare to search ledger. Shared actual
calls count once; identical query text in separate invocations counts again.
Duplicate receipts must agree canonically. search_count/budget_used.searches
equal each return's unique count. Missing/unattributed calls/count mismatches
exit 1; invented/conflicting receipts exit 2. A reviewer compares attested logs
to host transcripts; an uninstrumented tool cannot prove no hidden search occurred.

budget_used includes request_fetch_ids/document_requests/policy_requests. Count
charged document requests, escalations, redirect requests and API calls, plus
booked renders once; outcomes never count again. Robots are policy requests,
not page budget. Reconcile global unique request IDs with ledger and hosts.json.
An unmatched crash reservation remains charged and needs acknowledgement as
unattributed_request. Local imports do not count. query_log records receipts,
duplicate text, phase/assignment totals, document/policy counts and mismatches.
Warn at total >= ceil(0.8 * search_queries); over budget exits 1.

At most two expansion rounds. Dedupe leads by normalized URL, otherwise NFC/
whitespace/case-folded text, including previously rejected leads. expansion_log
records assignments, agent-attested new segment/problem keys, leads/rejections,
gaps and stop reason no_leads/two_rounds_without_new/round_limit/budget. Empty
expand/dead-end tails require tail_reason. Missing expansion returns obey the
same acknowledgement/harvest rule as original returns.

### 4.5 Output and receipt

Write unverified claims, rewrite typed links, sort record arrays by ID. The root
research envelope contains contract_version, run_id, manifest, log digests,
merge_receipt_sha256, rules_version, verifier_decisions, scope_resolutions and
gaps. Each claim preserves research_support_evidence_ids and
research_context_evidence_ids as original inputs, separate from gate output
partitions. Counter history cannot be removed to obtain support. Committed engine
receipts keep append-only counter links/search outcomes from merge/gate snapshots.
Gate rejects removals against that history except retention purge; typed
resolutions retain contrary links. New proven counter annotations join history at their
first gate, including a process-failed gate. Invalid/unproven references never
become permanent contrary facts. Reader counter-search source/evidence and
denominator refs are local IDs until merge rewrites them; bundle annotations use
global IDs.

merge_receipt records ID commitments, capture metadata, flags, excerpt hashes and
rewrites without raw page text/personal identifiers. It is committed in a private
engine generation; a bundle-local claim that a quote was checked is insufficient.
Without an external committed receipt, research grading refuses.

## 5. Privacy and retention over the graph

### 5.1 Protected-attribute unlinking

privacy_class is ordinary/aggregate/protected_individual; the last is refused.
Skip apparent minors' personal content. Ordinary evidence cannot bind age, race,
religion, politics, sexual orientation, health, disability or other protected cues
to person/thread. Check its entire connected component: source_ref, item_key,
aliases, source/evidence keys, claims, audiences, lexicon examples and reverse
references. An excerpt stripped of keys still identifies its author through an
author-bearing source/post locator. Salted keys are identities for this rule.

Unlink by removing personal sources, all their excerpts/keys/locators and reverse
links, including other sources sharing those keys, from deliverable graphs. Keep
only a generic privacy gap; shared output cannot map protected cues to removed
IDs. An unlinked segment-level hypothesis with no source/person/thread pointer
and empty support is permitted and remains lead_only. Do not manufacture an
aggregate from personal posts to preserve grades. Genuine deidentified team
aggregates or institutional statistics can support protected segments when no
personal keys/individual locators exist anywhere in their component and their
aggregate content/frame was reviewed. Privacy errors exit 1 and block content
outputs until corrected. The engine refuses rather than silently performing an
unreviewed privacy rewrite. Agent removes the component and resubmits.

Shared member/API evidence is authored summary only without post/video/comment
IDs. Health/disability/older-adult/minor channels get no shared quotes. Scrub
summaries and metadata too. Diagnostics never reproduce rejected personal text.

### 5.2 Expiry and repair

Every merge, gate and consumer rechecks UTC now against all reachable deadlines,
including context/counter/non-counting/import material. Official API deadlines
come from ledger/packaged routes. A legacy bare date expires next UTC midnight;
new records use timestamps. Equality is expired. No live clock override; tests
inject a clock through an implementation API.

Merge and gate --write-bundle purge expired content before assessment. Source
tombstone allowlist: id, channel expired, source_ref expired://<source_id>,
access_basis redacted, access_method retention_purge, public_scope none,
retention_status deleted, research_tombstone `{reason: expired, removed_at,
prior_access_basis}`. No original title/URL/keys/API/item IDs/hash/flags/payload.
Confirmed deletion, withdrawal or policy revocation uses the same content/link
repair with reason deleted/withdrawn/policy_revoked, channel redacted,
source_ref redacted://<source_id>, method content_purge and status withdrawn
only for withdrawal, otherwise deleted. These gaps use evidence_unavailable.
Purging preserves historical record IDs even when an expired derived statement
is replaced by generic unknown wording; the committed purge receipt authorizes
this specific exception to normal claim-identity recomputation.
Evidence tombstones keep id/source_id/evidence_type, epistemic_status unknown,
summary `Evidence removed at retention expiry.`; no content/hash.

Remove tombstoned IDs from all support inputs/output/context/counter lists,
counter read sources and export bindings. Private gap: `{code: evidence_expired,
affected_claim_ids, removed_evidence_ids, counter_gap, note}`. Downgrade dependent
claims to unverified/unknown before recomputation. Removed contrary evidence makes
a sticky counter_gap: conflicting, process exit 1 until a new completed
counter-search explicitly replaces it. Expiry cannot resolve a contradiction.
Empty non-product support becomes lead_only; product claims use remaining
observations or need a product check. Strip expired API content derived into
statements/values/summaries; retain generic unknown wording, never derived quotes.

Read-only gate refuses expired input with exit 2/gate_failed and directs a purge
with --write-bundle. Consumers refuse expiry with exit 2 and no content output.
gate --write-bundle commits privacy purge even if grading fails: purged unverified
bundle plus gate_failed. Otherwise failed gating does not write derived statuses.
Reread creates new capture/deadline; refresh only quotes rechecked against its
bytes. Copying a date does not refresh evidence or decisions.

The temporary-page 72-hour TTL is separate. Receipt-checked unchanged evidence
can be regraded after close; edited quotes need a new capture. Purge expired
material from engine generations/receipts/caches too, not only convenience files.
Owner removes/regenerates already shared artifacts; engine identifies affected
artifacts but cannot erase external copies.

## 6. Total grading and precedence

### 6.1 Fit and downgrades

The fit table/vocabulary in source-grading.md is normative. Pin rules_version
source-grading-2026-10-01.1 and rules/markers/suffix/organization-alias digests.
None-family evidence is E; unknown enums/malformed data are hard errors, not
fallback grades. Counting requires observed evidence; inferred/unknown inputs
stay context even with fit A/B. Apply missing publication date, secondhand, unclear context and
authorized member access as independent one-grade steps clamped at E, then every
cap; lowest wins, never raise a grade. Record all reasons.

Confirmed promotion/seller tie caps D; confirmed virtual person, uncleared
injection, stopped/deleted/withdrawn, LLM or synthetic source is E. Leads and
modelled community demographics cap D. Device cues are no device_mix support.
Count-only is E for size/population kinds. Counting voice support for any size/
population value is exit 2 even with measured support present; voice context is
permitted. These strict numeric checks also apply to weights/frequency, whatever
claim_kind the author chooses.

Confirmed incentives cap preference/satisfaction, counter-search use and star
averages D. For pain_point/workaround an incentive alone caps voice B at C; it
does not lower already downgraded C further or raise D/E from another rule.
Seller notices/platform points require the reviewer's own event trace and
excerpt decision; a notice alone never caps all reviews. Self-declarations do
not clear flags. Uncertain polarity cannot support satisfaction/preference or
qualify a counter result. Seller-board silence is not a counter result. Own-brand
review cap D is restored only after an independent A/B from another channel
survives every other cap. Compute external corroboration first; own-brand items
cannot supply their own corroboration. Normal support thresholds still apply.

Voice identity is an attested author_key, otherwise an attested thread_key.
Without item/author attestation, use the captured whole page/thread as one unit
with identity unknown; never infer a person from placeholders or separators.
Missing provenance for even that page/thread caps D, zero independent units. Default anonymous nicknames/
partial-IP handles require thread keys, all replies in a thread count once.
Institutions/measurements use producing org, normalized with pinned aliases and
registrable-domain rules where identifiable. Statistics portals need the producing
agency, not portal. Unknown producer caps D; repeated datasets from one org do
not become independent organizations. Blogs count per author. Missing channel
identity caps D. Privacy-redacted identities cannot count as people.

Union identity and copy-paste into components; each contributes best eligible
grade. Repeated means two people. Corroborated means two components across two
channel families, or two components of which one has measured/statistical B.
One measured A suffices. A copy component cannot supply two families. Per
author/thread across the run: three sources/five excerpts maximum, counting all
distinct items even called context. For this cap, an excerpt is the distinct
pair (resource source ID, normalized quote); repeated captures of that pair count
once while every actual reader request still counts. Separate capture_ref evidence
IDs preserve flags/retention and prevent a reread from replacing an older counter.
Duplicate returns do not charge again.
Excess exits 1; run-local keys cannot be joined across runs.

### 6.2 Denominators and bounds

Denominator is `{population, period_start, period_end, product_relation,
sampling_frame, n, method, unit, value_as_printed, interpretation}`. n is a
positive integer or null for defined census population; interpretation is
product_measure/population_bound/comparable_estimate. Other fields are nonempty;
dates form a real, non-future reference period. Match stat_card and evidence
scope. A general population statistic stays population_bound, even official B;
never retag product_measure or export as a product share. Draft bounds are separate.
Comparable estimates name the comparable product, period and relation to the
target; they map to estimated, never measured. Vendor-stake surveys use estimate.

Size/population support needs quantitative/statistic evidence with neutral frame:
analytics, sampled population with n or a defined population study. Post/review/
like/complaint counts, star averages and self-selected responses without a frame
are not denominators. Missing/incompatible denominator for numeric support exits 2.
Statistical sources need stat_card frame/reference_period. Existential measured
evidence need not have n. Numeric age/device/grip/familiarity weights, condition/
context shares and task frequency undergo these checks regardless of claim label.

### 6.3 Currency and observations

about_current_version requires brief release_date. Missing date yields stale
and process exit 1, including observed product claims. Effective date is valid_at/
explicit version or measurement period, falling back to published_at; observed_at
is a read date, never version truth. Unknown dates cannot establish currency.
For current-version claims old/undated items become context. The stale predicate
is about_current_version && (missing_release_date || no_current_potential_support).
Historical claims are never stale for that reason. Mixed old/current uses only current items. A product run
needs matching version or recorded execution on/after release, plus matching
product surface and typed task/context/version scope.

Only product_behavior can verify solely from observation_ids. Every counting
observation is observed with substantive result and scope; run completed with
existing same-scope scenario. Interrupted/inferred/unrelated runs do not count.
Synthetic personas may be test inputs to real product observations, never support
real-user shares/preferences/prevalence. Observations on pain_point establish
product conditions only: create product_behavior separately, do not raise the
users' existence/population grade.

### 6.4 First matching status

Assess every well-formed claim after integrity/process checks. A pass may contain
unsupported claims. Hard errors outrank process errors; failed assessed rows are
not consumable. Conflict/currency always precede support.

| Order | Condition | Status |
| --- | --- | --- |
| 1 | Unresolved counters, counter_search contradicts, or sticky expired-counter gap | conflicting |
| 2 | about_current_version && (missing_release_date || no_current_potential_support) | stale |
| 3 | product_behavior without eligible linked observation | needs_product_check |
| 4 | product_behavior with eligible observed completed runs, no earlier blocker | supported_high |
| 5 | Non-product nonempty inputs all assessed E | unfit |
| 6 | Empty inputs or no eligible A/B | lead_only |
| 7 | One A, or two B components corroborated above | supported_high |
| 8 | Two B voice units (people/threads) one channel; B plus independent C another channel; or one statistical B with producer | supported_medium |
| 9 | One B voice person/thread; same-channel C does not lift it | single_voice |
| 10 | Remaining cases, including one non-statistical institution B | lead_only |

best_grade is best eligible source support or null for empty/observation-only
claims. Product observation support does not invent a source A. Only supported
high/medium maps verified/epistemic observed and confidence high/medium. Others
map unverified. Captured evidence may remain observed while a claim is inferred/
unknown. D/E, old and surplus component items become context. Counters never
turn into support merely because their grade is high.

## 7. Counter-search, scope changes and verification

### 7.1 Triggers and receipts

Union canonical triggers: subject.segment_id joins primary manifest segment;
stakes high; non-null audience_value sets a share/weight; scenario_priorities
contains P0/P1; or a scenario priority/motivation_claim_ids joins this claim at
P0/P1. No segment_hint/free-text/omitted boolean cancels a trigger. Scenario-use
lists must agree; disagreement exits 1.

counter_search is `{call_ids, read_source_ids, counter_evidence_ids, outcome,
summary, resolution_id}` plus optional replaces_call_ids. Outcome is
none_found/qualifies/contradicts. Calls join
completed counter_search receipts; failures/interruptions do not satisfy it.
Read sources must be registered and actually read through reader or sanitized
import. Contradicts requires a linked counter excerpt except a proven engine
purge gap. Replacing an expired/unavailable counter requires replaces_call_ids
exactly matching that prior search, and new completed call IDs timestamped after
the source removal; a note alone cannot clear the sticky gap. Keep gap/history
visible after replacement. Qualifies requires a
typed scope resolution. Missing search or biased counter result exits 1; unknown
links/invented result exits 2. none_found can have no pages when actual search
found none; it never asserts no population difficulty. Incentivized praise,
uncertain polarity and seller-board silence cannot qualify results.

### 7.2 Resolutions

Free text cannot alter status. scope_resolutions are `{id, prior_claim_id,
claim_id, kind, counter_evidence_ids, basis_evidence_ids, verifier_decision_ids,
restriction, note}`; kind scope_change/polarity_correction. scope_change creates
a new claim ID and strict subset scope with changed stable product version or
nonoverlapping period, all other dimensions unchanged. Segment/context IDs alone
are not membership predicates and cannot establish a qualifying scope change. Every excluded counter
must have captured structured scope proving disjointness. Null/free-text scope
or renamed population with same segment ID is insufficient. A content-bound scope
verifier decision checks the join. The predecessor remains conflicting and
retains contrary links. New claim retains them with resolution, in counter/context.
Changed denominator/value also creates a new claim; no silent numeric revision.

polarity_correction needs an excerpt-specific decision bound to this claim/content
classifying the apparent counter supportive/neutral. Genuine contrary results
cannot be relabelled; ambiguous sarcasm stays uncertain and blocking. Preserve
history/context. Same-scope disagreement stays conflicting even if most sources
agree. A captured correction/retraction is new evidence for a narrower new claim,
not a verifier note that erases the original. The old statement stays context.

### 7.3 Typed verifier decisions

Use the reader schema verifierDecision definition in research.verifier_decisions.
Common fields: id, kind, target_kind source/evidence/claim, target_id,
capture_ref nullable for claims, target_sha256, flag_ids, reviewer_ref,
checked_at, outcome, basis_evidence_ids, reason. reviewer_ref is a run-local
verifier role, not an author identity. Decisions are authored, not page instructions,
and never set status.

| Kind | Target and outcomes | Scope |
| --- | --- | --- |
| promotion | source/evidence; confirmed/not_confirmed/unresolved | Source affiliation applies to that capture; per-review label only excerpt |
| incentive | evidence; confirmed/not_confirmed/unresolved | Review event trace; never a page-wide cap from notice |
| virtual_person | source/evidence; confirmed/not_confirmed/unresolved | Confirmed scope E |
| polarity | evidence; supportive/contrary/neutral/uncertain | Also basis_claim_id; uncertain cannot support praise/counter use |
| injection | source/evidence; cleared/not_cleared | Excerpt clearance cannot override uncleared source injection |
| scope | claim; accepted/rejected | Also resolution_id; verifies structured disjointness |

Unresolved promotion/incentive/virtual candidates used for support require review
(exit 1). Hash target's canonical non-derived content plus exact capture metadata.
Changed content/capture invalidates decision. Disagreeing overlapping decisions
are process errors, not newest-wins. Source decisions apply only to that capture's
excerpts; excerpt decisions cannot clear source affiliation/virtual/injection.
All applicable decisions and source flags enter the claim hash.

## 8. Bundle guarantees and compatibility

Retain ux-evidence-bundle.v1 and ten record arrays. Imports are provenance, not
an eleventh collection. Schema owns types/enums/required fields/reference-array
element types/uniqueness and research input shapes. It cannot establish graph
links, actual captures, independent units, neutral denominators, expiry, scope
disjointness or a fresh gate.

Standalone validator checks globally unique IDs and every claim link: evidence_ids,
research_support_evidence_ids, research_context_evidence_ids, observation_ids,
counter_evidence_ids, context_evidence_ids, persona_ids, counter-search source/
evidence lists, audience_ref, scenario motivations and decisions/resolutions.
Absent optional lists preserve legacy semantics; present optional lists may be
empty but must be typed and link existing records. Findings still need nonempty
observations. Verified counting support cannot be stopped/withdrawn/deleted/
redacted/lead/LLM/synthetic. Size/population claims need observed quantitative/
statistic support, eligible sources and complete frame/period. Validate tombstones;
retained expired content is always an error.

Research recognition is root research OR any access/provenance/original-support
markers OR linked research-origin records. Research claims can have empty source
evidence before observations. Verified research product_behavior needs eligible
observed completed same-scope observation_ids and may have evidence_ids empty.
Other verified research claims need nonempty observed eligible evidence. Gate
owns grades/process/currency/counters/independence/value eligibility. A bundle
verified flag alone never certifies a gate.

Legacy QA without research markers remains structurally valid, including the
existing verified product fixture. Observation-only product claims may pass with
observed completed same-scope runs. A verified legacy product_behavior without
those observations is a plain-validator warning and is refused by research
consumers. Optional present fields are checked even in legacy records.
Research consumers refuse legacy without authoritative receipts; deleting an
envelope cannot bypass gate because linked markers and external receipt are
required. Fixtures grade only in explicitly fixture runs and cannot export as
real research. audience_ref requires synthetic basis and known claims;
segments_affected is a unique string array, with research segments known to gate.
Deleted status with content is not a retention waiver.

## 9. Canonical hashes and idempotence

Canonical C rejects duplicate JSON keys, non-JSON values, invalid UTF-8/unpaired
surrogates, NaN/infinity, booleans in numeric fields. NFC normalize all strings/
keys; reject resulting key collisions. Sort object keys by Unicode code point;
UTF-8, ensure_ascii false, comma/colon separators, no spaces/trailing newline.
Integers decimal; finite fractional numbers use Python 3.10+ json.dumps shortest
round-tripping decimals; integral floats become integers, negative zero 0. Pin
and test serializer vectors. Existing differently spaced reader policy hashes
are unchanged. Normalize dates/timestamps to specified ISO forms.

Arrays retain order except declared sets: refs/flags sort and dedupe; records
sort by id; captures by fetched_at/capture_ref; audience_values by join. Search
queries, steps/results and report lines keep order. Stored quotes use section 4's
explicit normalization, not undocumented rewriting.

input_sha256 is SHA-256(C({bundle: the entire normalized non-derived input
bundle, process: harvest/search/budget/policy inputs, rules: pinned rules inputs})).
Regrade every claim on every gate run. Claim rows share this one input hash;
proofs, all evidence and reference records, brief, decisions, resolutions, gaps
and independence metadata participate even when they do not count. Reference
cycles are irrelevant to hashing. Reject only predecessor-link cycles among
scope_change resolutions. The data-flow lock compares this one hash.

Exclude derived verification/gate status/reasons/grades and gate-written epistemic
status. Reconstruct evidence/context outputs from research_support_evidence_ids
and research_context_evidence_ids on each run; exclude output partitions only
when they equal the gate projection of those originals. Counters are never
excluded. Preserve original authored epistemic state as research_epistemic_status.
Unexplained manual output-partition changes exit 2. Legitimate additions change
original inputs; gate --write-bundle can repair the prior projection under those
new proven inputs. A plain gate assesses inputs without requiring derived flags.

Hash proposed final normalized inputs before write; recompute on staged written
representation. Hashes must match. Unchanged regrade produces identical hashes,
statuses, partitions and gate bytes; gate has no volatile current-time field.
valid_until is the minimum reachable retention/terms-check deadline or null;
consumers compare live time even with identical hashes.

Gate JSON follows ux-research-gate.v1.schema.json: schema/contract/rules versions,
run_id/bundle_id, result/exit_code, dependency digests, valid_until, status_counts,
issues/warnings and claims. Claim rows contain claim_id/input_sha256/status/
best_grade, each evidence's fit/final grade and eligibility/reasons, counting/
context/counter/observation refs, independence units/families/organizations,
counter_search_required, confidence/share_basis and exact export_values with
contributing evidence kinds. Counts equal assessed rows; each claim appears once.
Pass has no issues and exact claim coverage. Failure may omit unassessable claims;
unknown identifiers/digests are null, never fabricated hashes. Consumers cannot
use failure rows. Issues specify code/location/reason/next_step.

Gate also has bundle_input_sha256 (all non-derived input), process_input_sha256
(harvest/search/budget/caps), brief_sha256, merge_receipt_sha256, rules_sha256.
Claim-ID set/run_id/bundle_id must match exactly. Every input change changes all claim input hashes and requires a new process check. Gate and draft mode is live/fixture, derived from the reader run test_hooks
flag; mode enters the process and every claim hash. Fixture runs are diagnostic
only: export refuses them with exit 2, and composition never accepts their data
as real research. gate_input_sha256 in report/minimize outputs means SHA-256(C(the complete pass
gate)), distinct from its bundle/process input hashes. Hashes
are consistency checks, not signatures against a malicious writer controlling
every local artifact. Recompute; never trust a supplied hash alone.

## 10. Transactions and concurrent writers

Use run engine.lock flock for writers/consumers. Acquire before input snapshot;
hold existing ledger state.lock only briefly inside it. Never wait for engine.lock
while holding state.lock. Default timeout five seconds, optional --lock-timeout
0–60 seconds. Contention exits 3. Reject symlinks/traversal/unsafe modes/oversized
inputs. Snapshot ledger/counters coherently; engine never edits reader policy.

Use one committed snapshot and one staged snapshot under .engine/. Stage
mode-0600 artifacts, fsync files and directory, validate shapes/links/hashes and
recheck retention before publish. Atomically replace engine-state.json last;
it names the snapshot and byte digests. Consumers read only this committed
snapshot, never convenience copies. Authored input annotations are separate from
committed engine output. A failure preserves the previous snapshot, invalidates
its pass for consumers and writes gate_failed.json. Discarded snapshots and
staging files are purged. No journal, mirror recovery or compare-and-swap.
Interruption before manifest replacement leaves the previous snapshot authoritative;
interruption after replacement leaves the new snapshot authoritative. A later
writer purges abandoned staging. There is no multi-generation rollback history.

Gate failure publishes gate_failed with result fail/issues code/location/reason/
next_step, removes current gate/pass pointer; hard errors exit 2 before process
exit 1. Pre-snapshot usage/I/O reports stderr and invalidates pass when run safely
identified. Lock conflict mutates nothing. Pass removes current gate_failed.
Privacy-purge failures commit purged unverified bundle and failure together.
Every consumer rechecks retention under the consumption lock.

## 11. Audience draft and exact value joins

### 11.1 Honest draft and news

Export ux-audience-draft.v1 with completion incomplete. It cannot enter persona
or scenario composition even if values look complete. Required root fields:
audience_id, product, bundle_id, gate hashes, sources, segments, value_provenance,
bounds, withheld, todos. Empty sources/segments is valid. Export only supported
high/medium and eligible values; record withheld claims/reasons and all gaps.

A segment needs supported segment_exists with the same segment_id binding/subject.
Withhold dependent task/condition/context values without that parent; do not invent
one. Draft segment has segment_id, existence_claim_ids and values, a map of
completed-audience relative field paths to actual supported values. Missing
age/devices/tasks/data/frequency/criticality/priority have no invented values.
Unknown share is `{value: null, basis: unknown, source_ids: []}` with unknown
provenance, never zero. Bounds are separate. Every missing required field gets
a todo with typed target, reason and permitted completion source.

Never insert age defaults, equal devices, guessed frequency/criticality, arbitrary
test amounts, quotes or number conversions to pass ergo-audience.v1. Safe test
data can later be explicitly owner-approved fixtures, not empirical evidence.
Map source types/evidence kinds/confidence from gate. bundle_ref is the nonempty
bundle source-ID string; bundle_id/claim IDs live in value_provenance. Community/
review URLs are null. Member/API personal locators and shared quotes are withheld.
News remains secondary context and is never automatically exported. Claims with
news context can export their independent eligible non-news support. Gate must
reassess the non-news counting subset for export eligibility; if it no longer
meets supported thresholds, withhold the value as secondary_required. Removing
news never removes a counter or staleness blocker. A lone C
news cannot establish a supported segment. Existing standalone completed audiences
may still accept news for existence; --gate refuses research value bindings to it.

### 11.2 Typed bindings

audience_value is `{join, value, denominator_evidence_ids, value_checks}`. join is
`{segment_id, entity_kind, entity_id, field}`; entity_kind segment/task/condition/
context/pain_point. Segment entity_id equals segment_id; other entity IDs are
task_id, condition vocabulary name, context_id or pain-point ID within segment.
Same task may occur in multiple segments; intrinsic goal/data/success agree,
frequency may vary by segment. No array-index joins or “some supported source”.

For shares and weights only, each numerical scalar/map component in value_checks requires `{pointer,
evidence_id, value_as_printed, conversion, numerator_as_printed,
denominator_as_printed}`. Pointer is empty for scalar or a JSON Pointer to the
component. Evidence is eligible observed quantitative/statistic support with
the same frame/period/product relation. Printed literals must occur verbatim
in that evidence and metric labels/scope must match (reviewer checks meaning).
conversion is identity, percent_to_fraction or count_ratio. Parse ASCII unsigned
decimal tokens, no locale guessing: identity uses a printed 0–1 decimal; percent
requires a printed decimal followed by % and divides by 100. count_ratio requires
both printed integer counts, positive denominator agreeing with the neutral
population size, and exact rational equality to the proposed JSON decimal.
Nonterminating or rounded count ratios require a directly printed proportion
instead. Unused numerator/denominator literals are null. Missing checks or a
numeric mismatch is exit 2; boolean values never count as numbers. No arithmetic
from voice/API counts. Maps need one check per component, no hidden normalization.
Non-numeric values use an empty value_checks array and remain reviewer-assessed.
Task concrete_data (amounts, counts, durations) may contain any safe finite scalar;
its exact value needs a completed product observation or an approved brief value,
not a proportion, sampling frame or denominator. Such values have empty
value_checks and are never treated as empirical shares or weights.

| Entity and fields | Claim kind and value |
| --- | --- |
| segment: name_ko, summary, role | segment_exists; nonempty string, role operator/customer/served |
| segment: share, age_bands, grips, familiarity, left_hand_share | segment_share; fraction/maps, neutral denominator |
| segment: devices | device_mix; catalog-ID fraction map, denominator |
| segment: orientation | context_of_use; portrait/landscape |
| task: goal_ko, jtbd, success_ko | task; nonempty string |
| task: frequency | task; daily/weekly/monthly/rare/once, measured with denominator |
| task: concrete_data | product_behavior/intended_behavior; safe nonempty scalar map from observed product/approved brief |
| task: criticality | intended_behavior; safety/health/money/legal/data/access/convenience |
| condition: presence, why, cause, stakes | condition_presence; true, string, permanent/temporary/situational, normal/high |
| condition: share | condition_share; fraction, denominator |
| context: mobility, lighting, one_handed, interruptions, time_pressure | context_of_use; audience enums/booleans |
| context: share | segment_share; fraction scoped to context/segment with denominator |
| pain_point: text | pain_point/workaround; nonempty string |

Root choices use entity_kind audience, segment_id null, entity_id audience_id,
field method/floors/exclusions; they cannot appear in research audience_values.
Segment priority uses its segment join. Missing-task todos may use entity_id *
with an ordinary task field; they create no exported task.

Priority/floors/exclusions/method and safe fixtures are owner/product choices.
They get owner_decision provenance with decision_ref/reason/exact value, not
fabricated claims. Export only manifest-approved priority; unknown decisions
stay todos. Criticality/concrete_data may be labelled owner/product choices on
completion. Shares/weights/presence/frequency never use owner_decision to bypass
empirical support. Priority becoming primary or P0/P1 use requires new gate and
counter-search. Inclusive floor coverage is a test choice, not condition evidence.

value_provenance is `{join, value, basis, bundle_id, claim_ids, evidence_ids,
source_ids, observation_ids, input_sha256s, decision_ref, reason}`. basis is
research_claim/owner_decision/unknown. Research requires claims/hashes, exact
canonical value equality, matching subject/scope/join, and exact eligible
contributing evidence/source/observation closure. Each source-based contributing
evidence gets its own evidence.kind from its family (voice firsthand; analytics/
survey/statistical statistic; interview/usability/tickets firsthand; intent
official; estimate statistic if it carries the number else inference; expert
inference). News has no export mapping. Claim confidence comes from gate status.

Multiple values on one join must agree; otherwise withhold/conflict, never average
or choose the largest. Map weights are finite fractions summing to 1 within 1e-9;
do not normalize arbitrary counts during export. Official bounds never become
share. Claim kinds outside this table cannot export by extracting facts from prose.

### 11.3 Draft check and completed check

audience-check --draft --gate --bundle --run checks draft schema, exact joins/
values, unknowns/todos and freshness; it may pass while incomplete. Without
--draft reject draft exit 1. Complete intentionally into ergo-audience.v1, with
all existing age/device/task/data/frequency/criticality/evidence checks. Add the
same value_provenance array to the completed document; every present material
field, including each nested numerical map, needs provenance. Derived confidence,
evidence.kind and share.basis agree with gate. These derived metadata fields
inherit the corresponding existence/share/evidence value provenance and are
checked separately from authored audience_values. Segment confidence is the
minimum high/medium confidence among its contributing existence_claim_ids.
Share basis is measured only if every contributing value proof measures this
product's users; otherwise a qualifying estimate says estimated. Source IDs/kinds
and quote_basis are checked against each contributing receipt. Unknown share
provenance records join field share with value null while the draft's values map
stores the full unknown-share object. Editorial translations can add
no facts and name the underlying claim; reviewer checks equivalence.

--gate/--bundle/--run are required together. Check every empirical field against
its appropriate supported claim/join, not source existence somewhere. New data
added during completion must enter research and be regraded. Match evidence
statement/quote to claim/receipt. Owner decisions are limited to the declared
choice fields; they cannot supply empirical weights/presence/frequency. Unknown
required age/devices/frequency cannot compose. Preserve no-gate validation for
standalone completed files. Research-origin audiences require gate before
composition/resume; standalone structural validation cannot promote them.

Output stdout ux-audience-check.v1 JSON with mode draft/completed, result,
exit_code, audience_id, bundle_id, checked_values, warnings and errors; each
error has join/location/code/reason/next_step. No files written by audience-check.

## 12. Report checker and reviewer mapping

Guarantee is narrow: recognized claim citations, annex placement of unsupported
IDs, phantom IDs and syntactic statement mapping with a fresh gate. Human reviewer
checks completeness of empirical assertions, faithful scope/numbers and honest
hypothesis/recommendation labels. Mechanical pass is not semantic approval.

Read UTF-8 Markdown, CRLF to LF, preserve line numbers. ATX levels 1–6 require
opening # followed by whitespace, up to three leading spaces. Setext ===/---
after nonblank prose are levels 1/2. Ignore headings/IDs in backtick/tilde fenced
blocks (three or more same characters, closing same type/at least opener length).
Unclosed fence exits 1. Strip heading decoration and link destinations; NFC/case
fold English. Annex matches whole English phrase/token Unresolved, Unverified,
Annex, Appendix, Next evidence needed, or Korean substring 미확정, 확인 필요,
부록. “Annexation” does not match; “No Annex” does (no negation inference).
Children inherit annex until same/higher-level outside heading; equal-level
sibling is outside unless it matches independently.

Scan all non-fenced text for CLM- followed by 8–64 alphanumerics and malformed
CLM-prefixed tokens. Recognize prefix case-insensitively to catch disguises;
exact stored spelling is uppercase CLM/lowercase hex. Malformed/wrong-case IDs
fail. Known legacy IDs are accepted only by literal membership in the research
claim set; new IDs have eight hex. Inline code, tables, link labels/destinations,
image alt, footnotes, HTML and comments all checked. Decode URL percent escapes
once; check raw and decoded destinations, dedupe same-span occurrence. Reference
link destinations checked at definition line. No fetching links/executing HTML.
Unsupported IDs are annex-only; unknown IDs fail even in annex. Fenced examples
do not count as citations or coverage; reviewer prevents hidden real assertions.

Mapping report-claims.json is `{schema_version: ux-report-claims.v1,
report_sha256, statements: [{id, line_start, line_end, text_sha256, kind,
claim_ids, reviewed_by, review_note}]}`. Hash full LF-normalized report bytes;
span hash is exact LF-joined inclusive one-based lines without trailing LF.
Spans must be nonblank, non-fenced, within report and nonoverlapping. kind
empirical/hypothesis/recommendation. Empirical needs known nonempty claims visibly
cited in span with compliant placement. Hypothesis/recommendation outside annex
may have no IDs if span starts Hypothesis:/Recommendation:/가설:/권고:
(English case-insensitive); cited IDs still obey annex rules. A measured statement
inside a recommendation needs separate empirical mapping. Table rows/paragraphs
are allowed; no unreliable Korean sentence splitting. reviewed_by/review_note
null means warn review_pending, not semantic certification.

report_check.json contains schema_version ux-report-check.v1, result, exit_code,
report_sha256, mapping_sha256, bundle_id, gate_input_sha256, citations,
violations, warnings, mapping_checks, supported_coverage. Citation has ID/line/
heading path/annex/status. Violations code/location/reason/next_step. Coverage
distinct cited supported IDs / total supported, null at zero; under half warns
without failing. Exit 1 placement/mapping/parser, 2 phantom/invalid ID or stale/
absent gate/integrity/I/O, 3 contention. Diagnostics contain no suspect prose.

Cannot discover uncited/unmapped assertions, overstated paraphrases, hidden facts
in screenshots/links/fences, or verify truth, causation, representativeness,
translation, legal compliance or human review authenticity. Mapping completeness
and semantic review remain required after exit 0. Labelled uncited hypotheses/
recommendations stay usable outside annex; unsupported cited IDs do not.

## 13. Deterministic loop sanitizer

minimize requires fresh gate/validated bundle; creates new bundle.min.json and
minimize.json, never overwrites research/upgrades claims. Use field allowlists,
not just deletion of five keys. Preserve schema_version/bundle_id/permissions,
ten arrays, IDs/links, observations/runs/scenarios/personas/findings/proposals/
Figma fields required by validator/loop. Synthetic test attributes must be safe.

Keep source channel/type/family, nonpersonal org, safe access/retention metadata;
source_ref becomes origin-only for pages or opaque team-import/tombstone URI.
Drop aliases/author/thread/item/API IDs, locating paths, capture bodies and flag
quotes. Source/evidence summaries must be separately authored/scrubbed, with no
protected/member/API quote. Missing safe evidence summary exits 1; do not invent
it from excerpt. Evidence keeps id/source_id/type/epistemic_status/summary and safe
numeric denominator/scope. Claims keep safe authored statement/kind/status/links/
subject/scope/scenario bindings. Other arrays retain required authored test/output
fields and graph links; unknown optional fields are dropped and recorded.

Recursively drop excerpt/raw/raw_html/raw_content/body/quote/text/page_text and
equivalents, including inside decisions/import metadata. Mechanical checks are field allowlists, reader identifier patterns and retained
quotations (including nested fields). Every authored statement/summary/result
needs a reviewer attestation {record_id, field, content_sha256, reviewed_by,
reviewed_at}, bound to its canonical content in research.summary_attestations.
The mechanical pass never proves authorship; the reviewer attests authorship
and suitability after checking original evidence. Strip
research grading envelope; add minimized_from `{bundle_id, bundle_input_sha256,
gate_input_sha256, rules_version, sanitizer_version, mode}`. Projection provenance is
not a research gate: it cannot regrade/export. Original support refs may remain
only if required for valid links, not raw proof. Manifest records record ID/path/
removal category/count, summary counts, URL reductions and unsupported hypotheses;
no removed values/locators/keys/quotes.

Run bundle validation and recursive raw/privacy checks; loop packet embedding
must pass uxloop/contracts.py after the observation-only validator fix. Statistical
bounds cannot be loop measured population claims: downgrade those verified
preference/prevalence/discomfort claims to unverified and record
population_bound_not_loop_measure. Actual measured claims need quantitative
evidence/support_basis measured_sample; do not relabel statistics to bypass loop.
No eleventh array, no permission change. C-sorted output is byte-identical on repeat.

## 14. Command surface and exits

Run from skills/remorsearch-ux-qa. Mandatory arguments shown; no implicit globs or
network. Optional common --lock-timeout 0–60. No force/skip-gate/allow-expired/
trust-status/live-now switch. Parser/help errors exit 2.

```sh
python3 scripts/ux_research.py merge --run RUN --manifest RUN/axes.json --acknowledgements RUN/axis-acknowledgements.json --search-ledger RUN/search-ledger.jsonl --imports RUN/sanitized-imports.json --returns RUN/returns/stats.json RUN/returns/reviews.json
python3 scripts/ux_research.py gate --run RUN --bundle RUN/bundle.json
python3 scripts/ux_research.py gate --run RUN --bundle RUN/bundle.json --write-bundle
python3 scripts/ux_research.py report-check --run RUN --bundle RUN/bundle.json --gate RUN/gate.json --report report.md --statements report-claims.json
python3 scripts/ux_research.py export-audience --run RUN --bundle RUN/bundle.json --gate RUN/gate.json --audience-id AU-product-202610
python3 scripts/ux_research.py minimize --run RUN --bundle RUN/bundle.json --gate RUN/gate.json
python3 scripts/ergo_qa.py audience-check RUN/audience.draft.json --draft --gate RUN/gate.json --bundle RUN/bundle.json --run RUN
python3 scripts/ergo_qa.py audience-check audience.json --gate RUN/gate.json --bundle RUN/bundle.json --run RUN
```

merge requires one-or-more returns, manifest/search ledger even empty; imports/
acknowledgements optional (empty when absent). Reads policy/ledger/pages/imports/
manifest/returns; writes bundle/query_log/expansion_log/merge_receipt plus
merge_result.json with result/issues/gaps/counts/input digests. Invalidates old
gate on change; never creates pass. On failure writes only sanitized result/
failure state, no partial content bundle except mandatory expiry purge.

gate reads policy snapshots/ledger/receipts/manifest/logs/bundle, including agent
counter/decision/resolution/scenario annotations. Writes gate or gate_failed;
--write-bundle also writes derived states/partitions to named bundle. External
bundle path must match run/receipt and participates in lock. Plain gate can
pass without editing bundle; consumers trust recomputed gate, not verified flags.

report-check reads committed bundle/gate/receipt and report/mapping, writes
RUN/report_check.json. Export reads committed bundle/gate/receipt, writes
RUN/audience.draft.json and audience.todo.md. Minimize reads same, writes
RUN/bundle.min.json and minimize.json. Audience-check reads audience, committed
bundle/gate/run and catalog; prints JSON only. --gate/--bundle/--run required
together; --draft requires them. No-gate standalone completed check keeps current
behavior. Fixed gate filenames cannot be replaced by arbitrary supplied passes.

Research commands print one summary JSON `{command, result, exit_code, files,
issues, warnings}`; usage/I/O stderr, no raw text. Consumers can run after close
using committed receipts/policy snapshots without salt/pages; unchanged quotes
may regrade, edited quotes need new run/capture. Terms freshness still applies.

| Command | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| merge | Valid, complete or acknowledged coverage | Harvest/count/budget/privacy/length violation | Schema/provenance/quote/collision/reference/policy/I/O | Lock conflict |
| gate, --write-bundle | Process pass, unsupported claims allowed | Counter/cap/privacy/verifier/release-date process failure | Integrity/reference/numeric support; read-only expiry | Lock conflict |
| report-check | Mechanical pass | Placement/mapping/fence violation | Phantom/invalid ID, stale/absent gate/integrity/I/O | Lock conflict |
| export-audience | Valid incomplete draft, possibly empty | Unsafe/invalid value binding | Stale/absent gate/expiry/integrity/I/O | Lock conflict |
| minimize | Safe valid projection | Missing summary/unsafe projection | Stale/absent gate/expiry/reference/I/O | Lock conflict |
| audience-check --gate | Valid draft/completed values | Audience required-field/value/provenance mismatch | Stale/absent gate/expiry/bundle integrity/usage/I/O | Lock conflict |

Standalone bundle validator retains 0 valid/1 contract error/2 usage-I/O.
Unsupported status alone is not a process failure. --write-bundle does not
promise every claim is verified.

## 15. Table-driven grading boundaries

Assert status, grades, units, partitions, issue codes and exits for each row.
Defaults: valid provenance/dates, normal stakes, non-primary, no numeric export.

| Boundary | Result |
| --- | --- |
| Empty non-product; all E; E+D | lead_only/null grade; unfit; lead_only |
| One measured A; same plus unresolved counter | supported_high; conflicting |
| One voice B; two B people same/different channels | single_voice; supported_medium/high |
| B plus independent C same/different channel | single_voice; supported_medium |
| One statistical B with producer/population denominator | supported_medium; bound only |
| One non-statistical institutional B | lead_only, never single_voice/medium |
| Same organization repeated; two orgs with statistical B | One unit; two eligible B corroborated high |
| Same quote across authors/channels | One copy unit, no two-family corroboration |
| Five anonymous replies one thread; two threads same family | single_voice; supported_medium |
| Missing author/thread or producing agency | D cap, no identity unit, lead_only |
| Two undated voice B-to-C | lead_only |
| Incentive complaint B; already C; D from other downgrades | C; C; D, never raised |
| Notice without review trace; confirmed incentivized praise | No whole-page cap; D/no qualifying counter |
| Own-brand alone; external independent B family | D/lead_only; restore B then usual thresholds |
| Uncleared source injection; excerpt clears only; correct source clearance | E; E; normal grade subject to caps |
| New capture after clearance | Old decision inapplicable, E |
| A plus counter; A old-current; both | conflicting; stale; conflicting |
| Missing release date, including product observation | stale, exit 1 |
| Current effective dates unknown; old B+current B | stale; only current B counts, single_voice |
| Product no/inferred/incomplete observation | needs_product_check |
| Product observed completed same scope, no evidence | supported_high; validator accepts verified |
| Same plus unresolved contrary evidence | conflicting |
| Pain voice B plus product observation | single_voice; separate product claim |
| National population figure exported as product share | Exit 2; bound retained separately |
| Voice numeric counting support with/without measured A | Exit 2; voice context permitted |
| Primary/high stakes/share/P0/P1 without counter | Exit 1 for each canonical trigger |
| Prose resolution; unknown counter scope | Still conflicting |
| New strict scope with proven disjoint contrary items | New grade computed; predecessor remains conflicting |
| Person three sources/five excerpts; fourth/sixth | At limit pass; exit 1 |
| Quote 300/301; resource excerpts five/six | Pass/exit 1; pass/exit 1 |
| Search 80%, exact budget, one over | Warning, pass, exit 1 |
| Deadline just future/equal now/bare-date next midnight | Live/expired/expired |

## 16. Acceptance matrix and failing fixtures

Implement fixtures and parameterized tests, not only tests mirroring helpers.
All existing tests must still pass.

| Area | Required passing and failing coverage |
| --- | --- |
| Schemas | Valid typed return/gate/draft/bundle; wrong family, missing version, decision outcome/target mismatch, extra status rejected |
| Imports | Sanitized reviewed console/analytics; raw/name/partial IP/fake fetch/wrong app/hash refused without leaking text |
| Authority | Matching successful quote; invented excerpt, relabelled known fetch, policy ID, 200-before-stop, changed flags/access/retention/hash rejected |
| Identity | Permuted input stable; tracking/redirect/mobile rules; semantic parameter preserved; simulated short/full hash collisions refuse |
| Harvest | Identical return deduped; acknowledged partial; different duplicate/excluded/unacknowledged part/changed manifest rejected |
| Queries | All original/expansion/counter calls charged; duplicate text calls counted; failed calls/robots/render/crash reservations reconciled |
| Grading | Every section 15 row; no supported-before-conflict/stale, vacuous empty unfit, anonymous invented author or institutional B fallback |
| Sizes | Neutral product frame and official bound; post counts/star averages/missing period/mixed voice/bound-to-product exports fail; printed 20% cannot export 0.8; maps check every component |
| Decisions | Content-bound flags; stale clearance, notice-wide incentive, conflicting decision timestamp choice rejected |
| Privacy graph | Genuine aggregate; keyless excerpt linked to keyed/locating source, profile alias/reverse link/minor rejected |
| Bundle | Observation-only completed product; broken observation/counter/context/original-support/audience links and inferred/incomplete product run rejected |
| Compatibility | Existing valid/minimal/legacy fixtures pass; removed envelope/receipt cannot bypass; no live fixture export |
| Whole input hash | Mutate counter/context/source/run/version/brief/org alias/component/decision: stale refused; unrelated changes invalidate the common hash |
| Regrade | Gate, write-bundle, gate repeat identical hashes/partitions/bytes; added claim/old pass on failure/self-invalidating writes rejected |
| Transactions | Competing writers serialize; kill at every rename; mixed pair/symlink/lost external edit/expired rollback never accepted |
| Expiry | Purge content/derived statements/links with gap; context/counter expiry not ignored; reread proof required; contrary expiry cannot erase conflict |
| Draft | Honest empty/missing-age-device-task todos; no invented defaults/missing parent/news-only export/guessed frequency |
| Audience | Exact joins/values; changed share/age/device/frequency or cross-segment condition fails despite supported source somewhere; no composition without gate |
| Report | ATX/Setext/Korean/children/fences/links/tables; phantom/case/encoded/unsupported-body/stale-map/unclosed-fence fail; semantic review still required |
| Minimize | Repeat bytes stable/required graph preserved; nested raw/personal locators/missing invented summary/loop bound-as-measured/permission change fails |

Validate Draft 2020-12 schemas and valid/invalid instances; enforce cross-file
references/conditionals in the implementing validator. Check runtime vocabulary
against data, bundle reference copies byte-identical, and run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
```

## 17. Implementation changes and owner questions

Add CLI operations, schema enforcement, pinned grading data, capture/import
receipts, harvest/search reconciliation, graph privacy/tombstones, counter/scope/
decision evaluation, whole-input hashes, snapshot transactions, draft exporter/value
check, Markdown checker and minimizer. Change validate_bundle for observation-only
claims, optional links, research recognition and strict tombstones. Change audience
validation/composition for --draft and required research gate/value joins. Preserve
reader access stops/policy. Add all acceptance fixtures above.

No essential behavior is left to the owner. Product priority, release dates,
permissions, frames and safe test values remain run inputs; missing data has
explicit gaps/status/todos. Future personal protected-attribute research,
automatic team scrubbing or news export needs a new contract/privacy revision.


## 18. Auxiliary file shapes and sanitizer allowlists

The following JSON interfaces are also fixed. No unknown top-level properties.
Common issue records are {code, location, reason, next_step}; timestamps are UTC;
counts are nonnegative integers; maps use the stated keys; set-like arrays sort.

axis-acknowledgements.json is {schema_version: ux-axis-acknowledgements.v1,
run_id, entries}. Each entry has kind, axis_id, assignment_id, reason,
acknowledged_by (agent/owner) and acknowledged_at. Discriminate by kind:
- missing/partial: non-null manifest axis_id and assignment_id; no request_gap.
- excluded: manifest excluded axis_id, assignment_id null; no request_gap.
- unattributed_request: both IDs null, request_gap required: {host,
  charged_documents, logged_documents, unmatched_count}. Positive unmatched_count
  equals charged minus logged and matches the current state snapshot.
No extra fields. Acknowledgement never completes an assignment, proves evidence
or reduces charged budget. Later complete harvest supersedes the gap, retaining
history. Changed request counts need a new acknowledgement. Logged requests over
charged slots are integrity errors.

query_log.json is {schema_version: ux-query-log.v1, run_id, receipts,
duplicate_queries, total_invocations, counts_by_phase, counts_by_assignment,
request_fetch_ids, document_requests, policy_requests, request_gaps, issues,
warnings}. duplicate_queries contains {q, lang, call_ids}; normalize NFC and
whitespace only for this diagnostic grouping, never merge invocations. Phase maps
have discovery/expansion/counter_search; assignment maps use manifest IDs.
Request gaps use the acknowledgement request_gap shape. Budget totals use the
larger charged ledger count, including acknowledged crash reservations.

expansion_log.json is {schema_version: ux-expansion-log.v1, run_id, rounds,
seen_leads, stop_reason, gaps}. Each round is {round, assignment_ids, new_leads,
rejected_leads, new_segment_keys, new_problem_keys}; rejected lead is {lead,
reason}; leads retain reader lead/why/angle. Only expansion assignments occur in
rounds. Stop reason uses section 4; no rounds/no leads is no_leads. Gaps retain
coverage/request issues, never page text.

merge_receipt.json is {schema_version: ux-merge-receipt.v1, contract_version,
run_id, bundle_id, input_sha256s, manifest_sha256, query_log_sha256,
expansion_log_sha256, rules_sha256, source_proofs, evidence_proofs, claim_proofs,
id_rewrites, counter_history}. Input digest map keys are safe run-relative artifact
names. Source proof is {source_id, full_id_sha256, captures};
capture is {capture_ref, content_sha256, metadata}. Metadata uses source grading
fields/access/flags from section 3, without locating URLs or raw item IDs.
Evidence proof is {evidence_id, source_id, capture_ref, full_id_sha256,
normalized_excerpt_sha256, item_binding_sha256}. Claim proof is
{claim_id, full_id_sha256, original_support_ids,
original_context_ids, original_counter_ids}. Rewrite is {assignment_id,
part_index, local_id, record_kind, id}. Counter history is {claim_id,
counter_evidence_ids, call_ids, outcome, resolution_id}; append proven changes
only. Receipt has no
bundle_input_sha256: that would form a cycle with the bundle's receipt hash.
Subsequent gate transactions may append counter history in their own immutable
receipt while preserving the original merge receipt and its digest.

engine-state.json is {schema_version: ux-research-engine-state.v1, operation,
generation_id, previous_generation_id, inputs, outputs}. Generation ID is SHA-256
of C({operation, inputs, outputs}), excluding this pointer; previous ID is null
initially. Inputs map safe artifact paths to byte SHA-256; output entries are
{file, generation_path, sha256}. No volatile time enters
gate bytes. Private transaction metadata is not research evidence.

minimize.json is {schema_version: ux-research-minimize.v1, result, exit_code,
bundle_id, bundle_input_sha256, gate_input_sha256, sanitizer_version, output_file,
dropped, summaries_kept, urls_reduced, retained_hypothesis_ids, warnings, issues}.
Dropped entry is {record_id, path, category}; category raw_content/personal_locator/
unknown_field/research_proof/population_bound_not_loop_measure. Never copy the
removed value into a path or reason. The sanitizer version is minimize-2026-10-01.1.

Explicit record allowlists follow. Required legacy fields remain required;
optional absent fields are not fabricated. Scalars/objects inside these fields
still undergo recursive privacy/raw checks. A removal that destroys required
input shape is a refusal, not a partial hand-off.

| Array | Kept field names |
| --- | --- |
| sources | id, channel, source_ref, access_basis, access_method, public_scope, retention_status, source_type, source_family, platform_family, org, retention_until, privacy_class, summary, research_tombstone |
| evidence | id, source_id, evidence_type, epistemic_status, summary, denominator, scope |
| claims | id, claim_kind, statement, epistemic_status, verification_status, evidence_ids, context_evidence_ids, counter_evidence_ids, observation_ids, persona_ids, subject, scope, stakes, about_current_version, scenario_priorities, support_basis |
| personas | id, basis, adapter_revision, schema_fingerprint, seed, shard_or_config, max_scanned_rows, max_bytes_read, timeout_ms, selected_record_ids, filled_strata, unfilled_strata, stop_reason, original_attributes, scenario_assumptions, audience_ref |
| scenarios | id, persona_id, task, task_id, segment_id, context_id, priority, motivation_claim_ids, audience_ref, scope |
| runs | id, scenario_id, status, surface_ref, epistemic_status, started_at, ended_at, version, observed_at, scope, artifact_refs, artifact_sha256s |
| observations | id, run_id, epistemic_status, result, scope, observed_at, version, artifact_refs, artifact_sha256s |
| findings | id, scenario_id, observation_ids, claim_ids, figma_id, verification_status, epistemic_status, severity, segments_affected, title, summary, actual, expected |
| proposals | id, finding_ids, figma_id, proposal_type, expected_behavior_change, summary, status |
| figma | id, file_key, branch_key, baseline_version, readback_version, node_ids, read_at, readback_artifact_ref, design_status, defect_class |

Source access blocks/captures/flags/provenance and original claim research inputs
are dropped; safe access metadata means the retained basis/method/scope fields.
Do not retain unnecessary original-support arrays in this projection. Expired
source tombstones keep exactly their section 5 allowlist, with no added summary.
root permits only schema_version, bundle_id, permissions, records, minimized_from.
All other root fields are recorded as dropped. Derived confidence/share basis/
evidence kind inherit value provenance as described in section 11; administrative
IDs/titles are checked against receipts rather than invented claim bindings.


Schema normalization and error classification: normalize reader quotes with the
section 4 scrub/NFC/whitespace algorithm before checking quote-length constraints.
A normalized 301-character quote is process exit 1, not a generic schema exit 2.
Otherwise-valid aggregate records with personal keys and false/missing import
review attestation are privacy process exit 1. Malformed types/enums/references
still exit 2 and outrank process failures. Any backstop identifier replacement
in a reader return is recorded and blocks pass until the sanitized return is
resubmitted; it is not silent permission to restore a placeholder.

Verifier target hashes use immutable snapshots: a source target hashes its
resource identity commitment plus the selected capture metadata/content hash,
not the mutable latest header or other capture histories. An evidence target
hashes its original fields plus that selected capture. Claim targets hash flat
non-derived claim inputs without decision objects. Hash the whole normalized input bundle and process/rules inputs; do not traverse
a per-claim dependency closure. Reject only predecessor cycles in scope changes.

Scope nulls are unspecified constraints on claims and unknown facts on evidence.
Unknown evidence never proves disjointness. In this revision only distinct stable
product-version identifiers or explicit nonoverlapping periods can mechanically
resolve a scope change. Segment/context ID inequality and population prose do
not prove nonoverlap or a subset; leave those cases conflicting or obtain a
content-bound polarity correction for a genuinely non-contradictory item. Do not
invent a membership-predicate language. Source version aliases/relative labels
(such as latest) must be resolved from captured publisher data; otherwise unknown.

A bounds entry emits exactly denominator.value_as_printed as a string, preserving
unit/period/population relation and claim/evidence provenance. It is not a numeric
product-value binding; no percentage coercion from a bound to share is allowed.
Observation_ids is a declaration of supporting product results: agents must not
link a contrary result as support. Register contrary completed-run results as
counter evidence from a sanitized native QA report (usability_test, product_surface
scope), retaining the run/artifact provenance. This never supplies a real-user
preference or population denominator. Gate checks structure; the reviewer checks
that the result actually supports the authored assertion.

Native team data and authorized own-app console exports may enter through import.
Pasted web posts, browser captures and third-party public API dumps cannot use
team_provided to bypass reader access or retention: retain actual reader/official
API provenance instead. A team import is not authority to lift a stopped host.

Minimized origin mode must equal the consuming loop packet mode; fixture
projections cannot be intake for a live loop. This additive origin check does not
weaken existing raw-content, execution or population checks.

## Release amendments

Depth levels in RELEASE-CONTRACT.md section 2 are budgets and search targets,
never minimum-query gate or merge requirements. Coverage is acknowledged per axis.
Shared reports cite community/review/social evidence by channel, date and source
ID. report-check rejects body URLs on those hosts in the pinned route table;
official and statistical URLs remain allowed. Research reports begin with
## Decision or ## 결론 after the title, with at most three findings and three next
steps, each priority citation carrying Counter: <outcome> - <summary> matching gate.
Read the populated reader-return.example.json and the short audience-pipeline
field guide rather than the machine schema. Schemas remain the validator input.

Exact product task-value proof is recorded in observation.product_values, an array
of {join, value}. A completed eligible observation must contain the exact join
and scalar-map value. A reviewed native product_brief excerpt can instead carry
approved_values with the same shape, checked against its sanitized brief text.
These references participate in the common input hash, never claim identity.

Gate annotations that introduce valid contrary links are recorded in a private
gate_receipt.json, including process-failed gates. On that failure the engine
retains the prior committed bundle content, preserves the authored input mirror,
and commits only the contrary-history receipt and the nonconsumable failure.
Hard-invalid annotations are never added to history. Passes and subsequent merges
retain that receipt. It participates in process inputs and the common input hash.

## Not in this release

- Unconditional mobile/desktop coalescing without a successful capture trail is
  unavailable. The engine uses proven final URLs and preserves other aliases as
  distinct resources; exact copied text still supplies one independence component.
  The packaged route table has no separate authoritative resource-ID equivalence
  attestation, so the engine does not infer one from mobile URL spelling.
- No exhaustive process-kill/stress matrix across every filesystem call is
  shipped. The acceptance tests inject interruption before/after staging, snapshot
  publication and atomic manifest replacement, and test competing lock holders.
  The committed manifest remains the authority after interruption.
- Discovery automation, raw-team-export repair, automatic news audience export,
  personal protected-attribute research, semantic report approval and authorship
  proof remain outside the scope fixed in sections 1, 3, 5, 11, 12 and 13. The
  engine instead requires actual receipts, producer review, gaps, withheld values
  and content-bound reviewer attestations.
- Journals, mirror recovery, compare-and-swap and collision migration are absent
  by the owner's amendments 9 and 10. The engine uses one lock, one committed
  snapshot, one staged snapshot, an atomic manifest and collision refusal.

The reader's low-level default budgets are preserved. Research agents must put
the chosen quick/standard/deep ceilings from RELEASE-CONTRACT.md section 2 into
the brief; the default research depth is standard. Query targets never fail the
engine. This routing guidance is a documentation delta for the routing package.
