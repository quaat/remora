# P01 research: upstream coordination surfaces (gh-aw, Symphony, Beads)

Task: P01, Reuse and authority decision. Sub-scope: upstream coordination surfaces.
Status: research evidence for the P01 owner. **This document makes no reuse,
backend or go/no-go decision.** P02a rejection-criterion material is labelled
"lead".

## 0. Method, pins and evidence labels

| Upstream | Repository | Commit inspected | Fetched (UTC) | Default-branch head at fetch | Nearest tag |
| --- | --- | --- | --- | --- | --- |
| gh-aw | `https://github.com/githubnext/gh-aw` (resolves to the same SHA as `github/gh-aw`) | `28f2101d8af447fdb90ffd70dd2579e4ad64a21c` (2026-10-29T14:07:49-07:00) | 2026-10-29T23:16:42Z | same SHA | `v1.0.1` (`0627fdbe…`), ancestor, 43 commits before the pin |
| Symphony | `https://github.com/openai/symphony` | `be10a1b79df723d6d7612b5651c8522704dafb2e` (2026-09-15) | 2026-10-29T23:16:42Z | same SHA | `v0.0.3` (`1c0fb6c8…`), ancestor, 1 commit before the pin; the moving `nightly` tag points at the pin |
| Beads | `https://github.com/gastownhall/beads` | `e226083653b893998614df4225f73b6688ca9166` (2026-10-29) | 2026-10-29T23:16:42Z | same SHA | `v1.3.2` (`9b65b9e1…`) is **not** an ancestor. It is a release-branch merge, forward-ported to main by `02f3349b99429628895e8ff520adcaf5cb0fc29a` |

Method: each repository was cloned under `/tmp/claude-1000/upstream/<name>` with
`git init` + `git fetch --depth 1 origin <sha>` + `git checkout -q FETCH_HEAD`. Tag
ancestry came from `git ls-remote --tags` and one bounded treeless fetch per
repository (`--filter=tree:0 --shallow-since=<tag date>`). No upstream build tool,
test, hook or interpreter was run. Inspection used `cat`, `sed`, `grep`, `git`, and
two `python3.12 -I` scripts kept in `/tmp/claude-1000/research-scripts/`. Machine-readable
pins are in `pins-upstream.json`.

Citations use `<repo>:<path>:<lines>` at the pinned commit. For example,
`gh-aw:pkg/workqueue/branch.go:357-391` means that path in the gh-aw checkout above.
Labels used below:

- **[O] observed**: read in code or files at the pin.
- **[D] documented**: stated in upstream documentation or specs but not exercised here.
- **[I] inference**: my reasoning from O/D evidence. Treat it as unverified.

All three default branches equalled the plan's revision-3 pins at fetch time
(`git ls-remote --symref … HEAD`, 2026-10-29T23:17Z). The plan's snapshots are
therefore still current heads, but they are not release tags.

### Documentation reachability (fetched 2026-10-29T23:18:32Z, `curl -L`)

| URL | HTTP | Pinned in-repo copy | Divergence check |
| --- | --- | --- | --- |
| https://github.github.com/gh-aw/introduction/overview/ | 200 | `gh-aw:docs/src/content/docs/introduction/overview.mdx` | Crude 60-char fragment overlap 11/14. Misses are list/markup formatting [O] |
| https://github.github.com/gh-aw/introduction/architecture/ | 200 | `…/introduction/architecture.mdx` | 64/128. MDX imports and diagram components are not rendered as text [O]. Not reviewed line by line |
| https://github.github.com/gh-aw/reference/custom-safe-outputs/ | 200 | `…/reference/custom-safe-outputs.md` | 78/109. Misses are mostly table rows [O] |
| https://github.github.com/gh-aw/specs/work-queue-specification/ | 200 | `…/specs/work-queue-specification.md` | 1650/2152. Live page shows the same research commit `81891f23…` and the same §9.1 rows ("Worker-evolution runtime…", "Trusted AW settings…", "Main at `303b402810`…") [O]. No content divergence found in those spot checks. The site's build commit is not exposed |
| https://github.github.com/gh-aw/specs/repo-memory-ledger-specification/ | 200 | `…/specs/repo-memory-ledger-specification.md` | 162/186. Live page shows Version 1.1, Working Draft, as pinned [O] |
| https://github.com/openai/symphony/blob/main/SPEC.md | 200 | `symphony:SPEC.md` | `main` equalled the pin at fetch time, so the revision is identical. Text overlap is not meaningful for GitHub's blob HTML |

The overlap metric is only a smoke check, not a diff. Treat the pinned in-repo
copies as the cited source.

---

## 1. gh-aw

### 1.1 Pin, license, versioning and runtime dependencies

- **License [O]:** `gh-aw:LICENSE`, MIT text, "Copyright GitHub, Inc.", sha256
  `2510b446bc1f0cf9702453075d20cd88631e20e5642658edb7325d9c1eb534f7`. The SPDX
  identifier `MIT` is inferred from the text and is not declared in the file. No
  top-level NOTICE file was found (`ls gh-aw | grep -i notice`, empty).
- **Repository identity [O]:** `go.mod:1` declares `module github.com/github/gh-aw`.
  `git ls-remote` returned the same HEAD SHA for `githubnext/gh-aw` and
  `github/gh-aw`. The README installs with `gh extension install github/gh-aw`
  (`gh-aw:README.md`, Quick Start). Inference: the plan's `githubnext` URL is an alias
  or redirect. Record `github/gh-aw` as canonical.
- **Release tags [O]:** 560 tag refs via `git ls-remote --tags`. The highest are
  `v1.0.0` (commit 2026-10-26) and `v1.0.1` (2026-10-27). Both are ancestors of the
  pin, and 101 commits landed on main from 2026-10-26 to the pin. **[D]** Cadence:
  "weekly or bi-weekly minor release". "Version numbers increment on a time cadence,
  not on the scope of changes" (`gh-aw:docs/src/content/docs/reference/releases.md:10-21`).
  Channels are `latest` or a pinned `vMAJOR.MINOR.PATCH`
  (`releases.md:23-29`). Blocked versions exist
  (`gh-aw:.github/aw/compat.json`, `blockedVersions` v0.82.8–v0.85.3).
- **How compiled workflows pin actions [O/D]:** `gh aw compile` emits `.lock.yml`
  with SHA-pinned `uses:` references, cached in `.github/aw/actions-lock.json`
  (`releases.md:135-156`). The compiler has dev/release/script/action modes. In
  release mode the setup action is `github/gh-aw/actions/setup@<sha> # <version>`,
  or `github/gh-aw-actions/setup@<sha>` in action mode
  (`gh-aw:pkg/workflow/action_mode.go:17-27`, `pkg/workflow/action_reference.go:33-36`).
  Example: `gh-aw:.github/workflows/smoke-work-queue-worker.lock.yml:123,171`
  pins `actions/checkout@3d3c42e5…` and `actions/github-script@3a2844b7…`.
- **Runtime version enforcement that is not pinned [O]:** the activation job fetches
  `https://raw.githubusercontent.com/github/gh-aw-actions/main/.github/aw/compat.json`
  and fails the activation job when the compiled version is blocked or below
  minimum. If the download fails, the check is skipped
  (`gh-aw:actions/setup/js/check_version_updates.cjs:9-16,29`; documented at
  `releases.md:70-88`). A pinned workflow can therefore be disabled by a moving
  remote file.
- **Schema versioning [O]:**
  - Queue schemas are JSON Schema 2020-12 files under `gh-aw:pkg/workqueue/schema/`
    (48 files, for example `QueueCommit.json`, `WorkQueueAssignment.json`,
    `WorkQueueFinishIntent.json`), generated from `specs/work-queue/transactions.tsp`.
  - The envelope carries `"version": {"const": 3}` (`QueueCommit.json`;
    `WorkQueueAssignment.json:79-81`). `$id` values are bare file names
    (`"QueueCommit.json"`), not resolvable URLs.
  - **[D]** Version 3 grows additively without a version bump: "Upgrade all
    closed-schema readers and runtimes before using newer version-3 fields or evidence
    records" (`gh-aw:docs/src/content/docs/reference/work-queue.md:374-376`).
  - The safe-outputs spec is "Version 1.29.13, Status: Working Draft … Future
    versions may introduce backwards-incompatible changes"
    (`gh-aw:docs/src/content/docs/specs/safe-outputs-specification.md:10-11,25`).
  - The ledger spec is "Version 1.1, Status: Working Draft"
    (`…/specs/repo-memory-ledger-specification.md:10-11`).
  - The work-queue spec says "specification with implementation in progress"
    (`…/specs/work-queue-specification.md:188`).
  - **[O]** `git diff --quiet v1.0.0 <pin>` over the work-queue spec,
    `pkg/workqueue/schema` and `transactions.tsp` exits 0, so these files are unchanged
    since v1.0.0. Between v1.0.1 and the pin, `pkg/workqueue`, `actions/setup/js` and
    the reference doc changed: 49 files, +2322/−299.
- **Runtime dependencies a consumer needs [O/D]:**
  - The `gh` CLI plus the `gh-aw` extension, which compiles Markdown into Actions
    workflows (`overview.mdx:46-48`).
  - GitHub Actions to execute everything. The setup action is `using: 'node24'`
    (`gh-aw:actions/setup/action.yml:40-41`).
  - The extension is written in Go (`go 1.27.3`, `go.mod:3`). Consumers install a
    released binary, so no Go toolchain is needed [D, README].
  - Queue operation requires a GitHub REST dispatch contract pinned to API version
    `2026-03-10` (`work-queue-specification.md:1248-1255`).
  - An AI engine secret (`COPILOT_GITHUB_TOKEN`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
    and others) (`gh-aw:docs/src/content/docs/reference/auth.mdx:19-50,102-200`).

### 1.2 Work queue

**Location [O]:**
- Spec: `gh-aw:docs/src/content/docs/specs/work-queue-specification.md`, 3494 lines,
  with "Research date: 2026-10-05" and "Repository examined … commit `81891f23…`" at
  :184-186.
- Operator/reference doc: `…/reference/work-queue.md`.
- Formal models: `gh-aw:specs/work-queue/` (TLA+, `transactions.tsp`, fixtures,
  `verification-2026-10-07*.json`).
- Go engine: `gh-aw:pkg/workqueue/` (39 non-test files, 12,234 lines by `wc -l`).
- JS runtime: `gh-aw:actions/setup/js/*work_queue*.cjs` (103 non-`.test.cjs` files,
  34,670 lines, including 27 `*_checks.cjs` modules).
- Compiler: `gh-aw:pkg/workflow/*work_queue*.go` (2,618 non-test lines).
- Operator CLI: `gh-aw:pkg/cli/work_command*.go`.

**Storage and data layout [D/O]:**
- There is one canonical `work-queue.jsonl` transaction log on a Git branch, default
  `work-queue`. Each line is one `QueueCommit` envelope with fields `version`, `id`,
  `previous`, `request`, `actor`, `policy_epoch`, `at`, `operations` and `trace`
  (`work-queue-specification.md:871-921`).
- "No separate scheduling log, authoritative outbox, database, cursor file, manifest,
  or state sidecar" (:198).
- Issues can mirror the queue but cannot store it, and there is no `storage` option
  (`reference/work-queue.md:6`; spec :3253, "Git-only storage"). The operator CLI
  rejects non-git storage (`pkg/cli/work_command.go:46-48`).
- Record kinds: Work, Claim, Policy, Deployment, Reservation, Completion, Result,
  Release (`reference/work-queue.md:20-29`).
- Ledger reads and publication must use Git objects/refs with complete ancestry. A
  shallow fetch must not substitute (spec :875-883).

**Concurrency and atomicity mechanism [O]:**
- Publication is a linear fast-forward commit pushed with
  `git push --porcelain --no-verify --recurse-submodules=no --force-with-lease=<ref>:<observed head>`.
  Rejections map to a CAS conflict (`gh-aw:pkg/workqueue/branch_git.go:525-563`, push
  at :545-546).
- The JS transport is equivalent: `push --force-with-lease=${ref}:${expected}`
  (`gh-aw:actions/setup/js/work_queue_git_transport.cjs:217`).
- **[D]** On conflict the scheduler discards its tentative selection and recomputes.
  On an uncertain response it looks for the stable request ID
  (`work-queue-specification.md:1041-1101`). "Two dispatchers proposing against the
  same branch version cannot both publish their candidates" (:1070).
- **[D]** "Live Git/network contention remains unverified" (:3301).

**Supported operations [D/O]:**

| Operation | Surface | Evidence |
| --- | --- | --- |
| Submit Work / graph | Agent intent `work_queue_submit` (staged, processed by trusted safe outputs). Operator `submit-work`, `submit-graph` | spec :1594-1606; `reference/work-queue.md:98-105,232-233` |
| Claim (grant) | Scheduler-selected only, via `work_queue_dispatch_next` or operator `dispatch-next`. "Direct claim and operator finish are unsupported" | spec :1338-1384; `pkg/cli/work_command.go:35-39,581-610` |
| Finish (complete/cancel) | `work_queue_claim_finish`, staged by the originally bound worker only. `keep_open` re-queues after verified delivery | `reference/work-queue.md:103,109-112`; `pkg/cli/work_command.go:39` |
| Release | Only on verified worker quiescence (conclusion job), exact native termination, or definitive nonlaunch. "No administrative force-release" | spec :1140-1336 (state table :1292-1300); `reference/work-queue.md:114,119` |
| Renew / lease | **Absent.** "There is no background timer or Claim lease" | `reference/work-queue.md:137`; spec :1332-1333 |
| Dependency gating | Work/Issue/PR DAG. Work needs predecessor **Results** (independently verified delivery). Issue deps need completion evidence; PR deps need merge evidence | `reference/work-queue.md:111-113`; spec §7.15–7.16 (:2136-2562) |
| Recovery | Stable request IDs; uncertain launch is retained, never resent; maintenance reconciliation with `actions: read`, `contents: write` | spec :1214-1290, :1217 |
| Checkpoint / compaction | Version-3 checkpoint root QueueCommit with `prior_git_sha` and digest verification; operator `compact` | spec :873-886; `reference/work-queue.md:244`; `pkg/workqueue/checkpoint.go` |
| Operator controls | `control` (pause/resume, credential rotation), `cancel-work`, `cancel-claim`, `reprioritize`, `clear [--hard]`, `reconcile`, `evidence`, `policy`, `deploy` | `reference/work-queue.md:222-246` |

**Implementation-coverage statements (spec §9.1, :3273-3340) [D]:**
- "This table is a release checklist, not a claim that the whole specification is
  already implemented or proved … A green ordinary CI run does not discharge an
  unexecuted formal, supported-host, performance, or deployment-security gate"
  (:3292-3295).
- Rows marked implemented carry live caveats:
  - "Live Git/network contention remains unverified" (:3301).
  - "hosted immutable-SHA dispatch compatibility remains a separate gate".
  - "Hosted Git publication and immutable-SHA dispatch remain unverified live gates" (:3319).
  - "Hosted execution remains unverified" (:3321).
  - "full runtime/host refinement remains unverified".
- "Authenticated ingestion, actual run/attempt binding, Claim/resource checks and
  credentials withheld from agent execution remain required" (:3323).
- §10 lists open items (:3342-3360). Among them:
  - Freshness/ref semantics must be validated under actual concurrent publication.
  - "Staged intents cannot return durable grants to the agent in the same turn under
    the current job topology; a live acquire-response design would be a different
    execution boundary" (:3352).
- Repository-writer caveat: writers can alter or delete the queue branch, and a deleted
  branch is a fresh queue (`reference/work-queue.md:33-34`). "No scheduling or replay
  guarantee covers raw writes by other repository writers" (spec :1113-1115).

### 1.3 Safe outputs

- **Pattern [D]:** the agent job runs read-only. Writes are buffered as NDJSON
  intents and applied by separate trusted jobs with scoped permissions. A threat
  detection job sits in between (`gh-aw:docs/src/content/docs/introduction/architecture.mdx:67,145,363`;
  safe-outputs spec §3-4).
- **Types [O]:** 44 built-in types map to handler functions in
  `gh-aw:actions/setup/js/safe_outputs_handlers.cjs`
  (`safe-outputs-specification.md:2402-2452`). Type definitions start at §7.1 (:2462).
  - Issues, comments, PRs, reviews and labels.
  - Projects, releases, assets and artifacts.
  - `dispatch_workflow`, `create_check_run` and `create_agent_session`.
  - Reporting types (`noop`, `report_incomplete`, …).
  - Linear/Jira types.
  - Notably **`merge_pull_request`** ("Merge pull requests only when configured policy
    gates pass", :2422, :3736-3742) and `approve_workflow_run`.
- **Schemas [O]:**
  - MCP tool schemas live in `gh-aw:actions/setup/js/safe_outputs_tools.json`, with a
    copy in `pkg/workflow/js/safe_outputs_tools.json`.
  - Workflow frontmatter schema: `gh-aw:pkg/parser/schemas/main_workflow_schema.json`.
  - Agent output schema: `gh-aw:schemas/agent-output.json`.
  - The spec requires JSON Schema Draft 7 validation of every invocation (:5275-5279).
  - Schema changes must update the spec, the Go and JS handlers, and prompts in the
    same PR (:2378-2387).
  - Payloads are constructed only from declared fields (§7.0.3, :2454-2460).
- **Validation and authorization [D/O]:**
  - Per-type `max` counts, `target` / `target-repo` and `allowed-*` filters,
    sanitization, and `staged` preview (spec §5–6, §9).
  - When the queue is enabled, every safe-output message must resolve to exactly one
    assigned Claim before any handler runs. This is "enforced authorization, not a
    prompt convention" (`work-queue-specification.md:206-211`).
  - Effect authorization rejects non-worker actors
    (`gh-aw:actions/setup/js/work_queue_store.cjs:535`).
  - Execution guarantees are weak by design: batch operations are best-effort with
    partial success, and create operations are non-idempotent (spec :5571-5600).
- **Custom outputs [D]:** `safe-outputs.jobs` (custom Actions jobs),
  `safe-outputs.scripts` (inline handlers) and `safe-outputs.actions` (wrapped
  Actions) (`reference/custom-safe-outputs.md:13-70,466,542`).
- **Reusability outside Actions [O/I]:** handlers are `actions/github-script` modules.
  They depend on globals `core, github, context, exec, io, getOctokit` set by
  `setup_globals.cjs` (`gh-aw:actions/setup/js/setup_globals.cjs:35`). Worker identity
  comes from the Actions run context (§1.5). [I] Running these handlers outside Actions
  would mean shimming the github-script globals and the run context. No documented
  supported path for that was found (searched docs for "outside actions",
  "standalone", "external worker"). Reusing the *pattern* with a local schema would
  be an adaptation, per plan §4.

### 1.4 Git-backed ledger specification

- **Status [O]:** "Version 1.1, Status: Working Draft"
  (`…/specs/repo-memory-ledger-specification.md:10-11`). The live site matches.
- **Semantics [D]:**
  - Append-only canonical-JSON records with `sha` = SHA-256 of the record, UUIDv4 IDs,
    and parent hashes forming a DAG. Records are stored in JSONL shards on
    `ledgers/<name>` branches.
  - Disposable SQLite projections; deferred mutations through safe outputs; a trusted
    persistence job (§2-5, :44-224).
  - Job/trust split table at :61-79.
- **Guarantees [D]:**
  - "Concurrent writers MAY produce multiple DAG heads … The ledger provides
    integrity, boundedness, deterministic reconstruction, and best-effort convergence.
    It does **not** provide distributed locking, serializable transactions across
    branches" (:226-236).
  - "Records are integrity-checked but not authenticated" (:299-305).
  - Compaction is published as one commit "guarded by the expected branch head"
    (:174-208).
- **Verification requirements [D]:**
  - Persistence revalidates the transaction artifacts and canonical history.
  - Compaction plans are treated as hostile input and checked against the latest
    state.
  - A conformance test list is at :307-316.
- [I] This is separate from the work-queue protocol. It is not a task-lock mechanism.

### 1.5 External-worker binding (P02a criterion-1 lead)

**Question:** can a process outside GitHub Actions hold, renew and release a Claim
through an authenticated, supported interface, without a second ledger or a
fabricated Actions identity?

**Found [O/D]:**
1. **Worker authority comes from the Actions run.**
   - `authenticatePublisher` reads `context.runId` / `GITHUB_RUN_ID` and
     `GITHUB_RUN_ATTEMPT`, refuses worker reruns (`attempt !== 1` →
     `rerun_not_authorized`), and fetches the native run through the API
     (`gh-aw:actions/setup/js/work_queue_native.cjs:240-251`).
   - Worker finish and binding call it with `role: "worker"`
     (`actions/setup/js/finish_work_queue_claim.cjs:169`;
     `actions/setup/js/work_queue_binding.cjs:115`).
   - Spec: "Bind only the original native attempt, identified by
     `(run_id, run_attempt=1)`" (`work-queue-specification.md:1269-1272`).
   - Dispatch requires a `workflow_dispatch` run of an approved workflow at an
     immutable revision (:1248-1258).
2. **The operator CLI is the only non-Actions publisher, and it cannot act as a
   worker.**
   - `Branch.authenticate` accepts only `administrator`, `producer` or `reconciler`.
     It rejects others with "native operator publisher cannot impersonate workflow
     roles" (`gh-aw:pkg/workqueue/branch.go:357-391`, check at :362-363).
   - The operator identity comes from `GET /user` plus repository `push`/`admin`
     permissions (:365-390).
   - CLI help: "Direct claim and operator finish are unsupported … Only the
     originally bound worker may stage work_queue_claim_finish"
     (`pkg/cli/work_command.go:35-39`).
   - A test asserts that `claim`, `finish` and `force-release` subcommands do not
     exist (`pkg/cli/work_command_test.go:52-58`).
   - `dispatch-next` grants and reserves but "does not launch workflows"
     (`reference/work-queue.md:234`).
3. **No hold/renew primitive exists.** "There is no background timer or Claim lease"
   (`reference/work-queue.md:137`). Release requires native-run evidence
   (spec :1292-1300). "Arbitrary run-ID adoption" is unsupported
   (`reference/work-queue.md:380`).
4. **Authentication is out of protocol.** "Authentication is provided by AW, outside
   the work-queue protocol … It defines no authentication or enrollment mechanism"
   (spec :1105-1107).

**Searched without a supporting hit:**
- `grep -rniE "outside (github )?actions|external worker|external process|non-actions worker|local worker|self-hosted"`
  over the work-queue spec, the reference doc, `patterns/workqueue-ops.md`,
  `specs/work-queue/README.md` and ADRs 67322/71495: no matches.
- `grep -rniE "renew|heartbeat|lease"` over `pkg/workqueue/*.go` and the queue docs:
  the only hits are Git `--force-with-lease` and reservation "release".

**Lead (not a decision):**
- I found no supported path for a process outside Actions to hold or exercise a
  Claim. Worker authority depends on authenticating as the original Actions run, and
  the one non-Actions publisher is explicitly barred from the worker role.
- An external supervisor could only take part by (a) triggering an AW worker
  workflow that does the work inside Actions, or (b) writing Claims under a non-worker
  role or into a separate record. (b) is what criterion 1 forbids.
- Open question for P02a/human, not settled here: whether an AW worker running on a
  self-hosted runner the supervisor operates counts as "outside Actions". It would
  still be an Actions run with an Actions identity.

### 1.6 Required GitHub identities and permissions

| Purpose | Credential / permission | Evidence |
| --- | --- | --- |
| Default agent job | Read-only `permissions:`; the compiler adds `actions: read` | `reference/permissions.md:9-19` [D] |
| Safe-output writes | `GITHUB_TOKEN` by default. Fallback chain: custom `github-token` → `secrets.GH_AW_GITHUB_TOKEN` (fine-grained PAT) → `secrets.GITHUB_TOKEN` | `reference/auth.mdx:167-199` [D] |
| GitHub App alternative | `github-app.client-id` and `private-key`; the token is minted per job with the job's permissions and revoked at the end. This does not apply to `COPILOT_GITHUB_TOKEN` | `auth.mdx:507-540` [D] |
| Cross-repo, Projects, triggering CI on PRs | PAT or App required | `auth.mdx:53-68` [D] |
| Queue dispatch credential | App token minted with `actions: write`, or `GH_AW_GITHUB_TOKEN` / `GITHUB_TOKEN`; the kind is recorded in config | `pkg/workflow/work_queue_dispatch_credentials.go:7-41` [O] |
| Dispatch tag creation `gh-aw/work-queue/<SHA>` | `actions: write` + `contents: write` | `reference/work-queue.md:72` [D] |
| Issue projection hooks | `contents: write`, `issues: write`, `actions: read`; per-hook App token when `safe-outputs.github-app` | `pkg/workflow/work_queue_issues.go:17-19` [O]; `reference/work-queue.md:186,202` [D] |
| Maintenance reconciliation | `actions: read`, `contents: write` | spec :1216-1217 [D] |
| Queue Git publication | "selected queue credential"; agents and snapshot MCP receive none | spec :893-895; `reference/work-queue.md:18` [D] |
| Operator CLI | User token via `gh`. `push` for producer/reconciler, `admin` for administrator, `maintain` or `admin` for `clear`; refuses CI environments for `clear` | `pkg/workqueue/branch.go:365-390` [O]; `reference/work-queue.md:272` [D] |
| Engine inference | `COPILOT_GITHUB_TOKEN` (PAT only), `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` / `CODEX_API_KEY`, `GEMINI_API_KEY`, or WIF/OIDC variants | `auth.mdx:19-50,102-470` [D] |

[D] "Queue use MUST NOT require repository-administration permission" (spec :1109).
[O] Even so, operator `policy`, `cancel-claim` and `reprioritize` authenticate as
`administrator`, which needs repo `admin` (`pkg/cli/work_command_operations.go:115-125`;
`branch.go:382-384`). I did not determine whether AW-managed first-submit bootstrap
avoids admin in all cases (spec :909-918 says Policy installs at genesis through the
first producer submit).

### 1.7 Preliminary evidence against P02a rejection criteria (leads only)

| Criterion | Evidence toward failing | Evidence toward passing | Unsettled |
| --- | --- | --- | --- |
| 1. External process holds and exercises a Claim through a supported authenticated path | §1.5: worker role is bound to the Actions run (`work_queue_native.cjs:240-251`); operator cannot impersonate workflow roles (`branch.go:362-363`); no claim/finish/lease commands | Operator CLI is a supported authenticated non-Actions path for producer/administrator/reconciler roles (`branch.go:357-391`) | Whether a self-hosted Actions runner on the supervisor host is acceptable. A live spike would confirm the refusal behaviour |
| 2. Reproducibly pinnable; unsupported versions rejected | Runtime fetch of `compat.json` from `gh-aw-actions@main` can fail pinned workflows (`check_version_updates.cjs:29`). Version-3 schemas grow without a version bump (`reference/work-queue.md:374-376`). Specs say "Working Draft" / "implementation in progress". Fast release cadence (101 commits in ~3.5 days; 43 since v1.0.1). Depends on REST API version `2026-03-10` (spec :1248) | Release tags exist (v1.0.0, v1.0.1); the gh extension can be pinned (`releases.md:46,56`); lock files SHA-pin actions; schemas carry `version: const 3`; queue spec and schemas unchanged v1.0.0→pin; closed readers reject unknown fields (`reference/work-queue.md:31,376`) | Whether a consumer can disable or self-host the compat check; whether the setup action at a tag is fully self-contained |
| 3. Net reduction of maintained Weave code and responsibilities | Adoption still needs AW worker workflows, Actions-run binding, Markdown compile/lock-file upkeep and engine secrets. [I] An external-supervisor adapter would sit beside these. Upstream queue code is large (≈12.2k Go + ≈34.7k JS non-`.test` lines), though Remora would consume rather than maintain it | Queue, scheduler, checkpoint, DAG gating and safe-output gates are already implemented upstream | Weave-side line counts are out of this sub-scope; P01/P02a must measure them |

---

## 2. Symphony

- **License [O]:** Apache-2.0 (`symphony:LICENSE`, sha256
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`). `NOTICE`
  reads "Copyright 2025 OpenAI" (sha256
  `38c76eb8701e52953f63154a77b407667a6ee34c3a2a8785c8f8b2cd5494d09d`).
  `README.md:41` confirms the license. [I] Reuse of code would require carrying the
  NOTICE content.
- **Maturity [O]:**
  - SPEC "Status: Draft v1 (language-agnostic)" (`SPEC.md:3`).
  - README: "low-key engineering preview for testing in trusted environments"
    (`README.md:11`).
  - The Elixir implementation is "prototype software intended for evaluation only"
    (`elixir/README.md:7`).
  - Tags: v0.0.1–v0.0.3, plus `nightly`.
- **Runner versus tracker boundary [D]:**
  - "Symphony is a scheduler/runner and tracker reader". Ticket writes "are typically
    performed by the coding agent through provider-native tools executed by Symphony
    with the configured tracker credential" (`SPEC.md:36-44`; §11.5 :1310-1323).
  - Success may end at a handoff state such as `Human Review` rather than `Done`.
  - Components: Workflow Loader, Config, Tracker Adapter, Orchestrator, Workspace
    Manager, Agent Runner (:71-116).
  - The runner wraps workspace + prompt + Codex app-server client (§10.7, :1163-1176).
  - "The Codex app-server protocol for the targeted Codex version is the source of
    truth" (:950-962).
- **`WORKFLOW.md` contract [D]:**
  - Repository-owned Markdown with YAML front matter (config) and a prompt-template
    body (§5.1-5.2, :318-353).
  - Front-matter keys: `tracker` (`kind`, `provider`, `required_labels`,
    `active_states`, `terminal_states`), `polling.interval_ms`, `workspace`, `hooks`,
    `agent`, `codex` (§5.3, :355-492).
  - Example: `symphony:elixir/WORKFLOW.md`. It runs Codex with
    `shell_environment_policy.inherit=all`, `approval_policy: never` and
    `networkAccess: true` (:34-39) [O]. That is a high-trust sample, not a hardened
    default.
- **Concurrency [D]:**
  - `agent.max_concurrent_agents` (default 10) and
    `max_concurrent_agents_by_state` (:444-461).
  - `available_slots = max(max_concurrent_agents - running_count, 0)` (:777-788).
  - SSH extension: optional `worker.max_concurrent_agents_per_host` (:2259-2262).
- **Blocker metadata [D/O]:**
  - `blocked_by` is "best-effort provider metadata". Eligibility is the
    adapter-derived `dispatchable` boolean (:187-195), and "adapters MUST NOT invent
    blocker semantics" (:1278-1281).
  - [O] The bundled GitHub adapter sets `blocked_by: []` and
    `dispatchable: not pull_request` (`elixir/lib/symphony_elixir/github/client.ex:198-199`).
    Blockers give no dependency gating for GitHub there.
- **In-memory claimed set and cross-host exclusivity [D/O]:**
  - "Single authoritative in-memory state owned by the orchestrator", including
    `claimed` (:280-293). Candidates must not already be in `claimed` (:763).
  - "Restart recovery is tracker-driven and filesystem-driven (without a durable
    orchestrator DB)" (:727-731).
  - [O] `claimed` is a `MapSet` in `elixir/lib/symphony_elixir/orchestrator.ex:39,776,823,989`.
  - Non-goal: "General-purpose workflow engine or distributed job scheduler" (:64).
  - SSH extension: "The orchestrator remains the single source of truth" for remote
    hosts (:2266-2267). It warns about re-executing the same ticket on multiple hosts
    (:2304-2306).
  - The README says blocked entries are in memory only, and a restart can re-dispatch
    them (`elixir/README.md:32-36`).
  - **Nothing found provides cross-host exclusivity between independent orchestrators**
    (searched SPEC for "distributed", "multiple instances", "lock", "leader",
    "cross-host").
- **Identity assumptions [D/O]:**
  - One tracker credential is held by the orchestrator host. Tracker-token env vars
    are stripped from the Codex child (`elixir/README.md:24-28`; SPEC :143-150).
  - GitHub adapter: `GITHUB_TOKEN` / `provider.token` and `GITHUB_REPO`
    (`github/client.ex:25-28,288-296`).
  - There is no per-worker or enrolment identity. The optional HTTP API is read-only
    except `POST /api/v1/refresh` (:1609,1628).
  - Trust boundary is implementation-defined (:1721-1733).
- **Runtime/language [O]:** Elixir 1.19.5-otp-28 / Erlang 28 (`elixir/mise.toml`,
  `elixir/mix.exs:7-8`). Requires a Codex CLI with app-server mode (SPEC :148).
- **What an optional Remora runner adapter would need [I]:**
  1. A tracker adapter whose `dispatchable` reflects the Remora authority's accepted
     claim for that host, rather than GitHub issue state.
  2. Removal or neutering of Symphony's own claim/dispatch authority. Its `claimed`
     set would duplicate authority unless it only mirrors.
  3. Mapping Remora stop/fence signals into Symphony's reconciliation, which currently
     terminates on tracker state change (§8.5, :819-840).
  4. A replacement or wrapper for the Codex-specific runner if non-Codex agents are
     needed.
  5. Hardened sandbox and approval settings.
  6. Elixir/OTP as an additional runtime.

  Adopting only vocabulary (`WORKFLOW.md` front-matter layout, active/terminal states,
  `dispatchable`, `blocked_by`) carries none of these costs.

---

## 3. Beads

- **License [O]:** MIT (`beads:LICENSE`, "Copyright (c) 2025 Beads Contributors",
  sha256 `caa2c60efbbf71e18b45ef6006a18213f8a42554b235af88883f6f1ec240b7db`).
  `THIRD_PARTY_LICENSES` (sha256 `50b7ae5d…24aa`) lists Dolt and go-mysql-server
  under Apache-2.0.
- **Readiness and dependency commands [D/O]:**
  - `bd ready` lists "open issues with no active blockers". It excludes
    in_progress/blocked/deferred/hooked.
  - `bd ready --claim` atomically claims the first match. `--explain` shows
    dependency-aware reasoning for why issues are ready or blocked.
  - Other `bd ready` flags: `--sort priority|hybrid|oldest`, `--unassigned`,
    `--parent`, label filters (`beads:docs/CLI_REFERENCE.md:8049-8094`).
  - Related commands: `bd blocked` (:6559-6572), `bd dep tree [--direction=up] [--depth]`
    (:2332-2357), `bd dep cycles` (:2269-2274), `bd update <id> --claim`
    (`README.md:73-79`).
  - Blocking dependency types: `blocks`, `parent-child`, `conditional-blocks`,
    `waits-for`. `related`, `discovered-from`, `tracks` and others are non-blocking
    (`internal/types/types.go:1463-1493,1547-1558`).
- **Explanation output shape worth borrowing [O]** (`internal/types/types.go:1935-1985`):
  - `ReadyExplanation{ready[], blocked[], cycles[][], summary{total_ready, total_blocked, cycle_count}}`.
  - `ReadyItem` adds `reason`, `resolved_blockers`, `pinned_dependencies`,
    `open_dependencies`, `dependency_count`, `dependent_count` and `parent`.
  - `BlockedItem` adds `blocked_by[]{id,title,status,priority}` and `blocked_by_count`.
  - [I] This maps directly onto a Remora "why not claimable" explanation. Remora would
    need extra reason kinds for missing completion evidence, resources, Needs-human
    and review budget.
- **Storage [D]:**
  - Dolt in either embedded mode (default, in-process, single writer) or server mode
    (external `dolt sql-server`, multiple writers).
  - Cross-machine sync is `bd dolt push/pull` against `refs/dolt/data`.
    `.beads/issues.jsonl` "is an export … not the source of truth" (`README.md:127-143`).
  - A schema version guard refuses older binaries on newer databases
    (`README.md:145-177`).
  - An HTTP backend is experimental. There, `ready --claim` may "list and claim in two
    steps rather than one transaction" (`README.md:178-200`).
- **Claim safety limits [D]:**
  - "A claim lease (`bd ready --claim` + `bd heartbeat`, reaped by `bd reclaim`) is
    only meaningful on the replica that granted it. The `leases` table is clone-local
    and never replicates" (`docs/multi-agent/federation.md:192-211`).
  - An in-repo proposal says `bd` lacks a general compare-and-set for coordination
    fields beyond `--claim` / `unclaim --if-assignee`
    (`PROPOSAL-cas-conditional-update.md:1-40`).
- **Runtime [O]:** Go (`go.mod:3`, go 1.27.3); distributed via brew, npm and release
  binaries (`README.md:96-115`).
- **Not to be adopted as a second issue database.** The plan already excludes this
  (plan §2, Beads row). The evidence above agrees: Beads' authority is its own Dolt
  database, and its claims are replica-local. Use it only as a source of vocabulary
  and explanation UX.

---

## 4. Cross-cutting: the ten Required contracts (plan §3)

Legend: **O** observed in code, **D** documented only, **—** absent / not found. A
"provides" entry is not conformance. Live behaviour is unverified for all three
projects.

| # | Contract | gh-aw | Symphony | Beads |
| --- | --- | --- | --- | --- |
| 1 | At most one accepted dev owner and one review owner per task/job | **O/D** single-winner Claims via Git `--force-with-lease` CAS (`branch_git.go:545-546`; spec :1070,1101). Live contention unverified (:3301). Owners must be Actions worker runs (§1.5). No distinct dev/review roles. [I] Review would be modelled as separate Work | **D/O** in-memory `claimed` set in one orchestrator (SPEC :280-293); no cross-host exclusivity | **D** atomic `--claim` within one Dolt DB; leases are replica-local (`federation.md:192-211`) |
| 2 | Claimable only when prerequisites have accepted completion evidence and resources are available | **D/O** DAG gating on verified **Results**; Issue/PR condition nodes; capacity and resource scope (`reference/work-queue.md:111-113`; spec §7.15-7.16) | **D** best-effort `blocked_by`, adapter `dispatchable`. GitHub adapter: `blocked_by: []` (O) | **O** `bd ready` blocking edges by status, not evidence |
| 3 | Stale worker cannot publish under an old claim generation | **D/O** effects gated per Claim against the bound original run (attempt 1); finish only by the bound worker; no lease/expiry or takeover ("no Claim lease") | — (stall timeout and tracker-state termination only, SPEC :819-840) | — fencing not found; replica-local leases |
| 4 | Review binds exact candidate and exact task revision | Partial **D**: immutable Work payload, `execution_ref` immutable SHA, signed-PR delivery checks exact head (`reference/work-queue.md:70,344`). No review concept | — | — |
| 5 | Review budget is task-owned and survives restarts and branches | — (only `retry.max_attempts` per Work, `reference/work-queue.md:44,346`) | — (in-memory retry backoff) | — |
| 6 | Timeout, unavailable checker or unverified result cannot become PASS | Partial **D**: delivery barriers stay pending on unavailable evidence; a successful Actions conclusion cannot release or settle (`reference/work-queue.md:111,115`; spec :1314-1321). Applies to effect delivery, not review verdicts | — | — |
| 7 | Done = integrated deliverable plus accepted evidence | Partial **D**: Result only after independent verification; verified PR delivery → "Needs review", not Done; PR dependencies need merge evidence (`reference/work-queue.md:113,160-165`) | — (agent moves tracker state; handoff may be `Human Review`) | — (`bd close`) |
| 8 | Human commands authenticated, correlated, auditable | Partial **O/D**: operator CLI authenticated by `GET /user` + repo permission (`branch.go:357-391`), request IDs, `trace` / `explain`; Issue close can cancel Work (`reference/work-queue.md:184`). Issue-comment command parser for the queue not found (not exhaustively searched) | — (only `POST /api/v1/refresh`; tracker state is the control channel) | — (local CLI; no authenticated principal found) |
| 9 | Board and summaries are recoverable projections, not locks | **D/O** Issues are a mirror only and "cannot store the queue"; projection failure does not roll back (`reference/work-queue.md:6,186`) | **Conflicts**: tracker state is the eligibility input and restart-recovery source (SPEC :727-731) | **Conflicts if adopted**: Dolt DB is a separate authority |
| 10 | No model process gets merge authority or unrestricted controller credentials | **D/O** read-only agent job; queue credentials withheld from agents (spec :893-895). But `merge_pull_request` and `approve_workflow_run` safe outputs exist and must stay unconfigured (spec :2422,3736) | Partial **D**: tracker token withheld from the child, but tools act with that credential; sample config is high-trust (`elixir/WORKFLOW.md:34-39`) | N/A (no execution component) |

## 5. Unknowns, blockers, and items only a live spike can settle

1. **External-worker refusal, live.** Confirm in a disposable repository that a
   non-Actions process cannot finish or effect a Claim through any supported gh-aw
   path. Also confirm the operator CLI refuses worker impersonation
   (`branch.go:362-363`). Code evidence is strong, but it was not executed here.
2. **Self-hosted runner question.** Can an AW worker on a supervisor-operated
   self-hosted runner meet criterion 1? This is a definitional decision for P02a or
   the human. Plan §4 forbids hiding a second authority behind Actions.
3. **Git CAS under contention.** `--force-with-lease` publication under real
   concurrent pushes and ambiguous network responses. Upstream states this is
   unverified (spec :3301, :3347).
4. **Pinning reproducibility.**
   - Can a consumer neutralize or pin the `compat.json` remote check
     (`check_version_updates.cjs:29`)?
   - Is a tagged `actions/setup` self-contained?
   - Can version-3 additive drift be detected or rejected by an older reader?
   - Is REST API `2026-03-10` available on the target host?
5. **Hosted gates upstream marks unverified:** immutable-SHA dispatch, hosted Git
   publication, hosted execution and native delivery (spec §9.1 :3301-3321).
6. **Latency and request volume.** Every grant/finish needs an Actions job, a Git
   fetch of full queue history and a push. There is no same-turn grant to the agent
   (spec :3352). Must be measured against plan §4 stop/poll targets.
7. **Admin requirement.** Which steady-state operations require repository `admin`
   via the operator path versus AW-managed bootstrap (spec :1109 vs `branch.go:382-384`).
8. **Symphony as runner.** No upstream support for an external authority's claims.
   Adapter feasibility (contract 9 conflict, Codex-only runner) is untested.
9. **Weave-side inventory for criterion 3.** Outside this sub-scope and not measured
   here.
10. **Not verified:**
    - The live docs site build revision.
    - The behaviour of any upstream binary (none were run).
    - Whether `githubnext/gh-aw` is a formal redirect, as opposed to merely resolving
      to the same SHA.
    - Exact meaning of the 27 `*_checks.cjs` files (counted as non-test by file name
      only).
