# P01 — Reuse and authority decision: index

Status: proposed candidate for independent review. P01 names a **preferred backend
candidate (narrow Git-state adapter) and fallback (gh-aw work queue)** for P02a; it does
not select the production backend. "Preferred" is the outcome P01 expects from the
code-level evidence, not a tie-break: the plan evaluates gh-aw first (plan sections 1-2),
and if gh-aw passes all three rejection criteria and A01/A04/A05/A07 plus A17 fencing, the
plan's reuse rule governs and gh-aw is selected (ADR 0003). Default placement:
supervisor-hosted reducer; fallback: Actions-hosted reducer. No two authorities are
proposed for the same state.

## Files and criteria

| File | Purpose | P01-AC01 | P01-AC02 | Task-packet deliverable |
| --- | --- | :-: | :-: | --- |
| `contract-comparison.md` | Contracts 1-10 and scope items mapped to reused code, adapter work or demonstrated gap; preferred backend and fallback; placement; authority map; what P01 does not decide | ✓ | | Reuse inventory |
| `weave-migration-boundaries.md` | Existing Weave behaviour; boundary for each P12 cutover step; what Weave does not record | | ✓ | Reuse inventory |
| `license-report.md` | Licences, digests, notice obligations, copy vs depend; Remora licence undecided | ✓ (licence row) | | License report |
| `handoff-P02a.md` | Conformance fixtures, rejection-criteria evidence, measured quantities, Weave SLOC for criterion 3, open questions | ✓ | | Interface decisions |
| `handoff-P02b.md` | Execution/stop interface, reviewer-launch fixture, runtime and credential tests, host requirements, joint M0 stop gate | ✓ | | Interface decisions |
| `handoff-P03.md` | Task/criterion/packet/review fields, digest rules, revision/approval objects, ownership, fixtures | ✓ | | Interface decisions |
| `scope-requests.md` | Proposed edits outside P01 paths (NOTICE, bootstrap policy pointer, validation record) | | | — |
| `weave-inventory.md`, `pins-weave.json` | Research: Weave pin, licence, code map, behaviour, migration leads | ✓ | ✓ | Reuse inventory |
| `upstream-surfaces.md`, `pins-upstream.json` | Research: gh-aw, Symphony, Beads surfaces; external-worker binding | ✓ | | Reuse inventory |
| `runtime-and-identities.md`, `permission-evidence.json` | Research: credential types, permissions, rulesets, transports, runtime support | ✓ | | Permission matrix |
| `../../decisions/0002-internal-interfaces.md`, `../../../contracts/interfaces.v1.json` | Internal interfaces with owner modules and consumers | ✓ | | Interface decisions |
| `../../decisions/0003-backend-preference-and-authority.md` | Preferred/fallback backend, placement, single-authority rule, P02a rejection table | ✓ | | Interface decisions |
| `../../../contracts/permission-matrix.v1.json`, `permission-matrix.schema.json` | Versioned machine-readable permission matrix (`matrix_version` 1.0.0): both placements, per-role permissions, forbidden permissions, repository/Project scope, rulesets, decision points DP-01…DP-10, bootstrap profile | ✓ | | Versioned permission matrix |
| `../../../contracts/upstream-pins.v1.json` | Consolidated pins equal to the two research pin files | ✓ | | Reuse inventory |
| `../../../tests/contracts/test_permission_matrix.py` | Standard-library checks of the matrix (schema, evidence resolution, single authority, forbidden permissions, rulesets, scope, decision points), pins and interface ownership (42 tests) | ✓ | | Versioned permission matrix |
| `../../../tests/contracts/test_unverified_routing.py` | Every unverified research item has a stable ID and a documented route; document consistency checks (7 tests) | ✓ | ✓ | — |
| `unverified-routing.json` | Stable IDs (`U-PE-*`, `U-US-*`, `U-WI-*`) and routes for every unverified item | ✓ | ✓ | — |
| `scripts/` | Verbatim stdlib-only scripts used for the static counts and documentation checks (run with `python3.12 -I`, paths as arguments) | | ✓ | Reuse inventory |

Verification: `python3 -m unittest discover -s tests -v` (includes `tests/contracts/`),
`python3 -m bootstrap check`, `git diff --check`. These are format and consistency checks;
they do not establish live GitHub or runtime behaviour.

## Human decisions required

Recommendations are P01's; the human decides and records the answer and its scope on
GitHub. Q2-Q10 are the matrix decision points DP-01…DP-09; Q15 is DP-10.

| # | Decision | Options | Recommended | Source |
| --- | --- | --- | --- | --- |
| Q1 (U-US-02) | Does an AW worker on a self-hosted runner operated by the supervisor host satisfy gh-aw criterion 1? | yes / no | No recommendation until P02a reports the technical result. Considerations for the human: the run would be a genuine Actions run with an Actions identity (not a fabricated one), but criterion 1 asks for "a process outside Actions", and plan section 4 forbids hiding a second authority behind Actions. The answer is a definitional decision for the human after P02a | `upstream-surfaces.md` §1.5, ADR 0003 |
| Q2 (U-PE-03) | DP-01 Organization- or user-owned repository and Project | org_owned / user_owned | org_owned; if user_owned, accept a separate classic/OAuth `project` credential with its exposure stated | `runtime-and-identities.md` §G.1 |
| Q3 | DP-02 State writer / publisher credential | GitHub App / fine-grained PAT / classic PAT | GitHub App (only documented single-actor bypass; can read Checks) | §A.1, §D |
| Q4 | DP-03 Trusted-CI identity | dedicated CI App / Actions `GITHUB_TOKEN` | dedicated CI App, separate from the publisher | §B.6 |
| Q5 | DP-04 May candidates modify `.github/workflows/**`? | reject / allow with Workflows write | reject | §G.1 item 6 |
| Q6 | DP-05 Which bypass may repository admins hold? | none / admin bypass on `main` only, in `pull_request` mode / admins on every list as visible override | admin bypass on `main` only, in `pull_request` mode (needed by the Q15 recommendation for a single maintainer); never on state/candidate rulesets; never `exempt` | §B.7, §D |
| Q7 | DP-06 App private key as an Actions secret (Actions placement, Actions projection job) | reject / accept | reject unless the Actions placement is required | §B.3, §G.3 item 7 |
| Q8 | DP-07 Repository visibility and plan | public / private on Pro, Team, Enterprise / private on Free (unsupported) | public, or private on a paid plan | §D |
| Q9 | DP-08 Who opens integration PRs? | human / supervisor | human for the pilot | §B.2 |
| Q10 | DP-09 Placement for the pilot | supervisor_hosted / actions_hosted | supervisor_hosted | plan section 4 |
| Q11 (U-PE-13) | P02b host: Docker Sandboxes needs Ubuntu 24.04+ (or macOS 14+ Apple silicon, Windows 11); the bootstrap host is Debian 11 | provide a supported host / rootless OCI only on Debian 11 / both | both: a supported host for the microVM profile, and rootless OCI as the portable profile once cgroup v2 + systemd enforcement is confirmed | §E, `handoff-P02b.md` §5 |
| Q12 (U-WI-05) | Preserve the legacy Weave ledger on host `gengar` | archive now / later | archive a read-only copy now and record its digest; it is load-bearing for P12 step 2 and is not on GitHub | `weave-migration-boundaries.md` §2, §5 |
| Q13 | Remora's distribution licence | maintainer's choice | decide before any upstream code is copied; P01 makes no licence recommendation | `NOTICE.md`, `license-report.md` |
| Q14 (U-WI-06) | Reuse Weave code by copying with attribution or by re-implementing against the same fixtures | copy with MIT attribution / re-implement | copy-with-adaptation for the modules listed in `weave-migration-boundaries.md` §4, after Q13, with the NOTICE change in `scope-requests.md`; first confirm the Weave rights holder and note the AI co-authorship flag | `license-report.md` |
| Q15 | DP-10 Required approvals on `main`, given that pull request authors cannot approve their own pull requests (S-gh-pr-approve-required) | one approval plus a human admin bypass in `pull_request` mode / one approval from a second human / zero approvals with PR and required checks | **one approval plus the human admin bypass in `pull_request` mode** while there is one maintainer (every merge is an audited bypass; Apps and PATs cannot merge); one approval from a second human once a second maintainer exists. **Zero approvals is not recommended:** Contents write includes the merge endpoint, so every Contents-write holder (supervisor App, Actions publisher, setup credential) could merge once checks pass, and "no merge authority" would rest on code only. With one approval and no admin bypass (Q6 = none), a single maintainer cannot merge | `contracts/permission-matrix.v1.json` DP-10 |

## Items marked unverified (routed)

Stable IDs are defined in `unverified-routing.json`; `tests/contracts/test_unverified_routing.py`
checks that every unverified item in `permission-evidence.json`, every item of
`upstream-surfaces.md` §5 and every bullet of `weave-inventory.md` §H has an ID, and that
each ID appears here and in the handoff it is routed to.

| ID | Item | Routed to |
| --- | --- | --- |
| U-PE-01 | Whether an individual User actor_type works as a repository ruleset bypass actor (REST enum lists it; UI eligible list does not). | P02a |
| U-PE-02 | Whether the GitHub Actions GITHUB_TOKEN identity can be a ruleset bypass actor (not found). | P02a (Actions placement only) |
| U-PE-03 | Whether a GitHub App installation can access user-owned Projects v2 (no App permission found). | P02a (setup observation); P07; human DP-01 |
| U-PE-04 | Fine-grained PAT / App permission levels required by GraphQL mutations createProjectV2, updateProjectV2Field, linkProjectV2ToRepository, createCommitOnBranch, updateRefs. | P02a |
| U-PE-05 | Which HTTP status (409 vs 422) REST ref PATCH returns for a non-fast-forward race. | P02a |
| U-PE-06 | Error shape and race behaviour of createCommitOnBranch expectedHeadOid mismatch and updateRefs beforeOid mismatch. | P02a |
| U-PE-07 | Whether ruleset Restrict updates / Block force pushes are enforced identically for REST, GraphQL and git push paths. | P02a |
| U-PE-08 | Whether bypass of one ruleset leaves rules in a separate no-bypass ruleset enforced for the same actor (two-ruleset layout). | P02a |
| U-PE-09 | Whether a GitHub App pull request review counts toward required approvals on main. | P02a; human DP-08/DP-10 |
| U-PE-10 | GITHUB_TOKEN behaviour when pushing changes to .github/workflows (no workflows permissions key documented). | P02a (Actions placement only); P09 |
| U-PE-11 | Classic PAT/OAuth scope required to create rulesets (not tabulated). | P02a (setup observation); P10 |
| U-PE-12 | Docker Sandboxes actual defaults on target host (docs inconsistent on shared skills mode; SSH agent forwarding on by default; default allowed-domain list not enumerated on defaults page). | P02b |
| U-PE-13 | Docker Sandboxes support on non-Ubuntu Linux hosts such as the Debian 11 bootstrap host (not in documented support list). | P02b; human Q11 |
| U-PE-14 | Rootless Docker cgroup limit enforcement on target hosts (silently ignored without cgroup v2 + systemd). | P02b |
| U-PE-15 | OCI egress enforcement including DNS and IPv6 bypass (not documented; P02b measurement). | P02b |
| U-US-01 | External-worker refusal, live | P02a |
| U-US-02 | Self-hosted runner question | P02a; human Q1 |
| U-US-03 | Git CAS under contention | P02a |
| U-US-04 | Pinning reproducibility (compat.json, tagged setup action, v3 additive drift, REST API version 2026-03-10) | P02a |
| U-US-05 | Hosted gates upstream marks unverified (immutable-SHA dispatch, hosted Git publication, hosted execution, native delivery) | P02a |
| U-US-06 | Latency and request volume; no same-turn grant to the agent (spec :3352) | P02a |
| U-US-07 | Admin requirement for steady-state operator operations | P02a |
| U-US-08 | Symphony as runner | not adopted for the pilot; any later runner adapter needs its own task after P06 |
| U-US-09 | Weave-side inventory for criterion 3 | resolved by weave-inventory.md §E; P02a computes the net figure |
| U-US-10 | Not verified: docs site build revision, upstream binary behaviour, githubnext redirect, meaning of 27 *_checks.cjs files | P02a (binary behaviour within its fixtures); informational otherwise |
| U-WI-01 | Executed status of Weave's controller tests; the '89 passing' figure is not reproducible statically | human; P12 (legacy import) |
| U-WI-02 | capabilities.md and orchestration-requirements.md conflict with observed behaviour | informational; P12 import must not rely on them |
| U-WI-03 | Whether gh-aw safe outputs/queue could replace publisher.py, state.py, the executor and github.py writes | P02a criterion 3 |
| U-WI-04 | Live Projects automation settings of the Weave board | human; P07; P12 |
| U-WI-05 | Contents and size of the legacy ledger on host gengar | human Q12; P12 |
| U-WI-06 | Legal effect of AI co-authorship trailers; Weave rights holder vs Remora owner | human Q14 |
| U-WI-07 | Per-file history taken from Weave's decision record, not git log | informational |
| U-WI-08 | No blocker prevented the inventory | informational |

Matrix-level open points not in the research lists: identity granularity of several
supervisors under one App (per-host keys) → P02a (`handoff-P02a.md` §5); in the Actions
placement, how a supervisor without Contents write submits transitions and hands over
candidate material, and the App permission for workflow dispatch → P02a/P05 if that
placement is selected; projection-only on a private user-owned repository cannot be
expressed (classic `repo` includes Contents write) → DP-01/DP-07; whether the owner of a
personal repository is matched by a `RepositoryRole` admin bypass on `main`, and how
`pull_request` bypass mode behaves → P02a (`handoff-P02a.md` F-APPROVE).

Matrix versioning: `matrix_version` stays 1.0.0 for every change made while the P01
candidate is under review; the first bump follows human acceptance of P01 (rule recorded in
the matrix's `versioning` field and tested).
