# Weave behaviour and migration boundaries (criterion P01-AC02)

Status: proposed P01 synthesis. This file consolidates `weave-inventory.md` (cited as
**WI §…**; Weave paths as `W:path:lines` at pin `e7c3f3cab1e25994b96a948cbe27c96bb061d5a8`).
It does not re-derive the inventory and adds no new upstream observation. Controller
paths are identical at the baseline `d8010ae` (WI §A), so everything below applies to both.
No Weave code was executed.

## 1. Existing Weave behaviour

### 1.1 Task states and transitions (WI §C1)

| Behaviour | Weave today | Remora disposition |
| --- | --- | --- |
| Board statuses | `Todo`, `In Progress`, `In Review`, `Done` (`W:model.py:8`; `policy.json:10-15`). No Ready column; blocked/needs-human stays in its column | Remora adds `Ready for Development` and derives every status from accepted state (plan section 6) |
| Allowed transitions | Todo→In Progress, In Progress→In Review, In Review→In Progress, In Review→Done, In Progress→Todo (`transitions.py:19-22`); anything else fails (`:82-84`) | Event table of plan section 6; gates reused with adapter (contract-comparison rows 3-7) |
| Gate inputs | Todo→In Progress needs packet, coordinator lock, CLAIMED/DOCS_IMPACT/PLAN, worktree, unchanged requirements (`:87-95`). In Progress→In Review needs clean head, IMPLEMENTATION_READY, VERIFICATION_RESULT PASS, DOCS_AUDIT_RESULT PASS, LOCAL_REVIEW_RESULT PASS, REVIEW_REQUESTED (`:120-147`). In Progress→Todo needs RELEASED (`:109-110`) | Pure gates move to Remora after adaptation (WI §D3) |
| Labels | Seven `agent:*` labels; documented as not locks (`policy.json:169-212`) | Projection only |
| Event kinds | 24 kinds (`schemas/event.v1.schema.json:74-100`) | Need generation, stop and command fields (WI §E) |

### 1.2 Claims and leases (WI §C2)

| Behaviour | Weave today |
| --- | --- |
| Claim fields | CLAIMED carries `claim_expires_at`, `coordinator_host`, `work_type`, plus `run_id` and `attempt` (`event.v1.schema.json:122-129, 352-362`) |
| Expiry | now + `claim_ttl_hours` (8) (`cli.py:56-59`; `policy.json:214-217`). **Never read**: no renewal, takeover or expiry-based release; `heartbeat_expired` has no caller (`state.py:219-221`) |
| Exclusivity | Non-blocking `fcntl.flock` on `<state>/coordinator.lock` (`state.py:194-214`); "one claim per issue" = latest CLAIMED without RELEASED/COMPLETED in the **local ledger** (`cli.py:67-74`). Single host by Weave's own statement |
| Generation | None. `attempt` = 1 + count of local CLAIMED events (`cli.py:272`) |
| Release | RELEASED via the generic relay; not a reserved kind (`cli.py:373-385`) |
| Reservations | Packet `allowed_paths`, held through In Review; conservative overlap; default `**` (`scheduler.py:214-269`; `cli.py:214-255, 281`) |
| Capacity | `max_active_implementation_issues: 3`; In Review not counted (`scheduler.py:182-211`) |

### 1.3 Review budgets (WI §C3)

- Round = 1 + count(REVIEW_REQUESTED in the current attempt) (`reconcile.py:21-22`).
- Budget `max_rounds_per_attempt: 5` (`policy.json:218-221`); `review` refuses round N > budget
  (`cli.py:678-681`).
- Rounds reset across attempts, asserted by `test_review_budget_counts_the_current_attempt_only`
  (`tests/test_transitions.py:143-155`).
- REQUESTED rounds are counted, including outages published as BLOCKED (`cli.py:729-734`).
- Remora counts **completed** PASS/CHANGES_REQUESTED rounds **task-wide**, default 3 (plan
  section 8). The two counts are not convertible without recomputation (section 2, step 3).

### 1.4 Evidence and verdicts (WI §C4)

- Verdicts `PASS`, `REQUEST_CHANGES`, `BLOCKED`; no `UNVERIFIED`.
- Timeout, non-zero exit, empty or non-JSON output → `ReviewRejected` → BLOCKED with
  `blocker: review-outage` (`review.py:107-128`).
- `accept` rejects mismatched run, attempt, request, head, base, requirements digest and
  inconsistent PASS (`review.py:148-177`).
- VERIFICATION_RESULT is run by the coordinator in the claimed worktree with no environment
  scrubbing; no independence flag, executor identity or environment digest (`cli.py:453-490`).
- A reviewer that cannot rerun checks may still PASS (`W:docs/development/review.md:66-68`;
  issue #6 round 3).
- FINDING_DISPOSITION `fixed`/`rejected`/`accepted_by_maintainer` (`transitions.py:181-192`).
- Done-gate integration evidence is derived from PR and Git data (`integration.py:44-82`).
- Reserved kinds may be published only by their producing command (`publisher.py:23-29, 110-128`).

### 1.5 GitHub reads and writes (WI §C5)

- Reads: paginated, completeness-checked issues, milestones, **user-owned** Projects v2
  (`github.py:66`), PRs with checks and `main` protection (`github.py:39-275`).
- Writes: issue comments (event envelopes, PR mirror), Project Status (`gh project
  item-edit`), labels (`github.py:276-311`). No PR creation, push, merge, close or comment edit.
- Identity: every write uses the coordinator's `gh` session, the maintainer's personal account
  `quaat` with `repo` + `project` scopes (`policy.json:17-24`).

### 1.6 Commands and configuration (WI §C6)

- CLI `python3 -m tools.weave_workflow` with dry-run-by-default writers (`cli.py:798-888`).
- Configuration: `policy.json`, `docmap.json`, `WEAVE_WORKFLOW_STATE`, `.claude/settings.json`.
- Human command: an unedited `/weave-decision` comment from a `maintainer_logins` author,
  not already in the ledger (`events.py:139-150`). No command ID, correlation, deduplication
  or scope beyond login membership.

### 1.7 Where authoritative state lives (WI §C7)

- **Local ledger** under `$(git rev-parse --git-common-dir)/weave-workflow/`: `ledger.jsonl`
  (event, delivery, operation, packet, run, evidence, subagent, mirror), `outbox/`,
  `checkpoint.json`, `active-run.json`, `coordinator.lock`, `stop-guard.json`,
  `docs-audit-pending.json`, `runs/<run_id>/…` (`state.py:1-5, 31-43`).
- **Issue comments** carry envelopes, trusted only when matched by a local delivery record
  and a coordinator author (`events.py:117-136`). Without the ledger they are untrusted.
- **Board and issue state** are eligibility, capacity and completion inputs
  (`scheduler.py:141-157, 193-197, 384-412`).
- **Git**: `agent/<N>-<slug>` branches, `.worktrees/`, `origin/main`.
- **Policy** in the repository (`tools/weave_workflow/policy.json`).

### 1.8 Triggers that can write (WI §C8)

- Claude Code hooks on nine events write the local ledger, checkpoint and guard files; no
  network writes (`.claude/settings.json:13-43`; `hooks.py:121-234`).
- GitHub Projects built-in automation "Item closed → Done" (not readable via API).
- No Actions workflow writes controller state; no daemon, cron, webhook or hosted controller.
  All controller writes come from a human-started Claude Code session running the
  `weave-project` skill.

## 2. Migration boundary for each P12 cutover step

Plan section 11, P12 steps 1-5. "Boundary" is what crosses into Remora and what must stop.
Artifacts and gaps are from WI §D1; "Remora must add" are the prerequisites that must exist
before P12, with the owning task.

| Step | Weave artifacts involved (WI §D1) | Boundary | Remora must add before P12 | Owner |
| --- | --- | --- | --- | --- |
| 1. Pause intake/dispatch; drain or stop; confirm no held claims, uncertain processes, pending publications, in-flight effects | Stop the `weave-project` session; `run stop --reason` (`cli.py:784-790`); `outbox/` (`cli.py:573-577`); partial `operation` records (`reconcile.py:73-82`; `transitions.py:295-310`); held-claim set (`cli.py:67-74`) | Nothing crosses yet. Weave has no process registry: subagents live inside the coordinator's Claude session and the Codex reviewer is a child with a timeout. The PR mirror comment is not write-ahead, so a crash can leave an unrecorded gap | A cutover checklist that inspects the legacy outbox, partial operations and held claims, and records an explicit human confirmation of quiescence (expiry alone is not confirmation) | P11 (rehearsal), P12 |
| 2. Export ledger, issue-event history, config, candidate/checkpoint refs; record a cutover marker and revision; revoke legacy authority; disable triggers | Whole `<git-common-dir>/weave-workflow/` directory on the coordinator host; all `<!-- weave-agent:event:v1 -->` comments and `/weave-decision` comments; `policy.json`, `docmap.json`, `schemas/`, `.claude/**`; `agent/<N>-<slug>` branches, `.worktrees/*`, local-only preserved branches; triggers: hooks, the skill, Projects "item closed → Done" | The **ledger export is load-bearing**: without it, exported comments cannot be authenticated by Weave's own rule (`events.py:129-135`). Legacy authority is the maintainer's personal token, so revoking it revokes the human: fencing must come from disabling the tooling and from Remora refusing `weave-agent` envelopes after the marker | A cutover-marker / authority-epoch record; an importer that verifies comments against the exported delivery records; a reducer rule that rejects legacy envelopes after the marker | P05 (epoch), P11/P12 (importer) |
| 3. Import open tasks, candidates, questions, resource holds, task-wide review history | Open tasks: board non-Done plus held claims. Candidates: `head_sha`/`base_sha` in IMPLEMENTATION_READY, VERIFICATION_RESULT, REVIEW_REQUESTED, REVIEW_RESULT. Questions: QUESTION/ANSWER by `correlation_id`/`causation_id`, BLOCKED `decision`/`maintainer-action`, `agent:needs-human`. Holds: `allowed_paths` in local packet files. History: REVIEW_REQUESTED/RESULT, CHANGES_REQUESTED, FINDING_DISPOSITION across attempts | Weave has no question IDs or designated human; "unresolved" must be inferred from QUESTION without a caused ANSWER, and some answers arrived as relayed ANSWER text. Review counts must be **recomputed** from REVIEW_RESULT verdicts across all attempts; a REQUESTED without a RESULT is ambiguous and blocks that task for human reconciliation. Resource holds are not on GitHub | Question records with stable ID and designated human; task-wide completed-round counter; an import recount rule with an explicit `ambiguous` outcome; reservation records | P07 (questions), P08 (rounds), P05 (reservations), P12 (import) |
| 4. New authority epoch; invalidate legacy claims; validate mappings, readiness, counts, evidence mode; dry-run diff; authorized acceptance | Legacy claims = every CLAIMED without later RELEASED/COMPLETED. Dependency sources: native blocked-by, `## Depends on`, `policy.json` dependencies, epic order, milestone `requires` (`scheduler.py:44-94`) | No claim generation exists to invalidate (`attempt` is the closest analogue). No evidence mode exists: historical completions are closest to "supplied plus CI status at merge" and need an explicit evidence-mode label. Task revision is only a body-section digest (`model.py:151-160`) | Epoch initialization with no imported active claim; evidence-mode labels on imported completions; approved revision objects created from imported definitions; dependency-source mapping into `plan-compiler` | P05, P08/P09, P03, P12 |
| 5. Start new supervisors in `trusted_ci`; reject late legacy events; rollback path | Late writers: any session still running `python3 -m tools.weave_workflow … --apply`, `reconcile --apply` replaying `outbox/`, Projects automation | Rollback into "an explicit compatible legacy state" would require appending matching `delivery` records to the legacy local ledger (`events.py:129-135`), outside the new controller's authority. The reverse mapping may be unsafe; the plan allows remaining paused (plan section 11, P12 step 5) | Rejection tests for late legacy envelopes; a documented reverse-mapping decision (likely "remain paused for manual recovery") | P11 (rehearsal), P12 |

## 3. What Weave does not record today (WI §D2) and what Remora must add

| # | Not recorded in Weave | Remora record (interface) | Owner before P12 |
| --- | --- | --- | --- |
| 1 | Claim generation / authority epoch | Generation in claims and command envelopes; epoch in state (`state-backend`) | P05 (P02a proves fencing) |
| 2 | Lease renewal and heartbeat records | Lease expiry and rare renewal transitions; heartbeats stay local and diagnostic | P05 (cadence from P02a) |
| 3 | Stop requests and stop confirmations | `sessions_and_stop` records; `execution.stop_request` / `stop_confirmed` / `authority_lost` | P05, P06, P07 (P02b proves runtime side) |
| 4 | Durable command IDs and receipts | `command_receipts`; `command-ingestion` | P05, P07 |
| 5 | Question IDs, designated human, superseded-question handling | `questions` records | P07 |
| 6 | Evidence mode, per-check `independently_executed`, executor identity, environment digest | `evidence-records.record_check_evidence` | P08, P09 |
| 7 | Task-wide completed-round count | `review_rounds` | P08 |
| 8 | Hard-resource reservations distinct from path globs | `resource_reservations` with hard/ordinary class | P03 (declaration), P05 |
| 9 | Cross-host-verifiable provenance (authenticity depends on one host's ledger) | State-branch history plus authenticated writer identities (matrix) | P05, P09 |
| 10 | Cutover marker / epoch | Epoch-change transition | P05, P12 |

## 4. Stays, moves, or is replaced (WI §D3, §E)

- **Stays with Weave the language project:** `inventory-proof/`, `agent-kit/`,
  `specification/`, `evidence/`, Weave decisions, Weave-specific `policy.json` values,
  `docmap.json`, `derive_checks` (`cli.py:182-211`), Weave prompts in `.claude/agents/*`
  and `review.py:25-45`, `.claude/skills/**`.
- **Candidate to move to Remora as generic Python after adaptation** (subject to README
  Q13/Q14 and a NOTICE scope request): `schema.py` (96 SLOC, as-is), `events.py` ordering
  (18, as-is), envelope/redaction (79), digests in `model.py`, `scheduler.py` (345),
  transition gates (174), `integration.py` (60), `review.py` (144), docs-audit engine (580,
  separated from Weave's docmap and from executing audited code), reconciliation concepts.
- **Replaced by the selected backend, not moved:** local ledger as authority and the
  `flock` (`state.py`, 168), comment-envelope authentication against the local ledger
  (`events.py` 110-152, 34), board writes inside the transition commit path (executor 106,
  becomes a projection reconciler under the narrow adapter).
- **Unknown, pending P02b:** `hooks.py` and the Claude settings guards (222 + 5 SLOC);
  Weave states they are not a security boundary.

## 5. Unknowns that affect the migration (WI §H)

- The contents and size of the legacy local ledger on host `gengar` are unknown and not on
  GitHub; this decides step 2 feasibility (README Q12).
- Live Projects automation settings for the Weave board are unverified.
- The "89 passing focused controller tests" could not be reproduced statically (163 test
  methods counted); executed status at either SHA is unverified.
- Weave docs conflict on whether an end-to-end run has happened and on heartbeat.
