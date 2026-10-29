# ADR 0003 — Backend preference, placement and single authority

Status: proposed; **P02a decides**. This ADR names a preferred candidate and a fallback
for the P02a spike. It does not select the production backend.

## Context

The plan asks M0 to choose one coordination backend after a time-boxed spike with
explicit rejection criteria, and forbids two coequal schedulers (plan sections 1, 4 and
11). P01 research (`docs/research/P01/`) found:

- Weave's controller is single-host: a local `flock` and a local ledger, with no claim
  generation, renewal or takeover. Its removable coordination/publication code is at most
  610 SLOC, or about 731 with reconciliation (`weave-inventory.md` §C2, §E).
- gh-aw's work queue implements Git-backed CAS publication, DAG gating and checkpoints,
  but worker authority is bound to the original Actions run, the operator CLI cannot take
  the worker role, and there is no lease or renewal. No supported path for an external
  worker was found (`upstream-surfaces.md` §1.5). Its specs are working drafts and a
  moving remote `compat.json` can disable pinned workflows (§1.1).
- GitHub tokens have no branch dimension; branch authority comes from rulesets and the
  trusted publisher, and only GitHub Apps are documented as single-actor bypass entries
  (`runtime-and-identities.md` §A.0, §D).
- REST ref updates have no expected-old value; `updateRefs` (`beforeOid`),
  `createCommitOnBranch` (`expectedHeadOid`) and `git push --force-with-lease=<ref>:<expect>`
  document expected-old semantics, but none has been tested under races (§C).

## Decision

1. **Preferred backend candidate: the narrow Git-state adapter** (one conditional update of
   `harness/state` per transition; per-task files, compact index, receipts, pending
   effects, verified snapshots).
2. **Fallback backend candidate: the gh-aw work queue**, assessed concurrently from day one
   within its three-engineer-day box. It is selectable only if it passes all three
   rejection criteria and the required scenarios. If neither candidate qualifies, P02a
   reports no-go and dependent implementation pauses.
3. **Placement default: supervisor-hosted reducer.** Each enrolled trusted supervisor runs
   the same pinned reducer; the state branch is the single authority.
4. **Placement fallback: Actions-hosted reducer**, separately justified for deployments that
   cannot trust state-writing supervisors. Same protocol and state branch; supervisors
   become read-only clients. Switching is an explicit pause/fence/drain epoch change.
5. **Single-authority rule.** Each state kind has exactly one authority
   (`contract-comparison.md` §5; machine form in `contracts/permission-matrix.v1.json`,
   tested by `tests/contracts/test_permission_matrix.py`). A placement or backend that fails
   is replaced, never kept as a second queue. Board and issue content are projections.
6. **Self-hosted runner question left open.** Whether an AW worker on a self-hosted runner
   operated by the supervisor host satisfies criterion 1 is for P02a to evaluate and the
   human to decide. It would still be an Actions run with an Actions identity, and plan
   section 4 forbids hiding a second authority behind Actions.

## Consequences

P02a starts both experiments on day one with the same fixtures (`handoff-P02a.md`). The
preference changes the order of expectation, not the work: gh-aw still receives its full
assessment, and the narrow adapter must still pass A01/A04/A05/A07 and A17 fencing.
State-writing supervisor credentials are part of the trusted computing base; the
permission matrix keeps them out of sandboxes and off the `main` bypass list.

If gh-aw is selected, the local state layout is replaced by gh-aw's supported storage and
checkpoint protocol, its schemas and versions are pinned, and the supervisor-hosted
placement exists only to the extent criterion 1 passed.

## Rejection-criteria table for P02a to fill

Record pass/fail with evidence for gh-aw, and the narrow-adapter result for the same
fixtures. "Lead" columns are P01 evidence, not results.

| Criterion (plan section 11) | P01 lead (cited) | gh-aw result (pass/fail) | gh-aw evidence (test IDs, logs, versions) | Narrow-adapter result | Narrow-adapter evidence |
| --- | --- | --- | --- | --- | --- |
| 1. A process outside Actions holds and exercises a Claim through a supported authenticated path, without another ledger or a fabricated Actions identity | Toward fail: `work_queue_native.cjs:240-251`, `branch.go:357-391`, `work_command_test.go:52-58`; no lease (`upstream-surfaces.md` §1.5) | | | n/a (supervisor authenticates with its own enrolled credential) | Identity used, ruleset bypass actor, doctor output |
| 2. Protocol, implementation, schemas and runtime dependencies pinnable to a reproducible compatible version; unsupported versions rejected | Mixed: tags and SHA-pinned locks vs moving `compat.json`, additive v3 schemas, working-draft specs, REST API `2026-03-10` (§1.1, §1.7) | | | Local schema version and refusal of unsupported state (A26) | Fixture IDs |
| 3. Adoption removes more hand-maintained Weave coordination/publication code than adapter/glue adds, and reduces responsibilities | Weave upper bound 610 SLOC (731 with `reconcile.py`); gh-aw still needs worker workflows, run binding, compile/lock upkeep, engine secrets (`weave-inventory.md` §E; §1.7) | | Files, non-generated SLOC removed/added, retained tests, responsibilities | Adapter SLOC added | Same accounting |
| Required scenarios A01, A04, A05, A07, A17 fencing | Not run | | | | |
| Time box | 3 engineer-days for gh-aw; any unresolved criterion at the deadline is no-go | Start/end dates | | Runs concurrently; no wait | |
