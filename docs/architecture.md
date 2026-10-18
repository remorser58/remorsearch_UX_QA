# Architecture: a bounded composition, not an autonomous monolith

## Ownership and trust

Research continues to own source provenance, evidence classification, claims,
problem hypotheses and sampling limitations. QA owns real product scenarios,
reproduction, observations, findings, browser telemetry, visual/accessibility
checks and regression replay. Synthetic personas only generate plausible test
situations. The coordinator does not convert persona confidence or repeated
community comments into measured preferences or prevalence.

The optional coordinator owns goals, required evidence/scenario scope, P0–P3
ordering, explicit operator permissions, state transitions and final acceptance.
A reviewed fix proposal is data; the narrow local patcher owns its authorized
application. Research and QA remain read-only. Checkpoint/report writes are
orchestration-owned effects requested by the CLI invocation, not product,
account, design or community writes.

External page text, provider receipts, Figma labels, community summaries and
patch explanations are untrusted data. None is evaluated as a shell command or
an instruction granting authority. The supervisor controls the CLI, workspace,
evidence root and explicit grant arguments. Original bundle permissions remain
historical; operational grants are separate checkpoint records with actor,
reason, timestamp and decision IDs. Grants are scoped by the immutable goal's
code paths and persist on resume; they do not authorize deployment.

## Components

| Module | Responsibility |
| --- | --- |
| `contracts.py`, `schema.py` | Strict versioned input shape, cross-references, epistemic/permission boundaries, append-only merging. |
| `evidence.py` | Hashes, receipt identities, run intervals, pinned Figma, actual/reference captures, explicit visual/accessibility/regression gates. |
| `storage.py`, `io.py` | Atomic persistence, locking, strict JSON, safe paths, code snapshots and integrity ledger. |
| `engine.py` | Bounded states, intake, priorities, fix/replay orchestration, stop decision. |
| `patching.py` | Exact, allowlisted unified text patches, predicted revisions and interrupted-write reconciliation. |
| `cli.py`, `scripts/ux_loop.py` | One foreground entry, explicit grants, exit codes and JSON report. |

The JSON Schema reader supports only the keywords used by
`schemas/ux-loop.v1.schema.json`. Unknown schema keywords fail closed. It is not a
replacement for a general JSON Schema implementation. Keeping it small avoids a
runtime dependency while the original v1 validator continues its semantic checks.

## Goal/state contract

`goal` has a stable ID, objective, complete scenario matrix, required evidence IDs,
explicit code paths, bounded `max_iterations` and mandatory stop conditions.
`policy` records whether design is Figma-first and whether side accents are allowed, prohibits raw community storage, and
sets a live-artifact freshness window of 1–30 days. Default example: seven days.
The normalized v1 bundle remains embedded without changing its record IDs.

Phases advance only in this order:

```text
research -> plan -> browser -> fix -> replay -> decision
                         checkpoint at every boundary
```

| Status | Meaning and continuation |
| --- | --- |
| `running` | A foreground phase is underway; not a successful result. |
| `interrupted` | Explicit pause, Ctrl-C or per-invocation step limit; resume that phase. |
| `blocked` | Permission/integration/artifact/matrix missing, unsafe path, conflicting workspace or unresolved design. Supply missing authorized input and resume. |
| `unknown` | Required evidence is inferred/unknown, inconsistent, stale or untrustworthy. Never accept. An explicit new bounded round is needed to retry. |
| `failed` | Actual declared comparison, accessibility, scenario or regression check failed. Preserve receipt and explicitly retry a new round. |
| `iteration_limit` | Budget exhausted; terminal without completion. A new scope/goal needs operator review. |
| `complete` | The decision gate rechecks every required stop condition; no direct skip from another phase. |

The `no_unknowns` stop condition applies to **required** goal evidence and final
scoped scenario/comparison/regression checks, not to unrelated hypotheses or old
failed records retained for audit. Those records keep their original epistemic
status. Failed historical rounds may coexist with a successful final round; a
failed/unknown/blocked final replay cannot complete. Every scoped finding must be
covered by an applied fix and same-scenario final replay; there is no waiver API.
A no-change round is allowed, but still needs the complete final scenario and
regression matrix and cannot waive unresolved findings.

The default invocation performs at most 12 phase steps (configurable 1–20).
Retries consume the immutable goal budget, at most 10 rounds. No background
worker, session hook, periodic polling, hidden continuation or unlimited loop is
installed. Missing browser runs stop at `browser`; missing post-fix receipts stop
at `replay`. Empty/no-op evidence does not count as a successful run.

## Persistence and recovery

A checkpoint stores the entire validated packet, scoped workspace/evidence paths,
run ID, permissions and their history, applied/accepted fix IDs, pending patch
intent, priorities, phase/status and a hash-chained event ledger. Atomic JSON
replacement with file and directory fsync keeps each checkpoint self-contained;
a checksum detects accidental corruption. The command locks both checkpoint and
workspace using POSIX `flock` so two cooperating goals cannot write together.

New input must preserve old array prefixes exactly. Reusing a record ID with a
new status, changing old timestamps or granting permission inside provider input
is rejected. Additional evidence invalidates a previous cached completion before
revalidation. Reopening a completed checkpoint rechecks live files/receipts:
changes or revoked/withdrawn support cannot silently retain acceptance.

Before modifying product files the engine persists the complete predicted patch
intent. It then accepts each file only at its original or already-predicted
content hash. A process crash between atomic file writes and the applied receipt
can be resumed idempotently. A concurrent unexpected edit blocks rather than
being overwritten. The multi-file operation is recoverable, **not a filesystem
transaction**; partial authorized edits may remain until the operator reconciles
or restores them. No automatic rollback rewrites independent human changes.

The checkpoint's checksum and event hashes are integrity aids, **not signatures**
or defenses against someone who controls the checkpoint file and can recompute
hashes. Store checkpoints and evidence in a trusted, private local directory.
Locks protect cooperating processes, not a malicious actor changing symlinks or
files concurrently at OS level. Paths are limited to portable ASCII relative
names; symlinks, parent traversal, reserved runtime/build directories and writes
outside declared code paths are rejected. Binary patches, mode changes and
renames are unsupported. Large inputs/artifacts/text files are bounded.

## Acceptance and evidence boundaries

A fix is `applied` after an explicitly authorized patch completes, never accepted
at that moment. The final replay must use new run IDs, the identical scenario
contract/digest, pinned device/viewport/route/fixture, a fresh isolated session,
the final scoped source revision, matching Figma versions/nodes, passed visual
checks, keyboard/focus/semantics plus declared accessibility coverage, and passed
regression coverage of the **whole declared matrix**. Live replay timestamps must
follow the actual local fix receipt. Console, network and runtime reports must
explicitly enumerate unexpected errors. Any such error fails a final replay.

A screenshot alone is not comparison proof. Both captures, versioned editable
Figma readback, a comparison receipt, method/reviewer and per-aspect judgments are
required. PNG structure/dimensions and SHA-256 integrity are checked, not visual
similarity computed by this CLI. Review/pixel-diff claims must be generated by an
external reviewer/comparator and remain tied to the run. The imported evidence
is checked for consistency, not authenticated independently. No device matrix
or accessibility subset establishes whole-site quality or WCAG certification.

`mode: fixture` permits clearly marked synthetic SVG captures, never claims a
live browser or actual editable Figma file, and always reports
`product_complete: false`. `mode: live` requires live execution metadata,
provenance and PNG captures. A live completed report means scoped acceptance
**from imported provider evidence**, not that this CLI launched a browser or
proved the provider honest. There is no aggregate UX score.

## Retention and live integration limits

Only minimized source metadata and authored summaries enter the composition;
raw community bodies/excerpts are rejected. Providers must redact credentials,
identifiers, request payloads and customer data from logs/captures. The live
freshness window expires evidence for acceptance, not an automated deletion job.
The operator owns artifact purge/withdrawal processing; once removed or expired,
a goal requiring it cannot be revalidated as complete. No raw community
collection or indefinite archive is implemented.

Aside intake, Figma reads/writes, browser execution, account/fixture provisioning,
cleanup, app rebuilds, visual comparison engines, accessibility scanners and
signed attestations are adapter boundaries, not shipped integrations. Providers
may run real scenarios externally after appropriate approvals and append their
receipts. The coordinator never claims an unavailable integration succeeded.
Design/spec conflicts require an approved editable Figma baseline before a new
implementation goal. Two original skill directories work without this layer.
