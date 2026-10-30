# Handoff to P03 — portable packets and plan validator

From: P01 (proposed, pending acceptance). P03 owns the model module and the task/review
schemas; P05 and P08 consume them (ADR 0002, interface `plan-compiler`).

## 1. Ownership boundary

- P03 owns `src/remora/plan/**`, `src/remora/contracts/**`, `docs/contracts/**` and their
  tests (proposed allocation in `.remora/tasks.json`).
- P05 (state), P07 (projection), P08 (review) and P09 (evidence) **consume** these schemas
  and may not edit them. A change needs a shared-interface reservation and an explicit
  dependency update (plan section 11).
- P03 publishes a documented schema fixture so downstream tasks can work without
  overlapping ownership (P03-AC02).

## 2. Fields the bootstrap already uses (`bootstrap/core.py`)

Remaining compatible with these lets bootstrap completions be imported with their manual
provenance (`docs/development/dogfooding.md`).

**Manifest** (`.remora/tasks.json`): `schema_version` (1), `project`, `tagline`,
`source_revision` (5), `source_path`, `source_sha256`, `milestones[{id, title,
description}]`, `tasks[]`.

**Task:** `id`, `title`, `milestone`, `source_excerpt`, `depends_on`, `scope_status`,
`allowed_paths`, `deliverables`, `exclusions`, `acceptance_criteria[{id, text,
verification}]`, `verification`, `architecture`, `review_limit`. Validation today: unique
IDs matching source sections, no drift from the source excerpt, non-empty required fields,
positive integer review limit, no absolute, `..` or unrestricted (`*`, `**`, `**/*`)
paths, unique criterion IDs, criterion text equal to the source acceptance sentence,
resolved dependencies, acyclic graph, all 28 scenarios present (`core.validate`).

**Review packet** (`core.review_packet`): `schema_version` (1), `mode`
(`bootstrap_advisory`), `task_id`, `task_digest`, `source_revision`, `candidate_sha`,
`base_sha`, `developer`, `policy_bindings` (path → digest for plan, manifest, policy,
architecture), `diff_sha256`, `task`, `criteria[{id, text, verification, digest}]`,
`review_limit`, `prior_findings_instruction`, `packet_digest`. Refuses a dirty tree and a
base that is not an ancestor of HEAD.

**Review** (`core.review_template` / `check_review`): `schema_version`, `packet_digest`,
`task_id`, `task_digest`, `candidate_sha`, `base_sha`, `reviewer{identity, provider,
tool_version}`, `verdict` (`PASS` | `CHANGES_REQUESTED` | `UNVERIFIED`), `summary`,
`criteria[{id, digest, status (satisfied | violated | unverified), findings,
evidence[{check_id, executor, environment, source_sha, artifact, provenance,
independently_executed (bool), exit_status (int)}]}]`. PASS requires every criterion
satisfied with successful, independently executed evidence on the candidate SHA; the
reviewer identity must differ from the developer.

## 3. Digest rules (current behaviour; keep or version explicitly)

- `digest(value)`: SHA-256 hex of raw bytes, or of
  `json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()`
  (UTF-8). This is **not** RFC 8785 canonical JSON: float formatting and Unicode
  normalization are not specified. Recommendation: forbid floats in digested objects, state
  the rule in the schema, and version it if it changes.
- Task digest = `digest(task object)`; criterion digest = `digest({id, text, verification})`;
  packet digest = `digest(packet without packet_digest)`; source digest = SHA-256 of plan bytes.
- Any change to a digested field yields a new revision; evidence bound to the old digest
  becomes invalid (plan sections 5 and 8).

## 4. Fields to add (plan sections 5 and 8)

**Task revision** (section 5): human owner; plan revision; context links and prerequisite
outputs; shared interfaces/resources with **hard vs ordinary** class; expected
documentation changes; blocking IDs vs non-blocking references; milestone gates; per
criterion an observable outcome and method (check ID or human evidence); architecture rule
IDs or a justified not-applicable result; required capabilities/toolchain, risk class,
time/cost budget, review limit; accepted deliverable location for non-code tasks
(contract 7).

**Review packet** (section 8): intended integration target; architecture and
verification-policy revisions; prior findings with disposition; accumulated round count and
remaining budget; developer evidence labeled supplied and trusted-CI evidence identified
separately; evidence mode (`unverified_pilot` | `trusted_ci`; bootstrap keeps
`bootstrap_advisory`).

**Verdict evidence** (section 8): add `environment_digest`, `command`/`check_id`,
`log/artifact reference` by digest, executor identity and provenance class
(`developer_supplied` | `reviewer_executed` | `trusted_ci` | `human_inspection`).

## 5. Revision and approval objects (proposed shapes)

- `TaskRevision{task_id, revision (monotonic int), parent_digest, definition_digest,
  criteria[] with digests, plan_source_digest, architecture_baseline_revision,
  verification_policy_revision, approval_id}`.
- `Approval{approval_id, kind (plan | revision | scope_amendment | review_limit |
  manual_acceptance), binds[] (digests), actor, command_id, decided_at, reason}`. In the
  product, approvals come from authenticated command receipts (P07/P05); during bootstrap
  the human records them on GitHub.
- `ScopeRequest{request_id, task_id, add_paths[], resources[], reason, status}`; approval
  updates the revision and reservations without releasing the lease (plan section 6).
- The plan file is an input. Approved revisions become authoritative only in state (P05);
  a mirrored repository file must not compete (plan section 5).

## 6. Fixture expectations (P03 acceptance)

- A valid plan fixture compiles **byte-identically** across runs and hosts.
- Invalid fixtures fail with actionable messages: missing criteria, duplicate criterion IDs,
  cycles, unresolved prerequisites, source/revision drift, unrestricted scope paths.
- Independent milestone branches remain eligible (A03); readiness explanations follow the
  Beads-style shape (`upstream-surfaces.md` §3) with extra reasons for missing completion
  evidence, resources, Needs human and review budget.
- A compatibility fixture: a packet produced by `bootstrap/core.review_packet` loads and
  keeps `mode: bootstrap_advisory` and its manual provenance.
- Weave reuse candidates for this work (copying requires README Q13/Q14 and the NOTICE scope
  request): `model.py:137-160` digests, `scheduler.py` graph and selection,
  `schema.py` fail-closed validator (`weave-inventory.md` §E).
