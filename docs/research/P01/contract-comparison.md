# P01 contract comparison (criterion P01-AC01)

Status: proposed P01 synthesis for independent review. It names a **preferred backend
candidate and a fallback for the P02a spike**. It does **not** select the production
backend: P02a selects one backend, or reports no-go, after its conformance fixtures and
the three rejection criteria (plan section 11).

Evidence base (cited, not re-researched):

- **WI** = `weave-inventory.md` (Weave pinned at `e7c3f3c`; paths there are `W:path:lines`).
- **US** = `upstream-surfaces.md` (gh-aw `28f2101`, Symphony `be10a1b`, Beads `e226083`).
- **RI** = `runtime-and-identities.md`; `S-…` source IDs resolve in `permission-evidence.json`.
- Interfaces named below are defined in `docs/decisions/0002-internal-interfaces.md` and
  indexed in `contracts/interfaces.v1.json`. Pins are consolidated in
  `contracts/upstream-pins.v1.json`.

Evidence labels: **observed** (read in pinned code/data), **documented** (stated by
upstream or GitHub docs, not exercised), **inference** (reasoning; must be confirmed).
No upstream code, test or binary was executed for P01. Weave SLOC figures are static
counts from WI section B/E.

## 1. Required contracts 1-10 (plan section 3)

| # | Contract | Weave code reused as-is (file:lines, SLOC) | Adapter work required (interface) | Demonstrated gap (citation) | Closes gap | Label |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | At most one accepted development owner and one review owner per task/job | None for ownership: the `flock` coordinator lock (`state.py:194-214`) is single-host authority and is replaced, not reused (WI §E). Reusable as-is beside it: path-overlap check `scheduler.py:213-270` (42 SLOC) | `state-backend.compute_transition` / `apply_transition` with a CAS condition carrying development and review claims with generation; `publisher.conditional_ref_update` as transport | Weave is single-host only by its own statement (`W:docs/development/github-adapter.md:41-49`); no review-owner concept, review is a synchronous child process (`cli.py:715-723`) (WI §C2, §F row 1). gh-aw Claims are single-winner via `--force-with-lease` but owners must be Actions worker runs (US §1.5, §4 row 1). Live CAS contention is unverified upstream (US §1.2, spec :3301) | P02a (A01, A04 for the transport), P05 (claims), P08 (review-job claims, A11) | observed; CAS under race unverified |
| 2 | Claimable only with accepted prerequisite completion evidence and available resources | `scheduler.py:213-270` path overlap (42 SLOC). The rest of `scheduler.py` (345 SLOC) is reuse-with-adapter | `plan-compiler.readiness` fed with accepted completions and reservations from `state-backend.read_state`; Beads-style explanation shape (US §3) | Weave treats "closed-as-completed **and** board Done" as completion (`scheduler.py:401-412`) and board cards as capacity input (`:193-197`); Projects automation can move cards (WI §C7, §F row 2). Resources are path globs only; no hard resources (WI §D2 item 8) | P03 (readiness and explanations), P05 (reservations, hard resources) | observed |
| 3 | A stale worker's output is not accepted under an old claim generation | None. Review acceptance binding `review.py:148-177` is reuse-with-adapter (144 SLOC file) | Claim generation in every command envelope (`state-backend`), `publisher.publish_candidate` rejects `StaleGeneration`, `execution.authority_lost` | No generation, fencing token or epoch exists (searched `generation`, `fenc`, `epoch`; WI §C2). gh-aw has no lease, renewal or takeover ("There is no background timer or Claim lease", US §1.5 item 3) | P02a (A04, A17 fencing), P05 | observed |
| 4 | Review applies to an exact candidate and exact task revision | None as-is. Reuse-with-adapter: head/base/requirements binding `review.py:157-168`; tree equality `integration.py:72-81`; digests `model.py:137-160`. The bootstrap `core.review_packet` already binds candidate, base, task digest and per-criterion digests | `plan-compiler.compile_task_revision`, `plan-compiler.build_review_packet` | Weave's "task revision" is a digest of selected issue-body sections, not an approved immutable revision (`model.py:151-160`; WI §F row 4). gh-aw has no review concept (US §4 row 4) | P03 (revision objects, packets), P08 | observed |
| 5 | Review budget belongs to the task across workers, restarts, branches and amendments | None. Weave **contradicts** the contract: rounds are per attempt, a released attempt resets them, and a test asserts the reset (`transitions.py:177-180`; `test_transitions.py:152-155`) | `review_rounds` records in `state-backend` (reserve slot on dispatch, finalize once); `evidence-records.validate_verdict` | WI §C3, §F row 5; issue #6 released an attempt to widen scope (WI §G). gh-aw only has `retry.max_attempts` per Work (US §4 row 5) | P08 (aggregate rounds), P05 (persistence), P12 (import recount) | observed |
| 6 | Timeout, unavailable checker or unverified test cannot become PASS | None as-is. Reuse-with-adapter: Codex timeout/exit/silence → `ReviewRejected` → BLOCKED, never a verdict (`review.py:107-128`; `cli.py:729-734`). Bootstrap `core.check_review` already refuses PASS without independent evidence | `evidence-records.record_check_evidence`, `validate_verdict` (adds `UNVERIFIED`), `reviewer-launch.collect_result` (infrastructure outcome is not a verdict) | A reviewer that cannot run checks may still PASS (`W:docs/development/review.md:66-68`; issue #6 round 3, I6:6503850141); no `UNVERIFIED` verdict; verification is coordinator-run, not trusted CI (WI §C4) | P08 (UNVERIFIED, per-check provenance), P09 (trusted CI) | observed |
| 7 | Done = integrated deliverable plus accepted completion evidence | None as-is. Reuse-with-adapter: derived integration evidence `integration.py:44-82` (60 SLOC); Done gate `transitions.py:150-206` | Completion record in `state-backend`; `trusted-evidence.verify_trusted_ci`; non-code deliverable location in the task revision (`plan-compiler`) | Strong for code tasks on one host, but no shared-state completion record and no non-code deliverable location (WI §F row 7) | P09 (gate), P05 (record), P03 (deliverable field) | observed |
| 8 | Human commands authenticated, correlated, auditable; discussion never changes policy | Generic causal ordering `events.py:153-174` (18 SLOC) reusable as-is. `/weave-decision` recognition `events.py:139-150` is removable under the narrow adapter (WI §E) | `command-ingestion.poll_commands`, `parse_and_authenticate`, `submit`, `post_terminal_command`; `command_receipts` in `state-backend` | No command ID, deduplication, question correlation or designated human; the coordinator and maintainer share one account (`policy.json:17-24`); decisions were relayed as orchestrator ANSWER text (WI §C6, §F row 8, §G) | P07 (ingestion), P05 (receipts, dedup) | observed |
| 9 | Board and summaries are recoverable projections, not locks | None as-is. Reuse-with-adapter: transition executor `transitions.py:208-323` (106 SLOC) becomes a projection reconciler; discrepancy classification `reconcile.py` (121 SLOC) | `board-projection.compute_projection`, `read_projection`, `reconcile_projection` | The board is an eligibility, capacity and completion **input** in Weave (`scheduler.py:193-197, 386-393, 410`; WI §F row 9). Symphony also uses tracker state as eligibility and restart source, which conflicts with this contract (US §2, §4 row 9) | P07 (projection, repair), P03 (readiness from state only) | observed |
| 10 | No model process receives merge authority or unrestricted controller credentials | None as-is. Credential scrubbing in `hooks.py:19-21, 93-98` and `review.py:22-23, 104-106` is classified "unknown" pending P02b (WI §E) | `execution.start` launches sandboxes with no GitHub credential; `contracts/permission-matrix.v1.json` (sandbox roles hold none); `RS-main` ruleset | Weave's orchestrator is a model session holding the maintainer's `repo`+`project` token; merge is "ask", not deny; candidate-tree code runs in the coordinator environment (WI §F row 10). GitHub: Contents write includes `PUT …/pulls/{pull_number}/merge`, so "no merge authority" is enforced only by the `main` ruleset (RI §G.1 item 5; `S-gh-fgpat`). That block holds only while `main` requires at least one approval: with zero required approvals (DP-10 option `zero_approvals_pr_required`) any Contents-write holder (`supervisor-runtime`, `actions-publisher-fallback`, the setup credential) can merge once trusted-CI checks are green, and contract 10 would rest on trusted code alone. The matrix therefore recommends one required approval plus a human-only admin bypass in `pull_request` mode (DP-10, DP-05); `merge_main` stays with `human-integrator`. Docker Sandboxes' `github` secret service would inject the host token into model requests (RI §B.4; `S-docker-sbx-credentials`) | P02b (credential separation, A19), P06, P10 (credential specification), P09 | observed + documented |

## 2. Additional P01 scope items

| Scope item | Reused code / component | Adapter work required (interface) | Demonstrated gap (citation) | Closes gap | Label |
| --- | --- | --- | --- | --- | --- |
| Licences | Weave MIT (controller paths annotated MIT in `W:REUSE.toml:15-92`); gh-aw MIT; Symphony Apache-2.0 with `NOTICE`; Beads MIT (`license-report.md`) | None | Remora's own licence is undecided (`NOTICE.md`). Copying Weave Python requires carrying the MIT notice and a NOTICE/attribution change outside P01's paths (`scope-requests.md`). AI co-authorship trailers on Weave controller commits are flagged, not assessed (WI §A) | Human decision (README Q13, Q14); the task that first copies code (P03/P05) via scope request | observed |
| gh-aw queue and safe-output surfaces | Candidate only. Queue: Git-backed `work-queue.jsonl` with linear fast-forward and `--force-with-lease` CAS (`pkg/workqueue/branch_git.go:525-563`), DAG gating on verified Results, checkpoint/compaction (US §1.2). Safe outputs: 44 typed handlers, trusted jobs apply agent intents (US §1.3) | If adopted: AW worker workflows, Actions-run binding, `gh aw compile` lock-file upkeep, engine secrets, plus an external-supervisor adapter. If not: adopt the *pattern* with a local typed-action schema and call it an adaptation (plan section 4) through `state-backend.compute_transition` | Specs are "Working Draft" / "implementation in progress"; version-3 schemas grow additively without a version bump; the activation job fetches a moving `compat.json` from `gh-aw-actions@main` and can disable pinned workflows (`check_version_updates.cjs:29`); upstream marks live Git contention, hosted publication and hosted execution unverified (US §1.1-1.2, §9.1 rows); safe-output create operations are non-idempotent (US §1.3) | P02a (criteria 2 and 3, time-boxed) | observed (code) / documented (spec) |
| External-worker binding | None | Would need a supported authenticated path for a non-Actions process to hold and exercise a Claim | Worker authority is bound to the original Actions run: `authenticatePublisher` reads `GITHUB_RUN_ID`/`GITHUB_RUN_ATTEMPT`, refuses `attempt !== 1` (`actions/setup/js/work_queue_native.cjs:240-251`); the operator CLI rejects worker roles ("native operator publisher cannot impersonate workflow roles", `pkg/workqueue/branch.go:357-391`); `claim`, `finish` and `force-release` subcommands are asserted absent (`pkg/cli/work_command_test.go:52-58`); no lease or renewal; authentication is "outside the work-queue protocol" (spec :1105-1107). No supported external-worker path was found (US §1.5) | P02a criterion 1 (live refusal test); human/P02a for the self-hosted-runner question (README Q1) | observed in code; not executed |
| Symphony runner boundary | Vocabulary only: `WORKFLOW.md` front-matter layout, active/terminal states, `dispatchable`, `blocked_by` (US §2) | An optional runner adapter would need six changes: authority-driven `dispatchable`, neutered `claimed` set, stop/fence mapping, non-Codex runner, hardened sandbox defaults, Elixir/OTP runtime (US §2) | In-memory `claimed` set in one orchestrator; no cross-host exclusivity; tracker state is the eligibility input; the GitHub adapter sets `blocked_by: []`; Draft v1 spec, prototype implementation (US §2) | Not adopted for the pilot; any later runner adapter needs its own task after P06 | documented / observed |
| Beads (readiness UX) | Explanation shape `ReadyExplanation`/`ReadyItem`/`BlockedItem` (`internal/types/types.go:1935-1985`) as vocabulary | Extra reason kinds (missing completion evidence, resources, Needs human, review budget) in `plan-compiler.readiness` | Claims are replica-local; Dolt is a separate authority; not to be adopted as a second database (US §3; plan section 2) | P03 (explanation output) | observed / documented |
| Runtime support | Docker Sandboxes (microVM, credential proxy, deny-by-default egress) or ordinary rootless OCI (RI §E) | `execution` interface and a pinned runtime profile with explicit settings (`ssh.agentForwardingEnabled=false`, skills off, browser off, clone mode, trimmed network policy; RI §E.1) | Docker Sandboxes Linux support is Ubuntu 24.04+ only; the bootstrap host is Debian 11; docs disagree on skills mounting and credential defaults; rootless cgroup flags are silently ignored without cgroup v2 + systemd; OCI egress enforcement is undocumented (RI §E, `S-docker-sbx-install`, `S-docker-rootless-tips`) | P02b; human host decision (README Q11) | documented; host checks inconclusive |
| Required GitHub identities | `contracts/permission-matrix.v1.json` (this task) | `harness init` emits the credential specification from the matrix (P10): per role the credential types, permission names and levels, repository selection and Project scope (`scope`), forbidden permissions, holder, expiry/revocation and ruleset enforcement; `doctor` checks access | User-owned Projects: only classic/OAuth `project` (`S-gh-pat-manage`, `S-gh-oauth-scopes`); Checks API not callable by fine-grained PATs and check-run creation needs an App (`S-gh-rest-checks`); only Apps are documented UI bypass actors (`S-gh-rules-create`); `GITHUB_TOKEN` cannot access Projects and is not a documented bypass actor (RI §G.1). Pull request authors cannot approve their own pull requests (`S-gh-pr-approve-required`), so a required approval count of one blocks a single maintainer unless DP-10 is decided | Human decisions DP-01…DP-10 (README); P02a/P02b live checks; P10 | documented |

## 3. Preferred backend candidate and fallback (input to P02a, not a selection)

**Preferred candidate for the P02a spike: the narrow Git-state adapter**, run by the
supervisor-hosted reducer, committing each transition as one conditional update of
`harness/state` (per-task files, compact index, receipts, pending effects, verified
snapshots; plan section 4).

**Fallback candidate: the gh-aw work queue**, assessed in full within its three-day box
from day one, alongside the narrow adapter. It becomes selectable only if it passes all
three rejection criteria and A01/A04/A05/A07 plus A17 fencing. If the narrow adapter
fails its fixtures and gh-aw fails any criterion, P02a reports **no-go** and publishes the
gap (plan section 11); no criterion is weakened.

**Selection order.** The plan evaluates gh-aw first and treats it as the first candidate for
reuse (plan section 1, "First evaluate gh-aw's queue and safe-output implementation";
section 2, "First candidate for reuse, subject to the M0 tests"; AGENTS.md, "Prefer existing
components when a pinned integration passes the contract"). P01 reverses that order only as
an expectation. "Preferred" means the outcome expected from the code-level evidence and the
default placement; it is **not** a tie-break. If gh-aw passes all three rejection criteria
and A01/A04/A05/A07 plus A17 fencing, the plan's reuse rule governs and gh-aw is selected.
Only otherwise is the narrow adapter selected (if it passes the same scenarios), and
otherwise P02a reports no-go.

Why P01 expects this outcome, tied to the rejection criteria:

1. **External process holds a Claim (criterion 1).** This is the central finding. Code
   evidence shows no supported path for a process outside Actions to hold or exercise a
   Claim: worker authority is the original Actions run (`work_queue_native.cjs:240-251`),
   the only non-Actions publisher cannot take the worker role (`branch.go:362-363`), and
   there is no claim/finish/lease command (US §1.5). An external supervisor could
   participate only by running the work inside an AW worker workflow, or by writing Claims
   under a non-worker role or a separate record; the latter is what criterion 1 forbids.
   The default placement is a supervisor outside Actions, so the lead is toward failure.
   It is a lead, not a result: the refusal was read in code, not executed, and the
   self-hosted-runner interpretation is open (README Q1).
2. **Pinnability (criterion 2).** Evidence points both ways (US §1.7): tags and SHA-pinned
   lock files exist and the queue schemas are unchanged since `v1.0.0`, but a moving
   remote `compat.json` can disable pinned workflows, version-3 schemas grow without a
   version bump, the specs are working drafts, and queue dispatch depends on REST API
   version `2026-03-10`. Unsettled; P02a must test whether the compat check can be pinned
   or neutralized.
3. **Net reduction of maintained Weave code (criterion 3).** The removable Weave
   coordination/publication code is at most **707 SLOC** (`state.py` 168, `publisher.py`
   106, transition executor 106, `github.py` writes 28, `events.py` authenticate 34, plus
   an upper bound of 265 SLOC of `cli.py` wiring that also builds packets), or **828 SLOC**
   with `reconcile.py` (121) (WI §E). Both backends replace roughly the same Weave code; gh-aw
   adoption additionally requires worker workflows, Actions-run binding, compile/lock-file
   upkeep and engine secrets, and still an external-supervisor adapter (US §1.7 row 3). No
   net figure exists for either option; P02a measures it.

The narrow adapter has its own unproven assumptions, which P02a must test rather than
assume: REST `PATCH git/refs` has no expected-old value and its 409/422 meaning is
undocumented; `updateRefs` (`beforeOid`) and `createCommitOnBranch` (`expectedHeadOid`)
document expected-old semantics but not race behaviour or required fine-grained/App
permissions; `git push --force-with-lease=<ref>:<expect>` needs a clean controlled Git
environment (RI §C). The ruleset layout that lets one App fast-forward but never rewind or
delete the state branch is an inference to test (RI §D).

## 4. Placement

- **Default: supervisor-hosted reducer.** Each enrolled trusted supervisor runs the same
  pinned reducer and publishes with the selected conditional update. The shared branch is
  the authority; supervisors are concurrent clients (plan section 4).
- **Fallback: Actions-hosted reducer**, separately justified for deployments that cannot
  trust state-writing supervisors. Same protocol and the same state branch; the writer
  identity changes to `actions-publisher-fallback` and supervisors become read-only
  clients. Switching placement is an explicit pause/fence/drain operation with an authority
  epoch change; the two placements never write concurrently. The fallback does not waive
  the external-worker or single-authority criteria (plan section 11). Its open issues are
  in the matrix: `GITHUB_TOKEN` as bypass actor not found, an App key as an Actions secret
  (DP-06), how a supervisor without Contents write submits transitions and hands over
  candidate material (unverified).
- gh-aw can be selected only if criterion 1 passes. If it is, its scheduler and trusted
  jobs in Actions are the single authority, supervisors participate only through the
  authenticated path that passed criterion 1, and the placements above (which describe the
  narrow adapter's reducer) do not apply. The external-worker evidence makes that outcome
  unlikely for supervisor-launched sandboxes, which is why the narrow adapter is the
  expected outcome.

## 5. Authority map (one authority per state kind)

Machine-readable form: `placements.*.authority_map` and `state_kinds` in
`contracts/permission-matrix.v1.json`, checked by
`tests/contracts/test_permission_matrix.py` (one writer per authoritative kind; projections
have no writer authority).

| State kind | Authoritative record | Writer, supervisor-hosted (default) | Writer, Actions-hosted (fallback) | Non-authoritative copies |
| --- | --- | --- | --- | --- |
| Task state (lifecycle, readiness, current revision pointer) | `harness/state` (narrow adapter: `state/tasks/<id>.json`) | reducer in `supervisor-runtime` via CAS | reducer in `actions-publisher-fallback` via CAS | Project Status, issue summary, labels |
| Approved task revisions | `harness/state` revision objects bound by digest | `supervisor-runtime` (on an authorized approval command) | `actions-publisher-fallback` | Plan file on `main` is an input; GitHub issue edits only propose |
| Claims/leases (development and review, generation, expiry) | `harness/state`, inside the task/job record | `supervisor-runtime` | `actions-publisher-fallback` | Issue summary "delegate" line |
| Resource reservations | `harness/state`, updated in the same commit | `supervisor-runtime` | `actions-publisher-fallback` | — |
| Review rounds and budget, findings | `harness/state`, task record | `supervisor-runtime` | `actions-publisher-fallback` | Project `Review` field |
| Questions | `harness/state` question records | `supervisor-runtime` | `actions-publisher-fallback` | Issue comment mentioning the human; `Needs human` field |
| Human command input | Issue comment by the accountable human (`human-integrator`) | the human | the human | Accepted only via command receipts |
| Command receipts (dedup) | `harness/state` | `supervisor-runtime` (several ingesters, one receipt per `command_id`) | `actions-publisher-fallback` | — |
| Pending external effects (outbox) | `harness/state` intents with idempotency keys | `supervisor-runtime` | `actions-publisher-fallback` | The effects themselves (comments, refs) are read back, never authoritative |
| Sessions, stop requests/confirmations | `harness/state` | `supervisor-runtime` | `actions-publisher-fallback` (supervisors report stop-confirmed as requests) | Issue summary |
| Enrollment | `harness/state` | `supervisor-runtime` (authorized command) | `actions-publisher-fallback` | — |
| Candidate branches | `refs/heads/agent/<task>/<generation>/…`; which candidate is under review is recorded in task state | `supervisor-runtime` (publisher) | `actions-publisher-fallback` | Pull request view |
| Trusted CI evidence | Check runs from the pinned trusted-CI App | `trusted-ci` | `trusted-ci` | Status rollups |
| Accepted evidence (verdicts, per-check provenance, manual acceptances, completion) | `harness/state`; artifacts by digest elsewhere | `supervisor-runtime` | `actions-publisher-fallback` | Issue comments |
| Integration | `main` via a reviewed pull request | `human-integrator` | `human-integrator` | — |
| Board projection, issue summaries | none (derived) | no authority; refreshed by `supervisor-runtime` or the optional `projection-only` job | no authority; `actions-publisher-fallback` or `projection-only` | — |

Rules that keep this single-authority:

- Only one placement is active per deployment; the switch is an explicit epoch change.
- The writer-ruleset bypass list (`RS-state-writers`, `RS-candidates-writers`) names only
  the active placement's writer; deletion and force-push rules sit in separate no-bypass
  rulesets (`RS-*-immutable`), subject to the live test in P02a.
- A failed gh-aw criterion selects the narrow adapter; it is never kept as a second queue
  behind Actions (plan section 4).
- During bootstrap the human is the only authority (ADR 0001); `.remora/tasks.json` and
  the board remain conventions until the P12-style Remora cutover
  (`docs/development/dogfooding.md`).

## 6. What P01 does not decide

- The production backend (P02a selects or reports no-go) and the CAS transport (P02a).
- Lease length, renewal cadence, poll and offline-grace intervals, skew bounds and the
  connected-stop target (P02a/P02b measure; plan section 4 defaults are proposals).
- The runtime profile and supported hosts (P02b; human Q11).
- Whether an AW worker on a supervisor-operated self-hosted runner satisfies criterion 1
  (P02a with the human; Q1).
- Every matrix decision point DP-01…DP-10 (human; `README.md` Q2–Q10, Q15).
- Remora's licence and whether Weave code is copied or re-implemented (human; Q13, Q14).
- The concrete state file layout and schemas (P05 for state, P03 for task/review schemas).
- Adoption of Symphony as a runner, or a hosted coordinator (not in pilot scope).
