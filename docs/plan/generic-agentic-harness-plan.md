# Generic agentic development harness — review plan

**Revision 5 · 29 October 2026 · final M0 review amendments incorporated**

This document supersedes revision 4 and the earlier service-first plan. The latest external review approves M0 and recommends the task split and operational clarifications incorporated here. This records the review disposition, not a claim that implementation has started. It is a plan for implementation, not a claim that the proposed software or its guarantees already exist. No repository, Project, permissions, or deployment was modified for this revision. Commands below are proposed interfaces.

## 1. Recommendation and intended outcome

Build a small, reusable extension of Weave around GitHub Issues, Projects, and pull requests. Its distinctive purpose is to turn an approved plan into bounded, evidence-backed work: dependency-aware task selection, independently reviewed candidates, explicit human decisions, and architecture-aware planning.

Reuse existing execution, isolation, and publication components wherever they meet the contract. Keep the reusable Weave logic in Python. Do not begin by building a hosted coordination platform, rewriting the harness in another language, or assembling several overlapping schedulers.

The initial deployment should require only GitHub plus machines on which workers run. A local trusted supervisor launches isolated developers or reviewers and runs the deterministic reducer, committing accepted transitions to shared Git state with a compare-and-swap (CAS) condition. There is no custom public server or inbound worker port in the default design. Actions supplies trusted CI evidence and optional human-command ingestion; it is outside the normal claim/renewal path. An Actions-hosted reducer is an explicitly selected fallback, not an additional authority.

First evaluate gh-aw's queue and safe-output implementation as the shared coordination/publication backend. If its supported interfaces cannot accommodate external workers and Weave's evidence contract, implement a narrow Git-state adapter using conditional branch updates. Choose one implementation after the time-boxed spike and explicit rejection criteria in P02a; never run two schedulers as coequal authorities.

The first usable release supports:

- One repository and one GitHub Project, with an approved task and milestone dependency graph.
- Two developer workers and one independently operated reviewer, including a cross-vendor development/review combination.
- Containerized task execution, with an optional microVM backend on supported hosts.
- Atomic accepted ownership, dependency gating, durable recovery, bounded review rounds, and human merge.
- GitHub questions and answers, plus a terminal interface to the same authorized commands.
- Architecture-aware plan linting and one integration with an existing architecture checker.
- A template for new projects and an additive installer for existing repositories.

Explicitly defer cross-repository scheduling, automatic merge, high availability, enterprise dashboards, autonomous architecture changes, and a signed architecture-governance service. These are not prerequisites for a useful pilot.

## 2. Evidence and reuse decisions

### Weave baseline

The earlier assessment inspected commit `d8010aec6746bbdcc54b21801c537d28917c0533` and reported 89 passing focused controller tests. Those tests were not rerun for this revision and do not validate the proposed distributed protocol or sandbox.

The revision-3 API check resolved Weave `main` to `e7c3f3cab1e25994b96a948cbe27c96bb061d5a8`. The `tools/weave_workflow/` and `docs/development/` directories are present. The reviewer's contrary directory observation does not match that snapshot; its cause is unknown. [S1]

Retain Weave's task packets, acceptance-criterion digests, deterministic scheduling, transition validation, event/outbox concepts, documentation-impact checks, and demonstrated Codex review adapter. Its published claims already contain expiry and coordinator-host metadata. The missing guarantee is atomic ownership across independent hosts, not the concept of a lease.

Issue #6 supplies three concrete requirements: amend scope without discarding an attempt; distinguish independently run checks from developer-supplied evidence; preserve nuanced human conversations as durable decisions. Its third review passed after two change requests, but full checks could not run in the review sandbox. That is evidence of a useful review loop, not evidence of complete independent verification. [S2]

### What to adopt, adapt, or leave out

| Reference | Verified relevance | Decision for this plan |
| --- | --- | --- |
| OpenAI Symphony | Tracker-driven execution, per-issue workspace, `WORKFLOW.md`, concurrency settings, blocker metadata, and in-memory orchestration state. | Adopt compatible vocabulary and evaluate its runner as an optional adapter. Do not assume its local claimed set provides cross-host exclusivity. Avoid a mandatory runtime migration. [S3] |
| GitHub Agentic Workflows | Compiled Actions workflows and validated safe outputs; current queue documentation also covers dependency graphs, Git publication, and recovery. Its release checklist explicitly distinguishes implementation from live verification. | First candidate for reuse, subject to the M0 tests. The external review's “no dependency gating” characterization is no longer a reliable basis for design. [S4–S6] |
| Beads | Dependency-aware readiness and claims; the current project uses Dolt, with embedded and server modes. | Borrow readiness and explanation UX. Do not add a second issue database to the pilot, or treat Git synchronization as proof of distributed claim safety. [S7] |
| Linear agent APIs | Human ownership distinct from agent delegation, typed activity, waiting for input, and stop signals. Current documentation lists six session states, including `stale`. | Adopt these concepts in GitHub issue summaries and the internal protocol. This is a Weave convention, not a native GitHub session API. [S8] |
| Docker Sandboxes | Current documentation describes microVM isolation, private clones, network policy, and credential proxying. Platform requirements apply. | Evaluate as an optional runtime; retain ordinary OCI containers for portability. Pin and test actual settings rather than relying on product defaults. [S9] |
| Hosted coding/review agents | Potential execution and supplemental-review endpoints. | Add only when an adapter can supply the required identity, candidate, evidence, cancellation, and licensing information. Availability is not contract conformance. |

The external comparison is useful direction, not proof that no competitor offers evidence-bound reviews or architecture checks. This plan makes no exclusivity claim. Gas Town and Fletch remain design references rather than required dependencies; the proposed host-side publication boundary stands on its own acceptance tests.

**Version discipline:** repository snapshots observed during revision 3 were Symphony `be10a1b79df723d6d7612b5651c8522704dafb2e`, gh-aw `28f2101d8af447fdb90ffd70dd2579e4ad64a21c`, and Beads `e226083653b893998614df4225f73b6688ca9166`. Documentation links may change independently. M0 must select exact deployable versions, licenses, schemas, and interfaces; these observations are not a validated dependency lockfile.

## 3. Scope, assumptions, and non-negotiable contracts

The project owner supplies an approved plan. Each executable task has context, deliverables, explicit exclusions, acceptance criteria, dependencies, milestone membership, and appropriate verification. The harness validates structure and exposes gaps; it cannot prove that a product plan is correct or that all hidden dependencies have been identified.

Trust assumptions: maintainers, trusted controller code, and the host supervisor are trusted. Repository code, candidate changes, model output, issue prose, and downloaded packages can be unsafe. Independent reviewers do not inherit the developer's session, writable environment, or authority. A trusted maintainer can still override repository protections; such an override is outside the automation guarantee and must be visible.

Required contracts:

1. At most one accepted development owner and one accepted review owner for a task/job at a time.
2. A task is claimable only when its approved prerequisites have accepted completion evidence and its required resources are available.
3. A stale worker cannot have new submissions, verdicts, or completion events accepted under an old claim generation.
4. Review applies to an exact candidate and an exact task revision, not a moving branch name.
5. Review budgets belong to the task and survive worker changes, restarts, branches, and scope amendments.
6. A timeout, unavailable checker, or unverified test report cannot become PASS.
7. Done means the required deliverable is integrated and its completion evidence accepted. Closing an issue alone is insufficient.
8. Human commands are authenticated, correlated, and auditable. Ordinary discussion never silently changes policy.
9. The board and issue summaries are recoverable projections of accepted state, not locks.
10. No model process receives merge authority or unrestricted controller credentials.

**Exclusivity limit:** an accepted-owner protocol cannot guarantee that a partitioned old process stops computing. The supervisor must stop on lost authorization, and publication must be fenced. If the project requires proof that no overlapping physical execution exists, do not reassign until termination is confirmed; accept reduced availability during partitions. Tasks with external side effects use this stricter policy or remain human-operated.

## 4. Minimal architecture and authority

| Component | Responsibility | Authority |
| --- | --- | --- |
| Plan/packet compiler | Validate plan graph, build immutable task and review inputs, map architecture rules. | Read approved definitions; propose revisions. |
| Trusted controller/publisher | Authenticate commands, apply deterministic transitions, maintain shared state, project to GitHub. | Scoped state, issue, Project, candidate-publication, and check permissions. |
| Worker supervisor | Authenticate an enrolled instance, run the trusted reducer/publisher by default, launch/stop sandbox, checkpoint artifacts. | Host-held state/publication credentials; trusted code enforces task/role policy. No merge authority; credentials stay outside model processes. |
| Developer/reviewer sandbox | Implement a task or independently inspect a candidate; run permitted tools. | Local workspace and approved model/tool access; emit structured proposals. |
| Trusted CI and human integrator | Execute required verification and authorize integration. | CI evidence identity; merge authority remains with the human for the pilot. |

**Default placement:** each enrolled, trusted supervisor runs the same pinned reducer locally and publishes transitions using the selected backend's conditional update. Shared state is the authority; local processes are concurrent clients, not separate ledgers. CAS resolves competing valid transitions; the reducer must still validate authorization, prerequisites, scope, and evidence. Supervisors make outbound GitHub requests and poll authorized issue commands. Optional Actions ingestion may submit the same durable command through the same reducer contract.

State-writing supervisor credentials are deliberately part of the trusted computing base. GitHub does not enforce per-task reducer policy inside a state branch; a compromised supervisor could bypass that policy. Use distinct revocable credentials, keep them out of model sandboxes, and pin the reducer/configuration. If a deployment cannot trust each supervisor with this authority, choose the Actions-hosted reducer fallback and accept its latency/cost. Both placements use one protocol and one authoritative state; switching placement is an explicit controlled operation. Do not introduce a second queue or silently weaken role checks.

Actor and role come from authenticated transport plus enrollment, never a model-supplied `worker_id` field. Duplicate command ingestion by several supervisors is safe only through durable command IDs and conditional publication. A failed upstream external-worker test selects the narrow adapter; it is not bypassed by hiding a second authority behind Actions.

Adopt gh-aw's safe-output pattern: the agent proposes a typed action; trusted code validates and applies it. If its actual handlers are reused, pin their schemas and supported versions. Otherwise define a small local schema and call it an adaptation, not gh-aw compatibility. Validate repository, issue, claim generation, resource scope, candidate SHA, command ID, and policy revision. Sanitizing text alone does not authorize an action.

Publication runs without executing candidate scripts, Git hooks, credential helpers, or filters from the sandbox. Candidate material is imported into a clean, controlled Git environment. Separate identities and jobs perform candidate publication and trusted verification. Credential isolation is insufficient if the model can invoke a proxy that grants arbitrary writes.

### Shared state and atomic claims

Preferred storage is one branch with append-only commit history, such as `harness/state`. For the narrow adapter, use per-task current state in `state/tasks/<id>.json`, a compact versioned index, separately addressable resource reservations, bounded event records, durable command receipts, and pending external effects. Claims, questions, and review counts live with the corresponding task or job. Logs and large artifacts live elsewhere, referenced by digest. Issue and board content cannot reconstruct all authority by themselves.

A normal transition updates the affected task plus relevant index/resource/receipt/event files in one commit. Do not promise exactly two files: multi-task or shared-resource transitions must atomically update every affected record. Avoid one ever-growing JSONL file or a global index containing full task histories. File partitioning reduces payload size; the branch-level CAS remains the serialization point. Keep the current-state files sufficient for ordinary reads, and retain deduplication receipts for the full supported command-retry horizon.

Create periodic verified snapshot commits with the schema/policy version, covered history tip, current state, and integrity digests. Startup may load a trusted verified snapshot and replay its bounded suffix; test state equivalence against full replay. A snapshot does not delete Git history or automatically bound Git object transfer. Measure both replay and fetch costs, preserve audit history, and fail closed on an invalid snapshot. If gh-aw is adopted, use its supported storage/checkpoint protocol instead of imposing this local layout or weakening its history-verification requirements.

**History compaction** is a named, explicitly authorized epoch-change operation, deferred beyond the pilot: apply cutover-style pause/fence/drain rules, archive the exact old branch tip under a protected retained tag, verify a complete snapshot, and start fresh history under a new authority epoch while preserving review counts, command receipts, pending effects, and audit links; reject old-epoch writes and use a separate authorized transition rather than an ordinary branch rewind. An adopted backend must support equivalent verified semantics before compaction is enabled.

First attempt to use an existing conforming backend. If a narrow adapter is needed, apply each transition as one conditional branch update:

1. Read authoritative state and its head SHA.
2. Validate the authenticated request, current task revision, dependencies, resources, and existing claim.
3. Compute the complete transition, including claim generation and pending projection events.
4. Commit only if the branch still has the observed head.
5. On conflict, reread and recompute; do not blindly rebase the previous decision.
6. On lost acknowledgment, search the committed state for the stable command ID before retrying.

GitHub's REST ref update exposes `sha` and `force`, not an expected-old-SHA parameter. Its 422 response is not uniquely a contention result. A suitable documented alternative is `createCommitOnBranch` with `expectedHeadOid`; an explicit expected-value Git push is another candidate. Validate the exact chosen transport in live races. Do not combine a Git-only upstream queue protocol with an incompatible GraphQL transport and call it conforming. [S10]

A single state commit makes eligibility, ownership, and resource reservations atomic within one repository. Separate claim refs plus a global lease introduce extra recovery states and are not the default. Scale limits are measured before changing this architecture.

Leases record task/job, authenticated owner, generation, approved revision, and expiry. For the narrow-adapter pilot, start with a configurable eight-hour lease and rare explicit renewals, evaluated in P02a for recovery latency and cost. This is a proposed operating default, not a newly verified claim about current Weave settings. No heartbeat generates a state commit or renews authority: local heartbeats/watchdogs are diagnostic; only accepted renewals change expiry. Early release, stop, and completed work still commit immediately.

Long leases must not delay stop detection. Supervisors separately poll shared authority and human commands at a bounded interval, stop before local lease expiry with a skew margin, and stop active execution when authority cannot be refreshed within the configured offline grace period. Record these intervals and connected-stop targets in P02a. Use trusted host clocks with measured skew limits; a supervisor outside those limits cannot grant or renew. Restart reconstructs durable leases, not heartbeat memory. If an adopted backend has different supported lease semantics, document and test them rather than pretending it implements this default.

Expiry permits fencing; it does not establish that a remote process or external effect has ended. Physical capacity reservations must not be released on a mere timeout when execution remains uncertain. Reclaim uncertain work only under the section-3 exclusivity policy.

Git commits and external GitHub effects are not one transaction. Persist an intent first, publish using an idempotency key or immutable generation-specific target, then reconcile/read back the effect. Recheck authority before acceptance. A delayed request may create an orphan candidate or stale comment; it must never advance authoritative state or satisfy completion. Do not promise exactly-once network delivery.

Protect the state branch against deletion, rewind, and model/sandbox writes; explicitly allow only the selected trusted supervisor or Actions publisher identities. If enrollment permissions or the account's available protections cannot enforce the selected profile, setup must report the exact gap and disable autonomous execution for that profile. Read-only plan linting can still work.

## 5. Planning contract and architecture guidance

Use one authoritative approved task definition, materialized into immutable revisions. GitHub issue editing proposes a revision; acceptance creates a new packet and digest. A mirrored repository file must not become a competing authority.

Minimum task fields:

| Field | Required content |
| --- | --- |
| Identity | Stable task/issue ID, milestone, human owner, plan revision. |
| Context | Goal, relevant existing behavior, links to decisions and prerequisite outputs. |
| Scope | Deliverables, exclusions, allowed paths, shared interfaces/resources, expected documentation changes. |
| Dependencies | Explicit blocking task IDs and milestone gates; separate nonblocking references. |
| Acceptance | Stable criterion IDs, observable outcomes, test/check or human-evidence method. |
| Architecture | Applicable blueprint/ADR/rule IDs, or justified not-applicable result. |
| Execution | Required capabilities/toolchain, risk class, time/cost budget, review limit. |

Readiness checks detect missing fields, ambiguous criteria, cycles, unresolved references, conflicting scope, and unsupported architecture rules. A semantic model review may suggest improvements, but cannot authorize its own plan changes. Tasks with missing critical information remain Todo with an actionable explanation.

Milestones form a DAG; numeric ordering is not an implicit global barrier. A milestone gate depends on explicitly required deliverables. Tasks on independent milestone branches may run concurrently. Cross-repository prerequisites are outside the pilot; missing or inaccessible prerequisites fail closed.

### AAB contribution

Treat the Agentic Architectural Blueprints material as an input to formalize, not an already implemented or universally established compliance standard. Put the authorized, versioned source in the repository before using it as a shared baseline; a private chat/library URL is not a portable reference. The full original AAB source has not been revalidated as part of this revision.

Start with **plan conformance**, before execution infrastructure is complete:

- Map task scope and acceptance criteria to applicable components, interfaces, quality attributes, and decisions.
- Flag contradictory patterns, missing migration/rollback tasks, omitted verification, and dependencies inconsistent with the proposed architecture.
- Explain candidate architectural patterns and their tradeoffs for the project's constraints. Preserve existing architecture unless an authorized decision changes it.
- Report `satisfied`, `violated`, `not_applicable`, or `unverified`, with evidence and rule coverage. Passing structural lint is not architectural approval.

For implementation conformance, configure established tools: import-linter for Python, dependency-cruiser for JS/TS, or ArchUnit for JVM projects. The pilot integrates one, selected by the pilot repository. Do not build a new language dependency analyzer. [S11]

Each mapping documents source/target selectors, direct versus transitive semantics, quantifiers, exclusions, generated code, and unsupported cases. Unmatched selectors and a missing checker cannot produce a vacuous PASS. “Required dependency” is not assumed to mean the same thing across tools. Human review covers properties such as resilience or operational boundaries that static import rules cannot establish.

Approval records bind plan, architecture baseline, and verification policy revisions. Changing any relevant baseline invalidates affected evidence. Defer cryptographic signing infrastructure; do not advertise a stronger governed profile until its independent authorization and evidence requirements exist.

## 6. Board, task lifecycle, and resource policy

Default columns are **Todo → Ready for Development → In Progress → In Review → Done**. Ready is both the initial executable queue and the rework queue. A four-column compatibility view may combine Todo and Ready, but eligibility remains explicit internally.

Keep at most three extra default fields: `Review` (for example, `2/3`), `Needs human`, and `Blocked by`. Keep the accountable human as the GitHub assignee. Show the developer/reviewer delegate in a maintained issue summary and event timeline; offer a Delegate field only as an optional view customization.

| Event | Result and guard |
| --- | --- |
| Plan approved and prerequisites complete | Todo becomes Ready. |
| Development claim accepted | Ready becomes In Progress; generation and scope recorded. |
| Candidate accepted for review | Freeze candidate packet; release development ownership; In Review. |
| Reviewer requests changes, budget remains | Record findings; return to Ready with rework reason and prior candidate. |
| Review passes | Remain In Review, marked ready for human integration. |
| Required checks and integration confirmed | Done; record merge/deliverable evidence; unlock dependents. |
| Human decision required or budget exhausted | Preserve lifecycle stage; set Needs human and make task unclaimable. |
| Dependency reopened, plan changed, or evidence invalidated | Recompute affected readiness; fence incompatible work and require revalidation. |

For non-code tasks, define the accepted deliverable location and explicit human acceptance; never infer completion from a model's summary. Issue closure without merge/accepted deliverable is reconciled as a discrepancy.

Reservations are configurable. Default ordinary path reservations last through active development; release them during review or a prolonged human wait. For tasks declaring hard shared resources—schema migrations, public API contracts, deployment state—the default is **retain through integration**, including review and human waits. Releasing or suspending such a reservation requires an explicit authorized policy decision and safe reacquisition; ordinary-path release must not implicitly release a hard resource. A released reservation must be reacquired before rework. Generated files should be regenerated from their authoritative sources; reserve the source contract when appropriate rather than serializing every task on a lockfile.

Before integration, rebase or construct the intended merge result and rerun affected checks. Concurrent work may still conflict semantically even when paths differ. Revalidation is essential and does not justify omitting declared dependencies.

Provide `harness scope request TASK --add PATH --reason ...`. Authorized approval atomically updates the task revision and reservations without releasing the current lease or discarding commits. If the new scope conflicts, pause until resolved. Preserve review history and invalidate evidence bound to the old revision. Controller auto-approval is limited to explicitly preauthorized scope rules; arbitrary expansion requires a human.

## 7. Workers, containers, credentials, and recovery

Ship a pinned harness/supervisor distribution plus agent-specific runtime images. Project toolchains layer on top through approved image builds or devcontainer configuration. Avoid one image containing every provider and language. Reuse devcontainer definitions where safe, but review host initialization commands, mounts, privileged flags, capabilities, and Docker socket access before execution. A repository's devcontainer is executable configuration, not inherently trusted. [S12]

A container is the execution unit; an enrolled running instance is the worker identity. Enrollment binds an authenticated principal, role, repository, runtime capabilities, and revocation policy. Starting several copies of an image does not create safe ownership without the shared protocol.

Ordinary OCI profile:

- Non-root execution, resource limits, restricted capabilities and host mounts; rootless runtime where supported.
- A private checkout and writable workspace/tmp; read-only root filesystem where the toolchain permits it.
- No host Docker socket, home directory, SSH agent, controller token, or merge credential.
- Externally enforced egress policy, including direct connections and DNS/IPv6 bypasses, not just proxy environment variables.
- Separate writable caches by trust domain; developer-controlled caches never become trusted review/CI inputs.

Docker provides useful isolation while sharing a kernel. A microVM runtime can strengthen that boundary, but requires supported hosts and its own tested mount, credential, network, and cancellation behavior. Docker Sandboxes is an implementation candidate, not an assumed drop-in replacement on every machine. Its documentation has differing descriptions of shared-skill defaults, reinforcing the need to set and inspect actual policy explicitly. Disable unneeded skills sharing and SSH forwarding. [S9, S13]

Read-only mounted credentials remain readable. Keep GitHub write credentials outside the agent environment; use narrow authenticated supervisor operations. Where feasible, use a model-provider credential proxy with destination and operation limits. If an adapter requires a credential inside the sandbox, document that exposure and use a scoped, revocable credential. Never bake secrets into images. A domain allowlist reduces exposure but does not prevent misuse of attacker-controlled repositories or endpoints on allowed services.

GitHub tokens are not intrinsically scoped to `agent/*` branches. Repository rules and a trusted publisher must enforce actual authority; main-branch protection alone does not isolate workers from each other's candidates. [S14]

Developers get a private environment per task lease, resumable while valid. Reviewers get a fresh clone, session, and writable scratch per review job. Matching CI image digests improve reproducibility but do not establish evidence trust; CI identity, workflow revision, source SHA, and execution result must also be verified.

Checkpoint source through the trusted publisher, together with task revision, claim generation, candidate SHA, question state, findings, and artifact references. Only acknowledged durable checkpoints are recoverable after host loss. Unpushed edits may be lost. Resume by reconstructing the packet and checkout, not by copying another worker's secret-bearing session.

Interactive operation remains supported: an operator may attach to a developer session or use `harness answer`. Containers do not require fully headless use. Durable decisions still go through GitHub so another environment can continue the work.

## 8. Independent review and integration contract

### Evidence modes and milestone boundary

**M2: `unverified_pilot`.** This mode demonstrates scheduling and an independent review/rework loop before P09 supplies trusted-CI provenance. Developer-supplied checks remain supplied evidence; independently run reviewer checks retain their actual provenance. Missing trusted verification produces `UNVERIFIED`, never a synthetic PASS. A human may make a separately recorded acceptance decision binding the exact candidate and task revision, listing unverified criteria and the reason for proceeding. Only that explicit decision plus confirmed integration/accepted deliverable can move a pilot task to Done. It does not rewrite the verdict or claim the M3 guarantee. Issue closure, generic approval prose, or a green untrusted test is insufficient. Mode and manual acceptance provenance are visible in the packet, issue summary, and completion record. Run this demonstration in disposable/pilot-scoped work; the live Weave cutover waits until P12.

**M3 onward: `trusted_ci`.** P09 enables the required evidence gates below. No pilot exception silently carries over: unfinished pilot tasks must be revalidated under the new policy; retained historical completions remain labeled with their actual evidence mode. P12 uses `trusted_ci`, not `unverified_pilot`.

**Dependency rule:** a Done task with a valid, explicitly authorized `unverified_pilot` acceptance and confirmed integration counts as completion evidence for dependents, including M3 tasks; readiness records the acceptance ID and inherited evidence mode. It does not convert the predecessor verdict into PASS or relax the dependent task's own `trusted_ci` checks. Missing acceptance, changed requirements/candidate identity, or revoked acceptance blocks affected dependents. A project requiring trusted evidence on every dependency edge must declare that stricter policy and the necessary revalidation explicitly; switching modes must not silently block or unblock historical pilot work.

The logical ownership, isolation, authorization, and review-budget contracts apply in both modes. P08 can reject a candidate and test rework in M2; missing CI evidence never authorizes a PASS.

### Review execution

A reviewer polls accepted pending review jobs; the developer does not call a reviewer and wait synchronously. Review jobs are claimed with the same ownership discipline. Eligibility requires the proper role and a reviewer session distinct from the developer. Cross-vendor review is the pilot default where credentials and provider support permit it; different vendors alone do not guarantee independence.

The review packet contains:

- Task ID, task revision, acceptance criteria and per-criterion digests.
- Candidate head SHA, base SHA, intended integration target, diff/artifact digest.
- Architecture and verification-policy revisions.
- Prior findings, their disposition, accumulated round count, and remaining budget.
- Developer evidence clearly labeled as supplied, with trusted CI evidence separately identified.

A verdict includes `PASS`, `CHANGES_REQUESTED`, or `UNVERIFIED`; criterion-level findings; reviewer identity/provider/tool version; packet identifiers; and per-check evidence. Infrastructure failure is a job outcome, not a quality verdict. `independently_executed` is recorded per check, together with executor identity, environment digest, command/check ID, exit status, source SHA, log/artifact reference, and provenance. A boolean asserted by the developer is not verification.

In `trusted_ci` mode, trusted controller code validates provenance. Required executable criteria need successful evidence from the configured trusted CI identity and approved verification workflow. The workflow must not allow candidate code to alter its own gate or expose verification credentials. Reviewer execution provides additional independent evidence; inability to run required checks yields UNVERIFIED unless an authorized policy explicitly accepts suitable trusted CI evidence. Non-executable criteria require the designated reviewer or human decision.

**Default budget:** three completed quality rounds per task. At most one aggregate round is active for a candidate/revision. Reserve a round slot on dispatch; finalize and increment exactly once when an accepted PASS or CHANGES_REQUESTED is recorded. Multiple configured reviewers contribute to that aggregate round under a fixed aggregation policy. Infrastructure retries and UNVERIFIED results have separate bounded retry/time/cost budgets and cannot loop indefinitely. Rejected or duplicate stale submissions do not consume another quality round. Previously completed rounds remain counted after invalidation, reassignment, or a new branch. A human can raise the budget with a reason; the history is never reset silently.

Supplemental hosted reviews are signals until an adapter satisfies this contract. Do not equate a relayed model PASS with a GitHub approval, or count each bot comment as a new round.

In `trusted_ci` mode, a human merges only after the required evidence gate is green; the M2-only manual acceptance path is defined above. Changed task requirements, candidate SHA, or relevant architecture policy invalidate the corresponding verdict. Base changes require integration checks and, when the effective candidate changes, renewed review. Completion records the actual merge/deliverable identity. Trusted reconciliation handles a merge notification lost during an outage.

## 9. Human input, stop, and notification behavior

Session status is separate from task status: `pending`, `active`, `awaiting_input`, `error`, `complete`, or `stale`. These concepts borrow from Linear; the harness additionally records explicit stop-request and stop-confirmation events. [S8]

A question has a stable ID, task revision, requesting session, reason, relevant alternatives, impact of delay, and designated human. Post a concise issue comment, mention the accountable person, and link the relevant context. GitHub notification delivery depends on account settings; the harness can confirm publication, not guarantee an inbox notification was read.

Proposed commands:

```text
/harness answer Q-17 <decision and rationale>
/harness scope approve REQUEST-9
/harness stop TASK-42
/harness resume TASK-42
/harness review-limit TASK-42 5 --reason <reason>

harness answer Q-17 --file decision.md
```

The terminal command posts the same authorized decision to the issue. Preserve the author, timestamp, question revision, and relevant conversational context. Never infer approval from unrelated prose or let model output masquerade as a maintainer command. Deduplicate delivery and reject replies to superseded questions until explicitly reconciled. Ordinary issue comments can discuss a question; a correlated authorized command resolves it.

On an accepted stop request, revoke publication authority immediately in shared state and request supervisor termination. The supervisor stops the process and confirms its last checkpoint. Report `stop_requested` until termination is observed; do not claim a partitioned worker has stopped. Set a measurable connected-worker stop target in M0 and keep disconnected execution fenced. Resume is an explicit authorized operation.

While awaiting input, the default is to checkpoint, stop active model work, and release ordinary path reservations. Retain declared hard resource reservations by default; suspend them only through an explicit authorized policy decision. Record whether the task is claimable; a paused question is never silently bypassed by reassignment.

## 10. Onboarding and operating model

Offer two entry points: create from a GitHub template, or run an additive installer in an existing repository. Both produce versioned configuration and a reviewable installation change, preserving existing AGENTS.md, devcontainers, CI, milestones, and issues.

The wizard asks for repository/Project, human owner, developer and reviewer providers, runtime choice, verification commands, architecture source, review budget, and explicit dependency mapping. It detects existing settings before asking. It configures the five statuses and three optional fields, approved workflows, state storage, and image pins. Projects permissions are checked separately from repository permissions. Provider login or API-key setup is guided per adapter; do not assume every provider supports the same unattended authentication.

`harness init` emits the exact credential specification from P01's versioned permission matrix for the chosen account, backend, and role: supported token/App type, repository and Project scope, API permission names/access levels, credential holder, expiry/revocation procedure, and separately required ruleset/publisher restrictions for the state branch and `agent/*` candidates. Branch patterns are enforcement configuration, not fictitious token permissions. Distinguish setup privileges from runtime privileges and generate separate credentials where one credential type cannot cover the required Project operations. Output contains no secret values; `doctor` checks the resulting access without granting it.

Proposed operator flow:

```text
harness init
harness doctor
harness plan check
harness worker start --role developer --provider <configured-provider>
harness worker start --role reviewer --provider <configured-provider>
```

Workers on another machine use the same configuration and their own enrollment. A user should not need to install every agent CLI globally. Setup still requires supported sandbox software, GitHub authorization, and provider access; “one command” means guided setup, not zero prerequisites.

`doctor` verifies permissions, branch protections, writable scratch, sandbox restrictions, provider access, Project mapping, plan readiness, and the actual selected backend. It distinguishes a missing prerequisite from a failed security guarantee. It must not silently fall back to unsandboxed execution or advisory ownership.

Polling is the portable baseline, including personal Projects. Use eligible webhooks as latency improvements, not the only correctness mechanism. Scheduled Actions may be delayed or dropped; recovery also runs on worker requests and manual reconciliation. The default supervisor path does not depend on scheduled Actions for claims or renewals. Bound command/authority polling, local heartbeat frequency, rare lease-renewal writes, and API concurrency. [S15]

**Idle invariant:** without a running supervisor or an explicitly enabled reducer host, no authoritative transition occurs: a posted answer remains pending until processed, and board projections may lag. `harness reconcile` runs an authorized one-shot reducer/reconciler to ingest pending commands and repair projections; it does not launch coding work. An optional scheduled Actions job may refresh projections from accepted state using projection-only credentials, but must not accept answers, renew/reclaim leases, acknowledge authoritative outbox state, or perform any other authority transition. It cannot substitute for a running supervisor.

Provide pause-all, status/explain, reconcile, checkpoint export, credential revocation, and upgrade/rollback documentation. Pin schema versions; old workers refuse unsupported state rather than corrupting it. The pilot does not require a general migration framework. Logs and retained history have explicit limits; no secrets or raw model credentials enter issue comments or state commits.

## 11. Delivery plan and issue-ready tasks

Five milestones contain thirteen tasks, with the former P02 split into P02a and P02b. Every task below defines context, scope, dependencies, and acceptance. Implementation issues should carry these definitions plus the chosen repository paths and owner. Estimates are rough engineering effort, not promised elapsed time or assumptions about agent speed.

| Milestone | Purpose | Exit condition |
| --- | --- | --- |
| M0 — Choose the smallest viable foundation | Verify reuse and live coordination/runtime assumptions. | Backend/runtime decision supported by experiments; failed guarantees explicitly block rollout. |
| M1 — Approve executable plans | Package the plan, task, review, and architecture contracts. | Invalid plans are explainable; a valid pilot plan compiles reproducibly. |
| M2 — Complete one independent review loop | Wire ownership, sandboxed development, human input, and pull review in `unverified_pilot` mode. | Two developers and an independent reviewer complete a dependency/rework scenario; Done requires recorded manual acceptance and integration, with no trusted-CI claim. |
| M3 — Verify and onboard | Enforce trusted evidence and install into a second project. | Template and existing-repo onboarding work without source-specific patches. |
| M4 — Qualify the pilot | Exercise fault recovery and real operations. | Required adversarial scenarios pass and operating limits are documented. |

### P01 — Reuse and authority decision (M0)

**Context:** recent reference implementations overlap the proposed controller. **Dependencies:** none. **Scope:** pin Weave and candidate upstream revisions; inspect licenses, gh-aw supported queue/safe-output surfaces, external-worker binding, Symphony runner boundary, runtime support, and required GitHub identities. Define internal interfaces and a versioned, machine-readable supervisor-hosted reducer permission matrix, including the Actions-hosted fallback and separate setup/runtime privileges, as the source for the credential specification emitted by `harness init`. Inventory the maintained Weave code removable through adoption versus required adapter code. Exclude a framework rewrite.

**Acceptance:** a comparison maps each required contract to reused code, adapter work, or a demonstrated gap; one preferred backend and fallback are named; no two authorities are proposed for the same state. Existing Weave behavior and migration boundaries are enumerated.

### P02a — Coordination and backend-selection spike (M0)

**Context:** documentation alone does not establish coordination guarantees. **Dependencies:** P01. **Scope:** start the gh-aw fit assessment and narrow-adapter tests on day one, using separate disposable authority branches/repositories and the same conformance fixtures. Default to two trusted supervisor-hosted reducers. Exercise A01, A04, A05, A07, and the authority-revocation side of A17: competing claims, renewal/takeover, ambiguous writes, disconnected workers, and rejection of publication after stop. Check external-worker authentication, CAS behavior, clock skew, rare renewals, and snapshot/replay equivalence. Use fixture processes; runtime containment and physical termination belong to P02b. Parallel experiments are not simultaneous production authorities.

**gh-aw rejection criteria — decide before integrating it:**

1. A process outside Actions must hold and exercise a Claim through a supported authenticated path, without another ownership ledger or a fabricated Actions identity. Failure selects the narrow adapter.
2. The protocol, implementation, schemas, and necessary runtime dependencies must be pinnable to a reproducible compatible version, with unsupported versions rejected. Reliance on a moving protocol or unpublished interface selects the narrow adapter.
3. Adoption must remove more hand-maintained Weave production coordination/publication code than the new adapter/glue adds, and reduce maintained responsibilities. Record the files, non-generated line counts, retained tests, and responsibilities; do not game the comparison by deleting tests or ignoring integration code. If the net reduction is absent or cannot be demonstrated within the spike, select the narrow adapter.

Time-box the gh-aw fit assessment to three engineer-days within P02a; any failed criterion or unresolved result at the deadline means no-go for that backend. Narrow-adapter validation runs concurrently from day one and does not wait for that decision. Select only a backend that passes the required tests; if neither qualifies, pause dependent implementation and publish the concrete gap rather than silently extending the spike or weakening a guarantee. Actions-hosted placement remains a separately justified fallback for deployments that cannot trust state-writing supervisors; it does not waive the external-worker or single-authority criteria.

**Acceptance:** A01/A04/A05/A07 and the authority-fencing portion of A17 pass for the selected backend. Report each gh-aw reuse criterion as pass/fail with evidence, alongside narrow-adapter results, latency, request volume, clock bounds, authority-poll/offline-grace intervals, renewal cadence, snapshot/replay/fetch costs, and authenticated identities. Select one backend or report no-go. M0 requires its integration with the selected P02b runtime to demonstrate both fencing and confirmed termination for A17; fixture success alone is insufficient. No custom daemon is built merely because the spike is inconvenient.

### P02b — Runtime isolation and reviewer-launch spike (M0)

**Context:** sandbox containment and process control require a separate host test rig. **Dependencies:** P01. **Scope:** run alongside P02a, using the P01 execution/stop interface and a fixture authority. Exercise A19, writable reviewer scratch, credential separation, actual egress enforcement, process termination, and the runtime side of A07/A17. Establish the small reviewer-launch interface/fixture that P08 can use without P06. Keep candidate code and model processes outside the trusted supervisor credential boundary.

**Acceptance:** the selected runtime blocks the tested host/credential/network access paths; the reviewer can execute checks in writable scratch; connected stop terminates execution within the documented target; partition tests report uncertainty honestly. Record host requirements and supported configurations. Join with P02a before M0 exit to verify that authority revocation and physical-stop acknowledgment remain distinct and work end to end. Runtime failures block P06/P08, not the independent backend assessment.

### P03 — Portable packets and plan validator (M1)

**Context:** plan quality is a prerequisite, independent of worker infrastructure. **Dependencies:** P01. **Scope:** extract Python models and graph checks; canonical task/criterion digests; milestone DAG; approved revision handling; actionable readiness explanations; task and review schemas. Exclude automatic product planning.

**Acceptance:** valid fixtures compile deterministically; missing criteria, cycles, unresolved prerequisites, and revision drift fail clearly; independent milestone branches remain eligible. A documented schema fixture supports downstream work without overlapping ownership of the model module.

### P04 — Architecture-aware plan checks (M1)

**Context:** valuable architecture guidance should arrive before the full runner. **Dependencies:** P03. **Scope:** portable authorized AAB/ADR baseline, rule applicability, criterion mapping, plan lint, and configuration export for one existing checker. Exclude a new analyzer and signed-governance service.

**Acceptance:** fixtures expose a contradictory task, missing architectural verification, unsupported rule, and unmatched selector; none silently pass. A compliant plan includes explainable rule-to-task mappings. One project-specific checker configuration has known-good and known-bad examples.

### P05 — Shared state, commands, and fencing adapter (M2)

**Context:** all later actions need one authority. **Dependencies:** P02a, P03. **Scope:** selected backend integration in the trusted supervisor, authenticated role binding, claims, reservations, task revisions, command deduplication, outbox/reconciliation, and state recovery. For the narrow adapter, implement per-task files, compact indexes, rare renewal commits, and verified snapshots. Reuse upstream logic where accepted by P02a; preserve its supported protocol if adopted.

**Acceptance:** ownership and resource acquisition occur in one accepted transition; replay preserves task history; repeated commands do not double-apply; unauthorized or stale operations fail. Delayed board updates never alter ownership. Protect and recover the authoritative branch.

### P06 — Developer supervisor and checkpoints (M2)

**Context:** arbitrary repository code needs a controlled execution boundary. **Dependencies:** P05, P02b. **Scope:** runtime adapter, private checkout, capability matching, heartbeat/stop watchdog, bounded resources, credential-safe candidate publication, scope amendment, and recoverable checkpoints. Exclude automatic merge and arbitrary host hooks.

**Acceptance:** an enrolled worker completes a scoped task; scope widening preserves its lease and commits; incompatible widening pauses; restart recovers the last durable checkpoint. Host mounts, credential access, candidate hooks, and egress controls pass negative tests for the selected profile.

### P07 — GitHub board and human decisions (M2)

**Context:** GitHub must remain understandable to the maintainer. **Dependencies:** P05. **Scope:** status projection, three default fields, human ownership/delegate summary, questions, terminal answers, stop/resume, and discrepancy repair.

**Acceptance:** duplicate/edited/stale commands cannot bypass authorization; a question blocks execution until an authorized answer; stop is shown as requested until confirmed; the board is rebuilt from state after a failed write. Human testing confirms that a maintainer can identify what is blocked, why, and who must respond.

### P08 — Pull-based review and task-wide budget (M2)

**Context:** review must operate independently of the developer session and should not wait for developer-sandbox implementation. **Dependencies:** P05, P03, P02b. **Scope:** pending review jobs, reviewer claims, fresh sandbox/session using the small launcher validated in P02b, schema-validated evidence, prior findings, aggregate rounds, rework queue, and bounded infrastructure retries. Use a fixture developer that submits a fixed candidate through the trusted publication contract; do not give it a direct-state bypass. Reviewer-specific launch support belongs to P08; general developer lifecycle integration remains in P06/P09.

**Acceptance:** an independently started reviewer processes the fixture candidate without P06; change requests return work to Ready; reassignment does not reset the budget; duplicate results count once; stale candidates and unverified checks cannot pass. Exercise `unverified_pilot` labeling and manual acceptance; no automatic Done transition is possible without the recorded decision and integration. Complete the real cross-vendor developer/reviewer pairing at M2 integration once P06 is available. Exclude broad hosted-review adapter coverage.

### P09 — Trusted evidence and integration gate (M3)

**Context:** matching toolchains and model verdicts are insufficient completion evidence. **Dependencies:** P04, P06, P07, P08. **Scope:** integrate the independently developed developer/reviewer paths, switch explicitly from `unverified_pilot` to `trusted_ci`, and implement trusted CI provenance, per-criterion evidence, architecture checker execution, required checks, candidate/base revalidation, manual integration, and Done reconciliation.

**Acceptance:** developer-supplied logs cannot satisfy a trusted-CI requirement; pilot manual exceptions cannot silently authorize new trusted-mode completions; altered workflows, stale SHAs, unavailable required checks, and unmerged PRs fail the gate. An accepted merge or explicit non-code deliverable completes the task and unlocks its dependents.

### P10 — Template and existing-repository installer (M3)

**Context:** reusability requires low-friction setup, not copied internals. **Dependencies:** P09. **Scope:** guided setup, generated credential specifications from P01, pinned images, capability/permission diagnostics, existing-project preservation, enrollment, operator examples, idle reconciliation, and documented upgrade/rollback. Exclude a hosted web dashboard.

**Acceptance:** clean template setup and a brownfield dry run produce reviewable changes; rerun is idempotent; no secret enters Git; missing Projects permission or unsupported sandbox yields a precise next step. The generated credential specification matches the selected profile and distinguishes API permissions from branch restrictions; an idle-system exercise shows an answer remains pending until `harness reconcile` or a supervisor processes it. The second project requires configuration changes only.

### P11 — Fault and adversarial qualification (M4)

**Context:** concurrency failures emerge at boundaries. **Dependencies:** P10. **Scope:** execute the scenarios in section 12 with durable evidence; inject network failure, retries, stale evidence, malicious configuration, and process loss. Keep unit tests for deterministic reducers and live tests for actual transport/permissions.

**Acceptance:** all required scenarios pass for the supported profile, including a rehearsal of the P12 cutover and rollback with old-controller callbacks; untested guarantees are explicitly marked unsupported; results include software revisions, test IDs, logs, and reproducible setup. No claim of production security certification.

### P12 — Two-project pilot and release decision (M4)

**Context:** a reusable harness must work beyond Weave. **Dependencies:** P11. **Scope:** operate Weave plus one existing project with different configuration; two developers and an independent reviewer; dependency unlock, scope amendment, human answer, failed review, takeover/recovery, and merge. Collect setup time, maintenance effort, API/Actions usage, review turnaround, and failure recovery data.

**Mandatory Weave cutover, rehearsed in P11:**

1. Pause legacy intake and dispatch; drain or stop all development/review executions. Confirm no held claims, uncertain active processes, pending publications, or unresolved in-flight effects. Lease expiry alone is not confirmation.
2. Export and retain the old ledger, relevant issue-event history, configuration, and candidate/checkpoint references. Record a cutover marker and exact source revision. Revoke or remove the legacy controller's publication authority and disable its triggers so delayed callbacks cannot write after cutover.
3. Import open tasks, candidate references, unresolved questions, resource holds, and task-wide review history across all legacy attempts. Preserve original event IDs and provenance; count completed quality rounds rather than resetting at attempt boundaries. Ambiguous or incomplete counts block that task for explicit human reconciliation. Do not infer a reset from missing data.
4. Initialize the new authority epoch, invalidating every legacy claim, with no active worker claim imported. Validate task mappings, dependency readiness, review limits/counts, and evidence mode; produce a dry-run reconciliation diff. Record an authorized cutover acceptance before enabling new supervisors.
5. Start the new supervisors in `trusted_ci` mode and verify rejection of late legacy events. Never run old and new controllers with simultaneous write authority. Rollback first pauses/fences and drains the new controller, reconciles post-cutover work back into an explicit compatible legacy state, and only then restores old authority. Do not restore an old ledger snapshot over newer completed work. If that reverse mapping is unsafe, remain paused for manual recovery.

**Acceptance:** both projects complete the scenario without harness-source patches; all critical gates remain enabled; the cutover report proves that imported review budgets/questions/candidates are preserved and no dual-authority interval occurred. Human operators can recover from documented failures. Publish a release decision, limitations, and prioritized follow-up work. Do not extrapolate a small pilot into a large-project throughput claim.

### Safe implementation parallelism

P02a, P02b, and P03 may proceed together after P01. Within P02a, the gh-aw assessment and narrow-adapter tests start together in separate test repositories. P04 may proceed beside P05/P06 after P03. P05 needs P02a and P03; P07 may follow P05 while runtime work continues. P06 and P08 additionally need P02b and can then proceed alongside P07, using P03 contracts and the P02b reviewer-launch fixture. M0 exit includes a joint coordination/runtime stop test, without merging the two task scopes. Separate ownership of backend, developer runtime, reviewer execution, GitHub projection, and architecture modules; schema changes require explicit dependency updates and a shared-interface reservation. M2 assembles the real developer/reviewer loop in `unverified_pilot` mode after P06/P07/P08. P09 explicitly depends on P06 and is the trusted-evidence integration point; decoupling P08 must not bypass developer-runtime integration. P11 and P12 require completed prerequisites because their acceptance depends on the integrated system.

A spike is plausibly several engineer-days. A useful integrated pilot is more plausibly several engineer-weeks, approximately 3–6 after scope and permissions are understood; hardening and broader provider/platform support take longer. These are low-confidence planning estimates. M0 replaces them with measured work, including maintainer review and integration effort; agent assistance is not a reason to promise a fixed delivery date.

## 12. Acceptance and failure scenarios

These are release requirements, not evidence of tests already executed. P02a covers A01, A04, A05, A07, and authority fencing in A17; P02b covers A19 and runtime behavior in A07/A17. Their joint M0 exit checks the complete stop path. P11 runs the integrated suite and the P12 cutover rehearsal. Unless stated otherwise these are `trusted_ci` release requirements. For M2, A13/A23 must additionally demonstrate that an `unverified_pilot` manual acceptance remains visibly distinct from a PASS or trusted-CI completion.

| ID | Scenario | Required observable outcome |
| --- | --- | --- |
| A01 | Two hosts claim the same ready task concurrently. | One accepted owner; the loser sees authoritative state and does not launch accepted work. |
| A02 | A task has an unfinished, inaccessible, or unapproved prerequisite. | It is not claimable; readiness explains the blocker. |
| A03 | Independent tasks span different milestones. | They can run concurrently unless an explicit milestone gate or resource blocks them. |
| A04 | Claim expiry races with renewal and takeover. | A single accepted generation wins; old-generation publication is rejected. |
| A05 | State commit succeeds but its response is lost. | Retry recovers the same command result without a second claim or round charge. |
| A06 | Board/comment write fails after state commit. | Reconciliation restores the projection without repeating authority transitions. |
| A07 | A disconnected old worker continues computing. | No new output is accepted; UI reports termination uncertainty; strict tasks are not reassigned prematurely. |
| A08 | Scope must widen mid-task. | Authorized amendment preserves commits and lease, rechecks resources, and invalidates affected evidence. |
| A09 | Two tasks edit an undeclared overlapping interface. | Detected overlap stops acceptance or integration; plan/resource declarations are revised explicitly. |
| A10 | A reservation is released during review and rework starts later. | Rework reacquires resources and validates the current base before publishing. |
| A11 | Two reviewers race for a pending job. | One accepted review owner; retry cannot double-charge the round. |
| A12 | Review result references an old candidate or task digest. | Result rejected for current approval; prior completed budget charges remain. |
| A13 | Reviewer cannot run full checks. | Missing evidence is explicit; no required check passes on a developer's assertion. |
| A14 | The task exhausts its quality or infrastructure budget. | Automatic work pauses; human receives a clear summary and authorized next options. |
| A15 | Worker/session/branch changes after rejection. | Rework retains prior findings and task-wide counts. |
| A16 | Unauthorized, duplicated, edited, or stale human answer arrives. | It cannot change policy; accepted replies are correlated and applied once. |
| A17 | Stop arrives during active work or publication. | Authority is fenced; connected supervisor terminates within the measured target; in-flight effects are reconciled without false stop confirmation. |
| A18 | Candidate modifies its own CI, harness policy, or devcontainer. | Trusted policy does not change; host hooks and elevated execution are not enabled by the candidate. |
| A19 | Candidate tries to access host credentials/socket or bypass egress. | The selected runtime profile blocks the tested path and records the result. |
| A20 | Developer poisons a shared package/test cache. | Reviewer and trusted CI do not consume developer-writable trusted inputs. |
| A21 | Container/host dies after checkpoint. | Replacement resumes the acknowledged checkpoint; unpushed work is explicitly unavailable. |
| A22 | Blueprint rule is unsupported or selects no modules. | Result is unverified or invalid, not satisfied by absence. |
| A23 | Issue is closed, PR is unmerged, or required evidence is missing. | Task does not become Done; dependents remain blocked. |
| A24 | Candidate/base changes after review. | Required revalidation prevents integration on stale evidence. |
| A25 | Scheduler trigger is delayed, requests hit limits, or network partitions. | Safety holds; latency degrades visibly; bounded retries and reconciliation recover when service resumes. |
| A26 | State is rewound, corrupted, schema is unsupported, or snapshot disagrees with replay. | Worker fails closed; snapshot/full-replay equivalence is checked; documented recovery preserves identity, command receipts, review counts, and audit history. |
| A27 | Duplicate dispatch creates uncertain physical execution. | Capacity is not refunded solely on lease expiry; owner/effect fencing holds and uncertainty is surfaced. |
| A28 | Installation is rerun in an existing project. | No duplicate issues/fields or destructive overwrites; configuration and authority remain consistent. |

Initial operating envelope: one repository, two developer slots, one reviewer slot, and a plan fixture of 500 tasks with a nontrivial DAG. Measure startup/replay cost, readiness-query latency, claim contention, request volume, and Actions consumption. M0 chooses explicit latency and cost thresholds suitable for the target account; the release report states achieved values. If this envelope fails, reduce supported scale or choose a justified alternative backend before expanding functionality.

## 13. Risks, decision gates, and review questions

The main risk is integration complexity masquerading as reuse. Upstream queue APIs may be unstable, Actions-native identity may not fit external workers, and different security models may make adaptation more expensive than a small local implementation. Time-box M0 and document the result. Upstream adoption must reduce maintained responsibility, not merely add dependencies.

The Git branch design trades simple infrastructure for serialized state writes, history growth, and GitHub latency. Measure these costs. A hosted coordinator is a fallback only if the chosen implementation cannot meet the supported envelope; that alternative needs a concrete hosting, authentication, backup, and maintenance plan before approval.

Architecture checks remain incomplete by nature. Distinguish check coverage from architectural adequacy, and preserve unverified outcomes. Human planning and integration remain central responsibilities.

The review session should focus on:

1. Does the selected upstream backend support authenticated external workers without an unsafe second authority?
2. Are logical exclusivity, physical termination, and external-effect delivery guarantees stated precisely enough?
3. Is the trust boundary practical for a single maintainer, including provider credentials and Projects permissions?
4. Are the packet, provenance, aggregate-round, and invalidation rules sufficient and implementable?
5. Does the scope remain small enough to deliver the M2 loop before expanding integrations?
6. Are AAB rules grounded in an accessible authorized source, with honest checker coverage?
7. Do task dependencies and acceptance criteria permit safe implementation parallelism?
8. What measured evidence should cause a no-go or a backend change after M0?

Approval of this plan authorizes implementation of its agreed scope, not automatic publication, merge, or expansion into deferred platform features. An implementation proposal should attach the M0 decision record before committing to its backend.

## Sources and verification notes

Sources below support the factual observations retained from revision 3; proposed behavior, task definitions, and estimates are design recommendations. Revisions 4 and 5 are design amendments based on the supplied reviews, not fresh upstream assessments. The reviewer's recent gh-aw operational statistics have not been independently verified here and are not treated as facts or prerequisites. No live coordination spike, container escape test, deployment, or new repository test run was performed for this revision.

- **S1 — Weave:** [inspected current commit](https://github.com/quaat/weave/tree/e7c3f3cab1e25994b96a948cbe27c96bb061d5a8); [original baseline](https://github.com/quaat/weave/tree/d8010aec6746bbdcc54b21801c537d28917c0533). Source-path and focused-test findings come from the earlier assessment plus revision 3's API verification.
- **S2 — Weave issue #6:** [scope release](https://github.com/quaat/weave/issues/6#issuecomment-6503275585), [round-3 review evidence](https://github.com/quaat/weave/issues/6#issuecomment-6503850141), [relayed maintainer decisions](https://github.com/quaat/weave/issues/6#issuecomment-6502491358).
- **S3 — Symphony:** [service specification](https://github.com/openai/symphony/blob/main/SPEC.md), [release history](https://github.com/openai/symphony/releases).
- **S4 — gh-aw:** [overview](https://github.github.com/gh-aw/introduction/overview/), [security architecture](https://github.github.com/gh-aw/introduction/architecture/), [custom safe outputs](https://github.github.com/gh-aw/reference/custom-safe-outputs/).
- **S5 — gh-aw queue:** [Work Queue Specification, including implementation coverage](https://github.github.com/gh-aw/specs/work-queue-specification/). Specification and reported local conformance are not proof of live deployment guarantees.
- **S6 — gh-aw ledger:** [Git-backed Ledger Specification](https://github.github.com/gh-aw/specs/repo-memory-ledger-specification/), currently identified there as a working draft; distinct from proving a distributed task lock.
- **S7 — Beads:** [current upstream README](https://github.com/gastownhall/beads), including dependency commands and Dolt storage modes.
- **S8 — Linear:** [delegation](https://linear.app/developers/agents), [session lifecycle](https://linear.app/developers/agent-interaction), [stop signals](https://linear.app/developers/agent-signals).
- **S9 — Docker Sandboxes:** [security model](https://docs.docker.com/ai/sandboxes/security/), [defaults](https://docs.docker.com/ai/sandboxes/security/defaults/), [installation requirements](https://docs.docker.com/ai/sandboxes/install/).
- **S10 — conditional Git publication:** [GitHub REST refs](https://docs.github.com/en/rest/git/refs), [GraphQL commits and expectedHeadOid](https://docs.github.com/en/graphql/reference/commits), [Git push lease semantics](https://git-scm.com/docs/git-push).
- **S11 — existing architecture tools:** [import-linter forbidden contracts](https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/), [dependency-cruiser rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md), [ArchUnit user guide](https://www.archunit.org/userguide/html/000_Index.html).
- **S12 — devcontainer authority:** [devcontainer base schema](https://github.com/devcontainers/spec/blob/main/schemas/devContainer.base.schema.json), including host initialization, mounts, and elevated runtime options.
- **S13 — OCI security:** [Docker Engine security](https://docs.docker.com/engine/security/), [rootless mode](https://docs.docker.com/engine/security/rootless/), [build secrets](https://docs.docker.com/build/building/secrets/).
- **S14 — GitHub authority:** [ruleset controls](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [fine-grained token permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens).
- **S15 — scheduling:** [GitHub Actions event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), including scheduled-run limitations. Personal-Project polling is retained from the earlier webhook-capability assessment.
