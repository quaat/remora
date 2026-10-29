# P01 — Reuse and authority decision: index

Status: proposed candidate for independent review. P01 names a **preferred backend
candidate (narrow Git-state adapter) and fallback (gh-aw work queue)** for P02a; it does
not select the production backend. Default placement: supervisor-hosted reducer; fallback:
Actions-hosted reducer. No two authorities are proposed for the same state.

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
| `../../../contracts/permission-matrix.v1.json`, `permission-matrix.schema.json` | Versioned machine-readable permission matrix (`matrix_version` 1.0.0), both placements, decision points, bootstrap profile | ✓ | | Versioned permission matrix |
| `../../../contracts/upstream-pins.v1.json` | Consolidated pins equal to the two research pin files | ✓ | | Reuse inventory |
| `../../../tests/contracts/test_permission_matrix.py` | Standard-library structural and single-authority checks (26 tests) | ✓ | | Versioned permission matrix |

Verification: `python3 -m unittest discover -s tests -v` (includes `tests/contracts/`),
`python3 -m bootstrap check`, `git diff --check`. These are format and consistency checks;
they do not establish live GitHub or runtime behaviour.

## Human decisions required

Recommendations are P01's; the human decides and records the answer and its scope on
GitHub. Q2-Q10 are the matrix decision points DP-01…DP-09.

| # | Decision | Options | Recommended | Source |
| --- | --- | --- | --- | --- |
| Q1 | Does an AW worker on a self-hosted runner operated by the supervisor host satisfy gh-aw criterion 1? | yes / no | Let P02a report the technical result first; recommended answer **no** for the supervisor-hosted placement, because it is still an Actions run with an Actions identity and plan section 4 forbids hiding a second authority behind Actions | `upstream-surfaces.md` §1.5, ADR 0003 |
| Q2 | DP-01 Organization- or user-owned repository and Project | org_owned / user_owned | org_owned; if user_owned, accept a separate classic/OAuth `project` credential with its exposure stated | `runtime-and-identities.md` §G.1 |
| Q3 | DP-02 State writer / publisher credential | GitHub App / fine-grained PAT / classic PAT | GitHub App (only documented single-actor bypass; can read Checks) | §A.1, §D |
| Q4 | DP-03 Trusted-CI identity | dedicated CI App / Actions `GITHUB_TOKEN` | dedicated CI App, separate from the publisher | §B.6 |
| Q5 | DP-04 May candidates modify `.github/workflows/**`? | reject / allow with Workflows write | reject | §G.1 item 6 |
| Q6 | DP-05 Admins on `main`/state-branch bypass lists? | remove / keep as visible override | remove; never `exempt` | §B.7 |
| Q7 | DP-06 App private key as an Actions secret (Actions placement, Actions projection job) | reject / accept | reject unless the Actions placement is required | §B.3, §G.3 item 7 |
| Q8 | DP-07 Repository visibility and plan | public / private on Pro, Team, Enterprise / private on Free (unsupported) | public, or private on a paid plan | §D |
| Q9 | DP-08 Who opens integration PRs? | human / supervisor | human for the pilot | §B.2 |
| Q10 | DP-09 Placement for the pilot | supervisor_hosted / actions_hosted | supervisor_hosted | plan section 4 |
| Q11 | P02b host: Docker Sandboxes needs Ubuntu 24.04+ (or macOS 14+ Apple silicon, Windows 11); the bootstrap host is Debian 11 | provide a supported host / rootless OCI only on Debian 11 / both | both: a supported host for the microVM profile, and rootless OCI as the portable profile once cgroup v2 + systemd enforcement is confirmed | §E, `handoff-P02b.md` §5 |
| Q12 | Preserve the legacy Weave ledger on host `gengar` | archive now / later | archive a read-only copy now and record its digest; it is load-bearing for P12 step 2 and is not on GitHub | `weave-migration-boundaries.md` §2, §5 |
| Q13 | Remora's distribution licence | maintainer's choice | decide before any upstream code is copied; P01 makes no licence recommendation | `NOTICE.md`, `license-report.md` |
| Q14 | Reuse Weave code by copying with attribution or by re-implementing against the same fixtures | copy with MIT attribution / re-implement | copy-with-adaptation for the modules listed in `weave-migration-boundaries.md` §4, after Q13, with the NOTICE change in `scope-requests.md`; first confirm the Weave rights holder and note the AI co-authorship flag | `license-report.md` |

## Items marked unverified (routed)

- All 15 `unverified` items of `permission-evidence.json`, carried verbatim in the
  matrix's `unverified` list: P02a (ruleset bypass actors, transports, ruleset parity,
  two-ruleset layout, GraphQL permission levels, App review approvals) and P02b (Docker
  Sandboxes defaults and host support, rootless cgroups, OCI egress).
- gh-aw: live external-worker refusal, `compat.json` pinning, admin needs, hosted gates
  upstream marks unverified (`upstream-surfaces.md` §5) → P02a.
- Identity granularity of several supervisors under one App (per-host keys) → P02a.
- Actions placement: how a supervisor without Contents write submits transitions and hands
  over candidate material; App permission for workflow dispatch → P02a/P05 if that
  placement is selected.
- Projection-only on a private user-owned repository cannot be expressed (classic `repo`
  includes Contents write) → DP-01/DP-07.
- Weave: executed test status, live Projects automation, legacy ledger contents → human/P12.
