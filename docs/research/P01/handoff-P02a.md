# Handoff to P02a — coordination and backend-selection spike

From: P01 (proposed, pending acceptance). P02a selects the backend; P01 only names the
preferred candidate (narrow Git-state adapter) and the fallback (gh-aw work queue) in
`docs/decisions/0003-backend-preference-and-authority.md`.

Ground rules carried from the plan (section 11):

- Start the gh-aw fit assessment and the narrow-adapter tests **on day one**, in separate
  disposable repositories or authority branches, with the **same fixtures**.
- Default to two trusted supervisor-hosted reducers (fixture processes). Runtime
  containment and physical termination belong to P02b.
- gh-aw box: three engineer-days; any failed or unresolved criterion at the deadline is
  no-go for gh-aw. The narrow adapter does not wait for that decision.
- Parallel experiments are not simultaneous production authorities. No custom daemon is
  built because the spike is inconvenient.
- Selection order (ADR 0003): if gh-aw passes all three rejection criteria and
  A01/A04/A05/A07 plus A17 fencing, the plan's reuse rule governs and gh-aw is selected;
  otherwise the narrow adapter if it passes; otherwise no-go. P01's "preferred" label is an
  expectation, not a tie-break.

Item IDs such as `U-PE-05` refer to `unverified-routing.json`; every unverified item routed
to P02a appears below at least once.

Interfaces under test: `state-backend` and `publisher` in
`docs/decisions/0002-internal-interfaces.md` / `contracts/interfaces.v1.json`. Credentials
and rulesets: `contracts/permission-matrix.v1.json` (placement `supervisor_hosted`).

## 1. Conformance fixtures and required observable outcomes

Each fixture runs against both candidates unless marked. Record test ID, software
revisions, transport, identities, raw responses and timings.

| Fixture | Scenario | Required observable outcome |
| --- | --- | --- |
| F-A01 (U-US-03) | Two supervisors submit claims for the same ready task at the same observed head | Exactly one claim record and one accepted generation in state; the loser gets `Conflict` (or a rejection on reread), rereads, sees the owner and does not start execution; no second ledger anywhere |
| F-A04a | Owner renews while the lease is expiring and a second host attempts takeover | One generation wins; state history shows a single accepted sequence |
| F-A04b | The losing (old) generation then publishes a candidate and submits a transition | `publish_candidate` and `apply_transition` reject with `StaleGeneration`; the old ref is not referenced by task state |
| F-A05 | State commit succeeds but the response is dropped (fault-injecting proxy) | Retry looks up `command_id` and returns the original receipt; no second claim, reservation or round charge |
| F-A07 | Owner host is cut off from GitHub while its fixture process keeps computing | After the offline-grace interval the supervisor stops itself; no output from the old generation is accepted; state reports termination uncertainty; a strict task is not reassigned before confirmed termination |
| F-A17f | Authorized stop arrives during active work, and separately during an in-flight publication | One transition records `stop_requested` and revokes publication authority; later publication is rejected; in-flight effects are reconciled with `read_back_effect`; no `stop_confirmed` is recorded without termination evidence (P02b supplies real termination at the joint gate) |
| F-SKEW | Supervisor clock outside the configured skew bound | It cannot grant or renew; the refusal is visible |
| F-SNAP | Verified snapshot plus bounded suffix vs full replay | Identical state; an invalid snapshot fails closed (part of A26) |
| F-T1 (narrow; U-PE-05) | REST `PATCH git/refs` with `force=false` under a concurrent fast-forward | Record the actual status code (409 vs 422) and body; decide whether it is usable as CAS (documented responses: `S-gh-rest-refs`) |
| F-T2 (narrow; U-PE-04, U-PE-06) | GraphQL `createCommitOnBranch` with stale `expectedHeadOid` | Record the error shape and any partial effect; record the permission needed (not tabulated; `S-gh-gql-commits`) |
| F-T3 (narrow; U-PE-04, U-PE-06) | GraphQL `updateRefs` with stale `beforeOid`, and with an all-zero `beforeOid` for a new `agent/**` ref | Atomic rejection across refs; creation refused if the ref exists (`S-gh-gql-git`) |
| F-T4 (both; U-US-03) | `git push --force-with-lease=<ref>:<expect>` (`--atomic` for multiple refs) in a clean Git environment with no hooks, helpers or filters | Rejection on a moved remote; record messages (`S-git-push`). This is gh-aw's own transport (`branch_git.go:545-546`) |
| F-RS (U-PE-07, U-PE-08) | Rulesets `RS-state-immutable` (deletion, non_fast_forward, no bypass) plus `RS-state-writers` (creation, update, bypass = writer App) | The writer App fast-forwards but cannot rewind or delete; another Contents-write identity cannot update; the same result for REST, GraphQL and Git push paths |
| F-GA1 (gh-aw; U-US-01, U-US-10) | A non-Actions process tries to finish or effect a Claim through every supported path, including the operator CLI | Expected from code: refusal (`work_queue_native.cjs:240-251`; `branch.go:362-363`). Record what actually happens |
| F-GA2 (gh-aw; U-US-04) | Pinning: activation with `compat.json` unreachable, blocked, or pinned; tagged `actions/setup` offline | Whether a consumer can pin or neutralize the remote check (`check_version_updates.cjs:29`) and whether an older closed reader rejects newer v3 fields |
| F-GA3 (gh-aw; U-US-07) | Steady-state operations needing repository `admin` | Which operations (`policy`, `cancel-claim`, `reprioritize`) require admin outside bootstrap (`branch.go:382-384` vs spec :1109) |
| F-RS-USER (U-PE-01) | REST ruleset with `actor_type: User` naming the account that holds a fine-grained PAT, on `RS-state-writers` | Whether the PAT holder can update while other writers cannot; decides whether DP-02 = fine_grained_pat can express single-writer enforcement |
| F-RS-TOKEN (U-PE-02; Actions placement only) | `GITHUB_TOKEN` named as a bypass actor (if any actor type accepts it) | Accepted or refused; otherwise the Actions placement needs an in-job App token |
| F-WF-TOKEN (U-PE-10; Actions placement only, otherwise P09) | A job pushes a commit touching `.github/workflows/**` with `GITHUB_TOKEN` (`contents: write`) | Accepted or refused, and the error shown (no `workflows` key is documented) |
| F-APPROVE (U-PE-09) | An App submits an approving review on a pull request to a `main` ruleset requiring one approval | Whether the approval counts. Relevant to DP-08 and DP-10; P01 does not recommend App approvals |
| F-SETUP (U-PE-03, U-PE-04, U-PE-11) | While creating the disposable test repositories, Projects and rulesets | Record the credential and scope/permission that worked, and GitHub's error text for any refusal (S-gh-gql-forming says errors name the needed permission) for: ruleset creation with a classic PAT (U-PE-11); `createProjectV2`, `updateProjectV2Field`, `linkProjectV2ToRepository` with a fine-grained PAT and an App (U-PE-04); App access to a user-owned Project (U-PE-03; if not observable in P02a's setup, P07 records it) |
| F-GA4 (gh-aw; U-US-05) | Hosted gates upstream marks unverified: immutable-SHA dispatch, hosted Git publication, hosted execution, native delivery | Pass/fail per gate on GitHub-hosted runners, with run IDs |
| F-GA5 (gh-aw; U-US-06) | A worker requests a grant and needs it in the same turn | Confirm or refute "staged intents cannot return durable grants to the agent in the same turn" (spec :3352); measure the extra round trip |
| F-API (gh-aw; U-US-04) | REST API version `2026-03-10` header on the target host | Accepted or rejected; gh-aw queue dispatch depends on it (spec :1248-1255) |

## 2. Rejection-criteria table

Fill the table in ADR 0003. Evidence already gathered (leads, not results):

| Criterion | Evidence toward fail | Evidence toward pass | Open |
| --- | --- | --- | --- |
| 1 External worker | Worker authority = original Actions run; operator CLI cannot impersonate workflow roles; no claim/finish/lease commands; authentication outside the protocol (`upstream-surfaces.md` §1.5) | Operator CLI is an authenticated non-Actions path for producer/administrator/reconciler roles only | Self-hosted runner interpretation (README Q1); live refusal not yet executed |
| 2 Pinnable | Moving remote `compat.json`; additive v3 schemas; working-draft specs; 101 commits in about 3.5 days; REST API version `2026-03-10` | Tags `v1.0.0`/`v1.0.1`; SHA-pinned lock files; `version: const 3`; queue spec and schemas unchanged `v1.0.0`→pin | Compat-check neutralization; self-contained setup action |
| 3 Net reduction (U-US-09, U-WI-03) | Worker workflows, run binding, compile/lock upkeep, engine secrets, external-supervisor adapter still needed | Queue, scheduler, checkpoint, DAG gating and safe-output gates exist upstream | No measured net figure for either option |

## 3. Weave numbers for criterion 3 (from `weave-inventory.md` §B, §E)

| Weave production code plausibly removable | SLOC |
| --- | ---: |
| `state.py` (local ledger, outbox, `flock`) | 168 |
| `publisher.py` (write-ahead comment publication) | 106 |
| `transitions.py` executor, lines 208-323 | 106 |
| `github.py` writes, lines 276-311 | 28 |
| `events.py` authenticate/decision, lines 110-152 | 34 |
| `cli.py` wiring 132-343 + 527-578 + 756-797 (also builds packets; upper bound) | 265 |
| **Subtotal (upper bound)** | **707** (+121 with `reconcile.py` = 828) |

Context: Weave controller production Python is 18 files, 4,468 lines, 3,698 SLOC; tests are
2,327 lines, 1,930 SLOC, 163 methods; JSON configuration and schemas add 1,835 lines. Tests
mainly exercising the removable code: `test_protocol.py` (16 methods) and parts of
`test_review_findings.py` and `test_transitions.py`. Do not count `scheduler.py`, gates,
`review.py`, `integration.py` or `docs_audit.py` as removable: they remain under either
backend. Subtract adapter/glue SLOC and do not delete tests to improve the figure.

Upstream behaviour not executed during P01 (U-US-10): record the actual behaviour of every
gh-aw binary and action version used in the fixtures; the docs-site build revision, the
`githubnext` redirect and the meaning of the `*_checks.cjs` files remain informational.

## 4. Measured quantities to report

| Quantity | Report |
| --- | --- |
| Transition latency | p50/p95/max from command to acknowledged commit, per transport, uncontended and contended |
| Request volume (U-US-06) | REST/GraphQL/Git requests per claim, renewal, release, publication and idle poll; rate-limit headroom |
| Clock bounds | Measured skew between hosts and the configured refusal bound |
| Authority-poll interval and offline grace | Chosen values and observed stop-detection time |
| Renewal cadence | Lease length (plan default proposal: 8 h) and renewal frequency; recovery latency after owner loss |
| Snapshot, replay, fetch | Snapshot creation time, suffix replay vs full replay time and equivalence, Git fetch bytes/time at the 500-task envelope |
| Actions cost (gh-aw, and Actions placement if exercised) | Jobs and minutes per transition |
| Authenticated identities | Which identity performed each write (App, installation, key), and what GitHub records for it |

## 5. Open questions routed to P02a

1. Self-hosted runner (U-US-02): can an AW worker on a supervisor-operated runner satisfy
   criterion 1? Evaluate technically; the human decides (README Q1).
2. `compat.json`: can the remote version check be pinned or disabled without forking?
3. REST `PATCH git/refs`: 409 vs 422 on a non-fast-forward race.
4. `updateRefs`/`beforeOid` vs `createCommitOnBranch`/`expectedHeadOid` vs explicit-lease
   `git push`: which transport is selected, with which permission (GraphQL permission
   mapping is not tabulated) and error shape.
5. Identity granularity: one App for all supervisors (one bypass actor) vs one App per
   supervisor. Whether per-host App private keys are distinguishable in GitHub's records is
   **unverified**; per-host revocation must still be possible.
6. Two-ruleset layout and ruleset parity across REST, GraphQL and Git push.
7. Whether `GITHUB_TOKEN` can be a ruleset bypass actor (affects the Actions placement only).
