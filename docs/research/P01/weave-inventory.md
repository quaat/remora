# P01 research: Weave controller inventory

Task: P01 (Reuse and authority decision), sub-scope "Weave inventory". Supports P01-AC02
(existing Weave behaviour and migration boundaries) and supplies inputs for P01-AC01 and
P02a rejection criterion 3. This file is evidence, not a decision. Nothing here selects a
backend or changes policy.

Citation conventions:

- `W:path:lines` is a path in Weave at the pinned commit `e7c3f3c`
  (`/tmp/claude-1000/upstream/weave`).
- `I6:<comment id>` is a comment of quaat/weave issue #6 as returned by the GitHub REST API
  (section G).
- `R:path:lines` is a path in this Remora repository.

Labels: **[observed]** means I read it in the pinned source or fetched API data.
**[documented]** means Weave's own documentation says it and I did not test it.
**[inference]** is my reasoning from observed facts. No Weave code, tests, hooks or build
tools were executed. Counts come from static parsing (`python3.12 -I` scripts kept under
`/tmp/claude-1000/research-scripts/`, which read files as text and import nothing from the
Weave tree).

---

## A. Pin and licence record

| Item | Value |
| --- | --- |
| Repository | https://github.com/quaat/weave |
| Pinned commit | `e7c3f3cab1e25994b96a948cbe27c96bb061d5a8` (commit date 2026-10-29T22:03:18+01:00, "Merge pull request #83 …") [observed] |
| Fetch | `git fetch --depth 1 origin <sha>` into `/tmp/claude-1000/upstream/weave` at 2026-10-29T23:16:41Z (UTC) [observed] |
| Baseline commit | `d8010aec6746bbdcc54b21801c537d28917c0533` (2026-10-29T18:35:41+01:00, "Merge pull request #81 …"), fetched the same way into `/tmp/claude-1000/upstream/weave-baseline` at 2026-10-29T23:16:49Z [observed] |
| Licence file | `LICENSE` (MIT text, "Copyright (c) 2026 Thomas F. Hagelien"), W:LICENSE:1-21 [observed] |
| SPDX | `MIT`. The `LICENSE` text matches the MIT template, and `W:LICENSES/MIT.txt` is byte-identical: both sha256 `b578d9a7c9556921a95db16fe27e74c6526fa9b71c4bbf0a2da68037534f0b71` [observed] |
| Per-path licensing | `W:REUSE.toml:15-92` annotates every `tools/weave_workflow/**` file, `docs/development/*.md`, `.claude/**` and `.github/**` as `SPDX-License-Identifier = "MIT"` with `SPDX-FileCopyrightText = "2026 Thomas F. Hagelien"` (lines 91-92) [observed] |
| Decision record | `W:docs/decisions/0002-licence-terms.md:4-6,22-28` records the maintainer decision "MIT for all of Weave; rights holder as in LICENSE" (28 Oct 2026). It names "the workflow tooling" as covered code [observed] |
| Other licence texts | `W:LICENSES/BSD-2-Clause.txt` (sha256 `f32fb3b4…1aec1df`), `Bitstream-Vera.txt` (`5b3b4d3c…d8e38`), `LicenseRef-Arev-Fonts.txt` (`ff385c27…12f8fd9`) and `OFL-1.1-RFN.txt` (`8eea8287…bcfd`). These cover the Sphinx-derived `weave.sty` and the fonts embedded in the PDFs (`W:REUSE.toml:443-500`). None applies to `tools/`, `docs/development/` or `.claude/` [observed]. The full digests are in `pins-weave.json` |
| NOTICE file | None at the root (searched: `ls` of the repository root). The attribution requirement is the MIT condition: keep the copyright and permission notice in copies or substantial portions (W:LICENSE:12-13) [observed] |
| Vendored third-party code in the controller paths | None found. The controller is standard-library-only Python 3.11+ (W:docs/development/agent-workflow.md:23-25; imports in `tools/weave_workflow/*.py` are stdlib or package-relative) [observed] |
| Third-party notices elsewhere | Furo template (MIT), Sphinx `sphinxmanual.cls` fragment (BSD-2-Clause) and fonts in the PDFs (W:REUSE.toml:430-500). These belong to Weave the language and its specification, not the controller [observed] |

**Constraints on copying Python into Remora** [observed + inference]

- MIT permits copying and modification if the copyright and permission notice travel with
  the copied portions. Remora's `R:NOTICE.md:10-15` currently states that no upstream code
  was copied and that no Remora licence has been chosen. Copying Weave code would need a
  NOTICE/attribution update and REUSE-style per-file annotation. That is a policy change for
  the orchestrator and human, not for this research.
- `W:docs/decisions/0002-licence-terms.md:259-267` records that commits touching
  `tools/weave_workflow/` carry `Co-Authored-By` trailers naming an AI coding assistant, and
  that a single human identity authored them. I make no legal assessment of what this means
  for copyright. Flagged for the human owner.
- `W:REUSE.toml:9` says the metadata "is not a completed provenance audit". The open items
  in `W:follow-up` (FU-01…FU-04) concern PDFs and fonts, not the controller.
- Whether the Weave rights holder and the Remora owner are the same person is **unverified**.

**Baseline vs pin** [observed]: `diff -rq` over `tools/`, `docs/`, `.claude/`, `.github/`,
`REUSE.toml`, `LICENSE`, `LICENSES/`, `AGENTS.md`, `CLAUDE.md` and `follow-up` reports them
identical at `d8010ae` and `e7c3f3c`. The 44 differing paths are all in `agent-kit/`,
`evidence/`, `specification/`, `README.md` and `STABILITY.md` (result-label work, PR #83).
Every controller finding below therefore applies equally to the baseline.

---

## B. Repository map (controller-like behaviour)

**Directory confirmation** [observed]: `tools/weave_workflow/` (32 tracked files) and
`docs/development/` (14 files) both exist at the pin and at the baseline. This confirms
R:docs/plan/generic-agentic-harness-plan.md:35 and refutes the contrary reviewer observation
quoted there.

Counting method: "total" is physical lines. "SLOC" is lines carrying Python code tokens,
excluding blank, comment-only and docstring lines (tokenizer + AST,
`research-scripts/weave_loc.py`).

**Non-generated:** none of these files is listed under `generated_documents` in
`W:tools/weave_workflow/docmap.json`. The generated targets are `inventory-proof/*`,
specification chapters and the section of `docs/development/documentation-map.md` between
its markers (docmap.json:39-77) [observed]. So every controller file below is hand-maintained.

Tests are `unittest` methods named `test*`, counted statically.

| Path | Total | SLOC | Responsibility | Covering tests (static import evidence) |
| --- | ---: | ---: | --- | --- |
| `tools/weave_workflow/cli.py` | 897 | 785 | All commands: claim (task packet, CLAIMED/DOCS_IMPACT/PLAN, worktree), event relay, verify, milestone-gate, transition, reconcile, docs-audit, review, run start/stop, hook; `derive_checks` (Weave component checks) | `test_review_findings.py`, `test_hooks.py` (`cli.main`), `test_scheduler.py` (`held_claims`), `support.py` |
| `tools/weave_workflow/scheduler.py` | 427 | 345 | Dependency graph (native blocked-by, `## Depends on`, policy), cycles, milestone exit gates, deterministic selection, concurrency count, conservative path-overlap reservation | `test_scheduler.py`, `test_review_findings.py` |
| `tools/weave_workflow/transitions.py` | 323 | 280 | Pure gate functions for the 5 allowed transitions (lines 1-207, SLOC 174); guarded executor: intent → board write → read-back → STATE_CHANGED/COMPLETED → labels, plus recovery (208-323, SLOC 106) | `test_transitions.py`, `test_protocol.py` (`PartialWriteTests`) |
| `tools/weave_workflow/github.py` | 403 | 335 | `GhCli`: paginated GraphQL/REST reads with completeness checks (1-275, SLOC 232); writes: comment, Status, labels (276-311, SLOC 28); `FakeGitHub` test double (312-390, SLOC 65); `milestone_index` (391-403) | `test_github_adapter.py` (fake `gh` binary), `FakeGitHub` used across suites |
| `tools/weave_workflow/state.py` | 221 | 168 | Local durable state under `<git-common-dir>/weave-workflow`: append-only `ledger.jsonl`, outbox, checkpoint, active-run file, run dirs, single-host `flock` coordinator lock, unused `heartbeat_expired` | `test_protocol.py`, `test_hooks.py`, `test_review_findings.py` |
| `tools/weave_workflow/events.py` | 174 | 131 | Envelope build/validate/render, secret redaction, ledger-based authentication, `/weave-decision` recognition, causal ordering | `test_protocol.py` |
| `tools/weave_workflow/publisher.py` | 139 | 106 | Write-ahead publication of events as issue comments, in order, with duplicate lookup after ambiguous writes; reserved-origin rule; authenticated event read | `test_protocol.py`, `test_review_findings.py` |
| `tools/weave_workflow/review.py` | 177 | 144 | Review packet, Codex `exec` adapter (read-only, ephemeral, scrubbed env, `--output-schema`), result acceptance bound to request/head/base/requirements | `test_transitions.py` (fake codex binary; `accept`, `run_codex`), `test_review_findings.py` (`render_result`) |
| `tools/weave_workflow/reconcile.py` | 140 | 121 | Restart reconciliation: outbox replay, partial operations, board vs. recorded state, held claims, stale PR heads, orphan worktrees, capacity | `test_scheduler.py`, `test_transitions.py` |
| `tools/weave_workflow/integration.py` | 82 | 60 | Done-gate integration evidence from PR data and local Git (merged, claim branch, required checks, merge containment, tree equality, human review) | `test_review_findings.py` |
| `tools/weave_workflow/model.py` | 197 | 148 | Snapshot dataclasses; acceptance-criterion extraction (`AC-n` + text digests); `requirements_digest` | indirect (all suites) |
| `tools/weave_workflow/schema.py` | 117 | 96 | Fail-closed JSON-Schema-subset validator | indirect via `events.validate` (`test_protocol.py`) |
| `tools/weave_workflow/docs_audit.py` | 706 | 580 | Documentation-impact and drift audit driven by `docmap.json`; change scope with base-map floor | `test_docs_audit.py` |
| `tools/weave_workflow/hooks.py` | 266 | 222 | Claude Code hook handlers: worker command/edit guards, credential-scrub prefix, evidence/checkpoint records, Stop guard | `test_hooks.py` |
| `tools/weave_workflow/capabilities.py` | 68 | 60 | Tool/scope discovery (gh scopes, codex flags, versions) | not found (searched tests for `capabilities`, `inspect(`) |
| `tools/weave_workflow/report.py` | 122 | 114 | Dry-run Markdown report | not found (searched tests for `dry_run_report`, `report`) |
| `tools/weave_workflow/__init__.py`, `__main__.py` | 6 + 3 | 1 + 2 | Package entry | — |
| `tools/weave_workflow/policy.json` | 271 | n/a | Project contract: repo, project, actors, milestones/epics, dependencies, labels, concurrency (`claim_ttl_hours: 8`), review budget (5), Codex flags, protected paths, integration checks | `test_transitions.py:148` asserts budget 5 |
| `tools/weave_workflow/docmap.json` | 442 | n/a | Documentation map (Weave-specific content) | `test_docs_audit.py` |
| `tools/weave_workflow/schemas/event.v1.schema.json` | 806 | n/a | 24 event kinds with per-kind required fields | `test_protocol.py` |
| `tools/weave_workflow/schemas/review-result.v1.schema.json` | 170 | n/a | Reviewer output schema (`PASS`/`REQUEST_CHANGES`/`BLOCKED`) | `test_transitions.py` |
| `tools/weave_workflow/schemas/task-packet.v1.schema.json` | 146 | n/a | Task packet schema | `test_review_findings.py` |
| `tools/weave_workflow/tests/*` (8 files) | 2327 | 1930 | 163 test methods: docs_audit 34, transitions 34, scheduler 33, review_findings 25, protocol 16, hooks 15, github_adapter 6; `support.py` 198/157 fixtures | — |
| `.claude/hooks/weave_hook.py` | 9 | 5 | Hook entry shim | `test_hooks.py` (`test_settings_register_every_handler`) |
| `.claude/settings.json` | 45 | n/a | Registers 9 hook events; deny force-push; ask merge/release | `test_hooks.py` |
| `.claude/skills/*/SKILL.md` (4), `.claude/agents/*.md` (6) | 343 | n/a | Orchestrator, task, review and docs skills; 6 subagent prompts | — |
| `docs/development/*.md` (14) | 1278 | n/a | Policy and operator documentation | `docs_audit` checks |
| `.github/workflows/ci.yml` | 110 | n/a | CI (`contents: read`); job "workflow tooling and documentation audit" runs the workflow tests and docs-audit (ci.yml:97-110) | — |

**Totals** [observed]: production Python in `tools/weave_workflow/` is 18 files, 4,468
physical lines and 3,698 SLOC. Tests are 9 files, 2,327 lines, 1,930 SLOC and 163 test
methods. JSON configuration and schemas add 1,835 lines (271 + 442 + 806 + 170 + 146).

Mapping the plan's retained concepts to code [observed]:

- Task packets: `cli.py:152-179`, `schemas/task-packet.v1.schema.json`.
- Criterion digests: `model.py:137-160`.
- Deterministic scheduling: `scheduler.py:299-427`.
- Transition validation: `transitions.py:19-207`.
- Event/outbox: `events.py`, `publisher.py`, `state.py:131-150`.
- Documentation-impact checks: `docs_audit.py:584-706`, `cli.py:282-285,580-591`.
- Codex review adapter: `review.py:93-130`.
- Claims with expiry and coordinator-host metadata: `cli.py:56-59,313-315`.
- GitHub projection: `transitions.py:208-323`, `github.py:276-311`.
- Candidate publication: not present. Branches are local worktrees; PRs are opened by the
  orchestrator session per `W:.claude/skills/weave-project/SKILL.md:53-55`, not by
  controller code (searched `github.py`, `cli.py` for `pulls`/`pr create`: none).
- Human questions and commands: `events.py:139-150` and QUESTION/ANSWER kinds.
- Review budgets: `transitions.py:177-180`, `reconcile.py:21-22`, `cli.py:678-681`.

---

## C. Existing Weave behaviour (P01-AC02, first half)

### C1. Task states and transitions [observed]

- Board statuses are `Todo`, `In Progress`, `In Review` and `Done` (W:model.py:8;
  W:policy.json:10-15).
- Allowed transitions are Todo→In Progress, In Progress→In Review, In Review→In Progress,
  In Review→Done and In Progress→Todo (W:transitions.py:19-22). Anything else fails
  (transitions.py:82-84).
- **Todo→In Progress** needs: a validated packet, the exclusive coordinator lock held,
  CLAIMED, DOCS_IMPACT and PLAN published, a worktree assigned, and requirements unchanged
  since PLAN (transitions.py:87-95).
- **In Progress→In Review** needs, all for the current head: a clean committed head;
  IMPLEMENTATION_READY mapping every PLAN criterion; VERIFICATION_RESULT PASS; a
  change-scope DOCS_AUDIT_RESULT PASS cited by IMPLEMENTATION_READY; local and safety
  LOCAL_REVIEW_RESULT PASS; and REVIEW_REQUESTED (transitions.py:120-147).
- **In Review→In Progress** is allowed on any of: REQUEST_CHANGES plus CHANGES_REQUESTED, a
  moved head, failed evidence, or a requirement change (transitions.py:98-106).
- **In Review→Done**: see C4/C5 (transitions.py:150-206).
- **In Progress→Todo** needs RELEASED (transitions.py:109-110).
- Label signals are `agent:managed`, `agent:blocked`, `agent:needs-human`,
  `agent:review-requested`, `agent:changes-requested`, `agent:ready-to-merge` and
  `agent:docs-stale` (W:policy.json:169-212). Labels are not locks
  (W:docs/development/communication-protocol.md:97-102).
- There is no separate "Ready" state and no fifth column. Blocked or needs-human work stays
  in its column (W:docs/development/agent-workflow.md:72-76).
- The 24 event kinds are listed in W:schemas/event.v1.schema.json:74-100 and their required
  fields in W:docs/development/communication-protocol.md:20-42.

### C2. Claim/lease semantics [observed]

- **Fields.** CLAIMED requires `claim_expires_at`, `coordinator_host` and `work_type`
  (W:schemas/event.v1.schema.json:122-129,352-362), plus the common envelope with `run_id`
  and `attempt`.
- **Expiry and host.** `claim_expires_at` is set to now + `claim_ttl_hours` (default and
  configured 8) (W:cli.py:56-59; W:policy.json:214-217). `coordinator_host` is
  `socket.gethostname()` (cli.py:313-315).
  - Live data: issue #6 claims record `coordinator_host: "gengar"` with 8-hour expiries
    (I6:6502477848, I6:6503285115).
- **Expiry is never read.** A repository-wide search for `claim_expires_at`,
  `coordinator_host`, `heartbeat_expired`, `renew` and `takeover` finds only the schema,
  the writer in `cli.py`, test fixtures and docs. `state.heartbeat_expired`
  (W:state.py:219-221) has no caller. There is no heartbeat event kind
  (schema kinds, line 74-100).
- **No renewal or takeover.** No renewal, takeover or expiry-based release exists. The plan's
  statement "published claims already contain expiry and coordinator-host metadata"
  (R:…plan.md:37) is **confirmed as recorded fields only**. No behaviour depends on them.
- **Exclusivity.**
  - A non-blocking `fcntl.flock` on `<state>/coordinator.lock`, writing run_id/pid/host
    (W:state.py:194-214). `claim` and `transition --apply` take it (cli.py:298, 553).
    Selection is repeated under the lock (cli.py:299-304).
  - "One claim per issue" means latest CLAIMED not followed by RELEASED/COMPLETED in the
    **local ledger** (cli.py:67-74; scheduler.py:341-348).
  - Weave documents this as single-host only, with no multi-host fencing
    (W:docs/development/github-adapter.md:41-49; agent-workflow.md:142;
    capabilities.md:40).
- **Generation.** No claim generation or fencing token exists (searched `generation`,
  `fenc`, `epoch` in `tools/weave_workflow/*.py`: no matches apart from a docs-audit
  comment). `attempt` is `1 + count(CLAIMED events for the issue in the local ledger)`
  (cli.py:272).
- **Release.** RELEASED is published through the generic relay by the orchestrator. It is
  not a reserved kind (cli.py:373-385; publisher.py:23-29).
- **Resource reservations** are the packet's `allowed_paths`, held while a claim is held,
  In Review included. Overlap is conservative (`**` overlaps everything), and shared
  generated artefacts conflict (scheduler.py:214-269; cli.py:214-255). The default is `**`
  (cli.py:281).
- **Capacity.** `max_active_implementation_issues: 3`. In Review does not count. A return to
  In Progress may exceed the limit (scheduler.py:182-211, 352-357).

### C3. Review-round accounting [observed]

- **Round number** = `1 + count(REVIEW_REQUESTED in the current attempt)` (W:reconcile.py:21-22).
  The current attempt is the highest `attempt` among the issue's authenticated events
  (transitions.py:48-51).
- **Budget.** The Done gate fails when `count(REVIEW_REQUESTED, attempt=current) >
  review.max_rounds_per_attempt` (transitions.py:177-180), with `max_rounds_per_attempt: 5`
  (policy.json:218-221: "Rounds 1-3 standard, 4-5 extra … #72"). `review` refuses to start
  round N > budget (cli.py:678-681).
- **Rounds reset across attempts.** "Rounds of a released attempt do not count"
  (W:docs/development/transitions.md:16). Tests assert it: `test_review_budget_counts_the_current_attempt_only`
  (W:tests/test_transitions.py:143-155).
- **REQUESTED, not completed, rounds are counted.** A REVIEW_REQUESTED followed by a
  rejected or timed-out result (published as BLOCKED, cli.py:729-734) still consumes a round.

### C4. Evidence and verdict handling [observed]

- **Verdicts.** Reviewer verdicts are `PASS`, `REQUEST_CHANGES` and `BLOCKED`
  (schemas/event.v1.schema.json:218-224; review-result schema). There is no `UNVERIFIED`.
- **Rejected results.** Timeout, non-zero exit, empty output and non-JSON raise
  `ReviewRejected` (W:review.py:107-128), which is published as BLOCKED with
  `blocker: review-outage` and is never a verdict (cli.py:729-734).
  - `accept` rejects any mismatch in run_id, attempt, request_id, head, base or
    requirements digest, and any "inconsistent PASS" (missing or unmet criterion, or a
    blocking/high/critical finding) (review.py:148-177).
- **Verification checks** (VERIFICATION_RESULT) are run by the coordinator on its own host
  in the claimed worktree. It uses no environment scrubbing and records argv, cwd, exit code
  and a local log path (W:cli.py:453-490). Whether a check was run independently is not
  recorded, and there is no executor identity or environment digest.
- **Reviewer limitations.** The reviewer runs read-only and "may be unable to rerun test
  suites". Its limitations are reported, yet PASS is still accepted
  (W:docs/development/review.md:66-68).
  - Issue #6 round 3: "full local test command and docs audit could not complete here. The
    packet records those checks passing" (I6:6503850141).
- **Findings.** Findings need a FINDING_DISPOSITION (`fixed`, `rejected` or
  `accepted_by_maintainer`). Maintainer acceptance requires a recorded `/weave-decision`
  (transitions.py:181-192).
- **Done gate integration evidence** is derived, not supplied (W:integration.py:44-82):
  - a merged PR from the claim's branch that closes the issue;
  - PR head equals the reviewed head;
  - all required checks present, complete and passing (policy plus branch protection);
  - merge commit is an ancestor of `origin/main`;
  - the tree equals `merge-tree(parent, head)`;
  - human review: an approving decision under protection, otherwise merged by a maintainer
    login (integration.py:62-68).
- **Reserved kinds.** Gate-relevant kinds may be published only by their producing command
  ("origin" recorded in the local delivery record) (W:publisher.py:23-29, 110-128).

### C5. GitHub reads and writes [observed]

- **Reads** (W:github.py:39-275), all paginated with total-count checks:
  - issues with labels, milestone, `blockedBy`, `subIssues`, `parent` and comments;
  - milestones;
  - user-owned Projects v2 items and the Status field (`user(login:…)`, github.py:66, so
    organisation projects are not supported);
  - PRs with head/base, merge commit, `reviewDecision`, `mergedBy`, closing issues and the
    status-check rollup of the last commit;
  - branch protection of `main`.
- **Writes**:
  - issue comments, used for event envelopes and the PR mirror (github.py:278-281;
    cli.py:742-746);
  - project Status via `gh project item-edit` (github.py:283-286);
  - label add/remove/create (github.py:295-310).
  - No PR creation, branch push, merge, issue close or comment edit appears in controller
    code (searched `github.py`, `cli.py`).
- **Identity.** All writes use the coordinator's `gh` session. At the pin this is the
  maintainer's personal account `quaat`, with `repo` and `project` scopes
  (W:policy.json:17-24; W:docs/development/agent-workflow.md:32-34, 136-139;
  github-adapter.md:60-66). Every issue #6 envelope was posted by `quaat` (I6 list,
  section G).

### C6. Commands and configuration surface [observed]

- **CLI** `python3 -m tools.weave_workflow` (W:cli.py:798-888): `capabilities`, `discover
  [--save]`, `plan`, `reconcile [--apply]`, `claim N [--base] [--allowed-path]* [--non-goal]*
  [--override-order] [--apply]`, `event validate|publish FILE`, `new-event`,
  `transition N STATUS [--worktree|--head] [--apply]`, `verify N [--apply]`,
  `milestone-gate Mx [--evidence] [--apply]`, `outbox`, `docs-audit [--base] [--impact]
  [--repo] [--publish N] [--apply]`, `docs-map [--write]`, `review N --worktree [--base]
  [--ci-link]* [--limitation]* [--evidence]* [--delta] [--apply]`, `report`,
  `run start|stop|status`, `hook EVENT`.
  - Global flags are `--json` and `--fixture SNAPSHOT` (fake GitHub).
  - Every writing command is a dry run without `--apply` (cli.py:1-2).
- **Configuration**:
  - `policy.json` (C2-C5);
  - `docmap.json`;
  - environment `WEAVE_WORKFLOW_STATE` (state-dir override, W:state.py:31-43);
  - Claude Code settings/hooks (`.claude/settings.json:1-45`).
- **Human command**: a maintainer comment whose first line starts `/weave-decision`, is
  unedited, comes from a `maintainer_logins` author and is not in the ledger
  (W:events.py:139-150). The coordinator refuses to post that prefix (events.py:76-77).
  There is no command ID, question correlation, deduplication or authorization scope beyond
  login membership.

### C7. Where authoritative state lives [observed + inference]

- **Local ledger.** The local, uncommitted ledger and files under
  `$(git rev-parse --git-common-dir)/weave-workflow/` [observed] (W:state.py:1-5, 31-43;
  agent-workflow.md:42-44) hold:
  - `ledger.jsonl` (types `event`, `delivery`, `operation`, `packet`, `run`, `evidence`,
    `subagent`, `mirror`);
  - `outbox/*.json`;
  - `checkpoint.json`, `active-run.json`, `coordinator.lock`, `stop-guard.json`,
    `docs-audit-pending.json`;
  - `runs/<run_id>/packet-<N>-a<attempt>.json`, `verify-*` logs, and `reviews/` (packets,
    Codex results and event streams) (cli.py:325-328, 472-483, 719-721).
- **GitHub issue comments** carry the event envelopes. They are trusted **only** if their
  comment ID and envelope digest match a delivery record in the local ledger and the author
  is a coordinator login (W:events.py:117-136; publisher.py:110-128). [inference] Another
  host, or a lost ledger, sees the same comments as untrusted. GitHub holds the projection,
  and the local ledger is what makes it authoritative.
- **GitHub board and issue state** are read as **inputs to eligibility**, not only as
  projections [observed]:
  - candidates must be on the board in `Todo` (scheduler.py:384-393);
  - prerequisites count as complete when the issue is closed-as-completed **and** the board
    shows Done (scheduler.py:401-412);
  - open cards In Progress count against capacity (scheduler.py:193-197);
  - milestone gates require closed epics plus a GATE_EVALUATED event (scheduler.py:141-157).
- **Git**: `agent/<N>-<slug>` branches and `.worktrees/` (cli.py:146-149, 279-280, 324),
  plus `origin/main` for integration.
- **Policy** is in the repository: `tools/weave_workflow/policy.json`, a protected path for
  workers (policy.json:237-247).

### C8. Triggers, callbacks and schedules that can write [observed]

- **Claude Code hooks** (`W:.claude/settings.json:13-43`) run `weave_hook.py` on
  SessionStart, PreToolUse, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop,
  Stop, PreCompact and SessionEnd. They write the local ledger (`evidence`, `subagent`,
  `run`), the checkpoint, `stop-guard.json` and `docs-audit-pending.json`
  (W:hooks.py:121-234). They make no network writes ("no network",
  hooks.py:1-6) [observed in code; not executed].
- **GitHub Projects built-in automation.** "Item closed → Done" (and observed auto-add/In
  Progress) is active on the board. Weave cannot read it through the API, so the
  documentation tells the maintainer to inspect it by hand
  (W:docs/development/capabilities.md:34; transitions.md:55-71). `transition N Done`
  explicitly accepts the closed→Done move (transitions.py:54-62).
- **GitHub Actions**: there is no workflow with a schedule or with issue/project write
  permissions (searched `on:`/`permissions` in `.github/workflows/*.yml`).
  - `ci.yml` is `contents: read`.
  - `docs.yml` deploys Pages (`pages: write`, docs.yml:61-71).
  - `pdf.yml` attaches release assets (`contents: write`, pdf.yml:19-20, 49-57).
  - None writes controller state.
- **No daemon, cron, webhook or Actions-hosted controller** (searched the tree). All
  controller writes happen when a human-started Claude Code session runs the
  `weave-project` skill and its CLI commands
  (W:.claude/skills/weave-project/SKILL.md:17-36).

---

## D. Migration boundaries (P01-AC02, second half)

### D1. P12 cutover steps mapped to Weave artifacts (R:…plan.md:400-406)

| Cutover step | Concrete Weave artifact(s) | Notes / gaps |
| --- | --- | --- |
| 1. Pause intake and dispatch | Stop the `weave-project` skill session; `run stop --reason` (cli.py:784-790) clears `active-run.json`; check `outbox` (cli.py:573-577) and partial operations (`reconcile`, reconcile.py:73-82) | **Held claims**: the local ledger's held set (cli.py:67-74). **Uncertain processes**: there is no process registry. Subagents run inside the coordinator's Claude session (roles.md:46-48); `SubagentStart/Stop` ledger records exist only during a run (hooks.py:159-166). The Codex reviewer is a child process with a timeout (review.py:107-112). **Pending publications**: `outbox/`. **In-flight effects**: `operation` records without `completed`/`abandoned` (transitions.py:295-310). The PR mirror comment (cli.py:742-746) is not write-ahead [inference: a crash between the REVIEW_RESULT publish and the mirror leaves an unrecorded gap] |
| 2. Export ledger, event history, config, candidates; record marker; revoke authority; disable triggers | **Ledger**: the whole `<git-common-dir>/weave-workflow/` directory on the coordinator host, including `runs/` packets, review artefacts and verify logs. **Event history**: all `[weave-agent]` comments with `<!-- weave-agent:event:v1 -->` envelopes on issues, epics and PR mirrors, plus maintainer `/weave-decision` comments. **Configuration**: `policy.json`, `docmap.json`, `schemas/`, `.claude/settings.json`, `.claude/skills/**`, `.claude/agents/**`. **Candidates**: `agent/<N>-<slug>` branches (local and pushed), `.worktrees/*`, local-only preserved branches (e.g. `agent/6-…-a1`, I6:6503275585), `checkpoint.json`. **Triggers to disable**: Claude Code hooks in `.claude/settings.json`; the `weave-project` skill; the Projects "item closed → Done" automation | **Cutover marker**: no concept exists in Weave. **Revoking publication authority**: the legacy controller posts as the maintainer's personal account (policy.json:17-24), so revoking that credential would revoke the human too. [inference] Fencing must come from removing or disabling the tooling and from the new reducer refusing `weave-agent` envelopes after the marker, not from token revocation alone. **Exporting history**: without the local ledger, exported comments cannot be authenticated by Weave's own rule (events.py:129-135), so the ledger export is load-bearing |
| 3. Import open tasks, candidates, questions, resource holds, review history | **Open tasks**: issues on the board not Done, plus the held-claim set. **Candidate refs**: `head_sha`/`base_sha` in IMPLEMENTATION_READY, VERIFICATION_RESULT, REVIEW_REQUESTED and REVIEW_RESULT events, plus the packet `branch`/`worktree`. **Questions**: QUESTION/ANSWER events linked by `correlation_id`/`causation_id`; BLOCKED with `blocker` in {decision, maintainer-action}; the `agent:needs-human` label. **Resource holds**: `allowed_paths` in local packet files (cli.py:214-222) and the `**` default. **Review history**: REVIEW_REQUESTED, REVIEW_RESULT, CHANGES_REQUESTED and FINDING_DISPOSITION across all attempts | **No question IDs**, open/closed state or designated human. "Unresolved" must be inferred from a QUESTION without an ANSWER caused by it. Maintainer answers can arrive as orchestrator-relayed ANSWER text, not `/weave-decision` (I6:6502491358, "given to the orchestrator in conversation"). **Review counts**: Weave counts REQUESTED rounds per attempt, outages included, with a budget of 5. Remora counts completed PASS/CHANGES_REQUESTED rounds task-wide with a default of 3 (R:…plan.md:246). Imported counts must be recomputed from REVIEW_RESULT verdicts across attempts; a REQUESTED event without a RESULT is ambiguous (outage vs. lost). **Resource holds** are not on GitHub (DELEGATED carries only `packet_digest`) |
| 4. New epoch; invalidate legacy claims; validate mappings, readiness, counts, evidence mode; dry-run diff; authorized acceptance | **Legacy claims to invalidate**: every CLAIMED without a later RELEASED/COMPLETED. **Dependency sources** to map: native blocked-by, the `## Depends on` body section, `policy.json` dependencies, epic "Work items" order and milestone `requires` (scheduler.py:44-94) | **Evidence mode**: Weave has no `unverified_pilot`/`trusted_ci` concept. Its VERIFICATION_RESULT is coordinator-run and its Done gate uses PR status checks. [inference] Every historical completion is closest to "supplied plus CI status at merge" and needs an explicit evidence-mode label on import. **Task revision**: only a body-section digest (model.py:151-160), with no approved immutable revision. **Claim generation**: none to invalidate; `attempt` is the closest analogue |
| 5. Start new supervisors (`trusted_ci`); reject late legacy events; rollback path | Late legacy writers: any session still running `python3 -m tools.weave_workflow … --apply`, `reconcile --apply` replaying `outbox/`, or project automation | [inference] Rollback "into an explicit compatible legacy state" means writing Weave events that the old authenticator accepts. That requires appending matching `delivery` records to the legacy local ledger (events.py:129-135), which is outside the new controller's normal authority. The reverse mapping may be unsafe, and the plan already allows remaining paused (R:…plan.md:406) |

### D2. Cutover assumptions that Weave does not actually record [observed absence; searched schema kinds and `tools/weave_workflow/*.py`]

1. **Claim generation / authority epoch**: absent (C2).
2. **Lease renewal and heartbeat records**: absent. `heartbeat_expired` is unused.
3. **Stop requests and stop confirmations**: absent. There is no stop kind and no
   process-termination evidence; `run stop` only edits local files.
4. **Durable command IDs and receipts** for human commands: absent. The only identifier is
   the GitHub comment ID of a `/weave-decision`.
5. **Question IDs, designated human, superseded-question handling**: absent.
6. **Evidence mode, per-check `independently_executed`, executor identity, environment
   digest**: absent.
7. **Task-wide completed-round count**: not recorded. Only per-attempt REQUESTED counts are
   derivable.
8. **Hard-resource reservations** distinct from path globs: absent.
9. **Cross-host-verifiable provenance**: event authenticity depends on one host's local
   ledger.
10. **Cutover marker / epoch**: absent.

### D3. Stays with Weave (the language) vs moves to Remora [inference from paths and responsibilities]

- **Stays (Weave the language/project):**
  - `inventory-proof/`, `agent-kit/`, `specification/`, `evidence/`, `docs/decisions/`,
    `STABILITY.md`, the Rust ADR direction (W:docs/development/implementation-language.md);
  - Weave's project-specific configuration: milestone/epic map, issue-number special cases,
    decision tasks, protected paths, integration check names (`policy.json`);
  - `docmap.json`;
  - `derive_checks` component rules (cli.py:182-211);
  - the Weave-specific prompts in `.claude/agents/*` and `review.py:25-45`.
- **Candidate to move to Remora** (as generic Python, after adaptation):
  - envelope/schema validation;
  - criterion and requirement digests;
  - graph, readiness and selection logic;
  - pure gate functions;
  - integration-evidence derivation;
  - the review adapter and acceptance binding;
  - the docs-audit engine, separated from Weave's docmap;
  - reconciliation concepts.
- **Replaced by the selected backend** (gh-aw or narrow adapter), not moved:
  - the local ledger as authority;
  - the coordinator `flock`;
  - comment-envelope authentication against the local ledger;
  - board-status writes as part of the transition commit path.

---

## E. Reuse inventory classification

These classifications are judgements [inference]. They depend on P02a outcomes I did not
test. Line counts are observed: file-level SLOC from section B; sub-ranges use the same SLOC
method (`research-scripts/weave_range_sloc.py`).

| Module / range | Total / SLOC | Classification | Rationale |
| --- | --- | --- | --- |
| `schema.py` | 117 / 96 | reuse as-is (Python) | Generic fail-closed validator for a JSON-Schema subset. No Weave coupling observed |
| `model.py` digests and criteria (137-160) and dataclasses | 197 / 148 | reuse with adapter | `acceptance_criteria` and `requirements_digest` are reusable. Section names and the `M<n>` milestone key are Weave conventions (model.py:11-18, 151-160). The snapshot model is GitHub-shaped |
| `scheduler.py` | 427 / 345 | reuse with adapter | Deterministic graph and selection logic. Inputs are GitHub board/issue state and Weave policy keys (`epic`, `early_start_exceptions`). Completion must come from accepted state, not closed+Done. Path overlap (213-270, SLOC 42) is reusable as-is |
| `transitions.py` gates (1-207) | 207 / 174 | reuse with adapter | Pure gates over events. Need claim generation, a task-wide budget, UNVERIFIED and evidence-mode inputs |
| `transitions.py` executor (208-323) | 116 / 106 | removable if gh-aw adopted | Board write intent/read-back/recovery is projection publication. Under a narrow adapter it becomes a projection-reconciler (reuse with adapter). gh-aw coverage is **unverified here** |
| `review.py` | 177 / 144 | reuse with adapter | Codex `exec` adapter plus strict acceptance binding. Must add UNVERIFIED, per-check provenance and review-job ownership. The prompt is Weave-specific |
| `integration.py` | 82 / 60 | reuse with adapter | Strong derived-evidence Done check. Policy-coupled; uses local `git` |
| `events.py` build/validate/render/redact (1-109) | 109 / 79 | reuse with adapter | Envelope and redaction are reusable. The kinds need generation, stop and command fields |
| `events.py` authenticate/decision (110-152) | 43 / 34 | removable if narrow adapter | Trust rests on local-ledger delivery records. Shared state replaces this under the narrow adapter, or gh-aw's model if adopted. Command parsing needs IDs |
| `events.py` ordering (153-174) | 22 / 18 | reuse as-is (Python) | Generic causal ordering |
| `publisher.py` | 139 / 106 | removable if gh-aw adopted | Write-ahead comment publication with ambiguous-write lookup. If gh-aw safe outputs are adopted, this may be removable (**unverified**). Under the narrow adapter it maps to pending external effects (reuse with adapter) |
| `state.py` | 221 / 168 | removable if gh-aw adopted | Local ledger, outbox and `flock` are exactly the single-host authority Remora replaces. Also replaced under the narrow adapter by Git-state CAS. Not reusable as authority |
| `reconcile.py` | 140 / 121 | reuse with adapter | Discrepancy classification is useful. It reads the local ledger, `git worktree list` and board state |
| `github.py` reads (1-275) | 275 / 232 | reuse with adapter | Paginated, completeness-checked reads. User-owned projects only (github.py:66) |
| `github.py` writes (276-311) | 36 / 28 | removable if gh-aw adopted | Comment, Status and label writes. If gh-aw safe outputs cover them, removable (**unverified**) |
| `github.py` `FakeGitHub` (312-390) | 79 / 65 | reuse with adapter | Test double living in production code. Useful for Remora fixtures |
| `cli.py` | 897 / 785 | reuse with adapter (split) | Sub-ranges listed below |
| `docs_audit.py` | 706 / 580 | reuse with adapter | Documentation-impact engine. Hard-codes Weave components (docs_audit.py:251-253) and `weave.py` command discovery (331-335). It also executes code from the audited tree (unit-test discovery imports, `command-regex`/`command` checks: docs_audit.py:408-438, 482-491) |
| `docmap.json` | 442 / n/a | Weave-specific, stays | Content is Weave's documentation |
| `policy.json` | 271 / n/a | Weave-specific, stays | Values are Weave's. The structure informs a Remora policy schema |
| `hooks.py` + `.claude/hooks/weave_hook.py` + `.claude/settings.json` | 266+9+45 / 222+5 | unknown | Claude-session guards. Weave states they are not a security boundary (hooks.md:34-35). Their fate depends on the P02b runtime choice |
| `capabilities.py` | 68 / 60 | reuse with adapter | Seed for a `doctor` command. Tool list is Weave-specific |
| `report.py` | 122 / 114 | reuse with adapter | Dry-run report. Depends on `cli`/`reconcile`; untested |
| `schemas/*.json` | 1,122 lines | reuse with adapter | Strict schemas. Need generation, UNVERIFIED, evidence provenance and command IDs |
| `.claude/skills/**`, `.claude/agents/**` | 343 lines | Weave-specific, stays | Orchestration instructions for one Claude session |
| `tests/**` | 2,327 / 1,930, 163 methods | reuse with adapter | Retain as behavioural fixtures. Many tests encode per-attempt budgets and single-host assumptions that Remora rejects (e.g. test_transitions.py:143-160) |

`cli.py` sub-ranges (SLOC):

| Range | SLOC | Content |
| --- | ---: | --- |
| 1-79 | 50 | Helpers including held/active claims |
| 80-131 | 47 | `capabilities`, `discover`, `plan` |
| 132-343 | 184 | Packet and claim. `derive_checks` (182-211, 29) is Weave-specific |
| 344-451 | 89 | Relay and new-event |
| 452-491 | 37 | `verify` |
| 492-526 | 32 | `milestone-gate` |
| 527-578 | 46 | `transition`, `reconcile`, `outbox` |
| 579-651 | 66 | `docs-audit`, `docs-map` |
| 652-755 | 101 | `review` |
| 756-797 | 35 | `report`, `run`, `hook` |
| 798-897 | 98 | Argument parser |

**Inputs for P02a criterion 3 (not a computed result)** [inference]:

- Production Python that plausibly counts as "coordination/publication" in Weave adds up to
  610 SLOC:
  - `state.py` 168;
  - `publisher.py` 106;
  - `transitions.py` executor 106;
  - `github.py` writes 28;
  - `events.py` authenticate 34;
  - the claim/transition/outbox/run wiring in `cli.py`, roughly 132-343 + 527-578 + 756-797
    = 184 + 46 + 35 = 265, which also contains packet building, so it is an upper bound.
- With `reconcile.py` (121) included, the figure is up to ~731 SLOC.
- That is an **upper bound** for what a backend could remove. The tests that exercise this
  code are mainly `test_protocol.py` (16 methods) and parts of `test_review_findings.py` and
  `test_transitions.py`.
- Any net-reduction claim must subtract the new adapter/glue SLOC. It must not count
  `scheduler.py`, gates, `review.py`, `integration.py` or `docs_audit.py`, which remain
  under either backend.

---

## F. Contract-to-code leads (R:…plan.md:62-73)

| # | Contract | Weave code today (observed) | Completeness | Gap |
| --- | --- | --- | --- | --- |
| 1 | One accepted dev owner and one review owner at a time | `flock` lock (state.py:194-214). One held claim per issue in the local ledger (cli.py:67-74; scheduler.py:341-348). Selection re-run under the lock (cli.py:298-304) | Single host only, by Weave's own statement (github-adapter.md:41-49). No review-owner concept: review is a synchronous child process of the coordinator (cli.py:715-723) | Atomic cross-host ownership; review-job claims |
| 2 | Claimable only with accepted prerequisite completion and resources available | Blocking edges from three sources. Prerequisite = closed-as-completed **and** board Done (scheduler.py:401-412). Milestone gates need GATE_EVALUATED (scheduler.py:141-157). Path reservations (cli.py:225-255) | Partial: completion is read from GitHub issue and board state, which manual moves or automation can change (transitions.md:55-71), not from the COMPLETED record. Resources are path globs only | Completion from authoritative accepted state; hard resources |
| 3 | Stale worker's submissions not accepted under an old claim generation | Review results bound to run_id, attempt and request_id (review.py:157-162). Relay checks sender role only (cli.py:388-401) | Partial for reviews; absent for other submissions. No generation (C2) | Claim generation, fencing on every accepted event |
| 4 | Review applies to exact candidate and task revision | head/base/requirements-digest binding (review.py:157-168). Done gate requires the latest result for this head, not superseded (transitions.py:160-176). Tree equality (integration.py:72-81) | Strong for the candidate. "Task revision" is a digest of selected issue-body sections (model.py:151-160), not an approved immutable revision | Approved revision object; packet digest binding in review |
| 5 | Budget belongs to the task across workers, restarts, branches and amendments | Per-attempt REQUESTED count (transitions.py:177-180; reconcile.py:21-22); budget 5 | **Contradicts the contract**: rounds reset when an attempt is released, and tests assert this (test_transitions.py:152-155). Issue #6 released an attempt to widen scope (I6:6503275585) | Task-wide completed-round counter, scope amendment without new attempt |
| 6 | Timeout, unavailable checker or unverified test cannot become PASS | Codex timeout, exit, silence or prose → BLOCKED, not a verdict (review.py:107-128; cli.py:729-734). Inconsistent PASS rejected (review.py:174-175). Done needs VERIFICATION_RESULT PASS (transitions.py:193-194) | Partial: a reviewer that could not run checks can still PASS (review.md:66-68; I6:6503850141). Verification is coordinator-run, not trusted CI; no UNVERIFIED verdict | UNVERIFIED outcome; per-check provenance; trusted-CI gating |
| 7 | Done = integrated deliverable + accepted completion evidence | Derived integration evidence (integration.py:44-82) and Done gate (transitions.py:150-206). Decision tasks need `/weave-decision` (transitions.py:153-156) | Strong for code tasks, single host | Shared-state completion record; non-code deliverable location |
| 8 | Human commands authenticated, correlated and auditable; discussion never changes policy | `/weave-decision` recognition (events.py:139-150). Coordinator cannot post the prefix (events.py:76-77) | Weak: no command ID, deduplication or question correlation. The coordinator and maintainer share one account (policy.json:17-24). Issue #6 maintainer answers were relayed from conversation as ANSWER events (I6:6502491358). Orchestrator ANSWERs also made scope choices (I6:6503302506) | Command IDs, receipts, correlation, distinct identities |
| 9 | Board and summaries are recoverable projections, not locks | `reconcile` reports board/ledger mismatches as conflicts (reconcile.py:91-101). Labels documented as not locks | Partial: the board is also an eligibility, capacity and completion **input** (scheduler.py:193-197, 386-393, 410). Project automation can move cards (capabilities.md:34) | Derive eligibility only from authoritative state |
| 10 | No model process gets merge authority or unrestricted controller credentials | Worker shells credential-scrubbed by hook (hooks.py:19-21, 93-98). Codex reviewer env scrubbed (review.py:22-23, 104-106). `merge.delegated_to_coordinator: false` (policy.json:233-236) | Weak: the orchestrator is itself a model session holding the maintainer's `repo`+`project` token. `gh pr merge` is "ask", not deny (hooks.py:26-27; settings.json:8-11). Subagents share process, user and keyring (roles.md:46-49). `verify` and `docs-audit` execute candidate-tree code in the coordinator environment (cli.py:475-477; docs_audit.py:408-421, 489-491) | Credential-holding supervisor outside model processes; no candidate execution with publication credentials |

---

## G. Issue #6 leads (R:…plan.md:39, S2 at plan.md:479)

**Fetch** [observed]: `GET https://api.github.com/repos/quaat/weave/issues/6` and
`/issues/6/comments?per_page=100`, both HTTP 200, at 2026-10-29T23:19:28Z. Saved under
`/tmp/claude-1000/upstream/weave-issue6/`. The issue is titled "Machine-readable diagnostics
with stable rule IDs and source spans", closed as completed at 2026-10-29T17:35:42Z, with 58
comments. All 58 comments are `[weave-agent]` envelopes posted by `quaat`, and none was
edited. There is no `/weave-decision` comment on the issue.

All three comments cited by S2 exist:

- `6503275585` is RELEASED (attempt 1): "released to widen the allowed paths; the committed
  work (head bb15c5d) is carried into attempt 2 unchanged". It was preceded by an
  implementer BLOCKED (`6503275151`) saying the needed files were outside `allowed_paths`.
- `6503850141` is REVIEW_RESULT, attempt 2, round 3, PASS, `codex-cli 0.162.1`, with this
  reviewer limitation: "This review sandbox has no writable temporary directory, so the full
  local test command and docs audit could not complete here. The packet records those
  checks passing at the reviewed head."
  - Rounds 1 and 2 were REQUEST_CHANGES (`6503587418`, `6503711980`), each followed by
    CHANGES_REQUESTED.
  - "Third review passed after two change requests" is **verified**.
- `6502491358` is an ANSWER from the orchestrator: "Maintainer answers, given to the
  orchestrator in conversation on 29 October 2026: (1) Refresh the snapshots once. … (2)
  Adopt all four … (3) For #8: relabel at the kit and envelope layer …".

**The three requirements** (R:…plan.md:39) are **not stated as requirements in issue #6**.
The issue body only asks for diagnostics features (AC list in the body). They are the plan
author's derivation from this history. Each underlying event is observed:

1. *Amend scope without discarding an attempt*: scope was widened by RELEASE and a new
   claim (attempt 2). That reset the per-attempt budget basis (C3), though no rounds had yet
   been used in attempt 1.
2. *Distinguish independently run checks from developer-supplied evidence*: the round-3
   PASS relied on "packet records" of checks that the reviewer could not rerun.
3. *Preserve nuanced human conversations as durable decisions*: maintainer decisions
   entered as orchestrator-authored ANSWER text, not as `/weave-decision` comments. The
   attempt-2 ANSWER (`6503302506`) also contains orchestrator-made choices (version bumps,
   the prototype staying at v3).

The derivation is a reasonable [inference] from the observed events, but it is not a quote
from the issue.

---

## H. Unknowns and blockers

- **Test runs.** The "89 passing focused controller tests" (R:…plan.md:33) were **not
  rerun** here (no Weave code was executed).
  - Static count at both revisions is 163 `test*` methods in `tools/weave_workflow/tests/`,
    with 10 `subTest` uses. I could not reproduce "89" from any subset of the test files.
    Which subset the earlier assessment counted is **unknown**.
  - Executed pass/fail status at either SHA is **unverified**.
- **Weave docs that are stale or conflict with each other** [observed]:
  - `capabilities.md:38` says no end-to-end run has been performed (observed 2026-10-28),
    yet issue #6 shows a complete claim → review → Done run on 2026-10-29.
  - `orchestration-requirements.md:265` asks for heartbeat in issue events; no heartbeat
    is implemented.
- **gh-aw coverage.** Whether gh-aw safe outputs or the queue could replace `publisher.py`,
  `state.py`, the transition executor and `github.py` writes is **unverified** here. That is
  another P01 sub-scope. The "removable if gh-aw adopted" labels mean "the responsibility
  is of the kind gh-aw claims to cover", nothing more.
- **Project automation.** The live GitHub Projects automation settings for quaat/weave
  Project #3 are **unverified**: not readable via the API, according to Weave's own
  `capabilities.md:34`. I did not query Projects.
- **Legacy ledger contents.** The actual contents and size of the legacy local ledger on
  host `gengar` are **unknown**. It is not in GitHub. This directly affects cutover step 2
  feasibility.
- **Licence.** The legal effect of AI co-authorship trailers on the controller files is not
  assessed. Identity of Weave rights holder vs. Remora owner is unverified.
- **Shallow clones.** Both checkouts are `--depth 1`, so per-file history and authorship
  were taken from Weave's own decision record, not from `git log`.
- **No blocker** prevented completing this inventory.
