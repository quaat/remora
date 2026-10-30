# ADR 0002 — Internal interfaces for M0-M2 tasks

Status: proposed by P01; the maintainer confirms. Owner tasks finalize signatures.

## Context

P02a, P02b and P03 run in parallel after P01, and P05-P09 later integrate their results.
Plan section 11 requires separate ownership of the backend, developer runtime, reviewer
execution, GitHub projection and architecture modules, with schema changes made through
explicit dependency updates and a shared-interface reservation. P02b must use a P01
execution/stop interface; P08 must launch reviewers without P06. These parallel tasks
need agreed boundaries before any product code exists.

Machine-readable index: `contracts/interfaces.v1.json` (operations, inputs, outputs and
errors). This ADR records ownership and the rules; the JSON lists the operations.

## Decision

Product code lives under `src/remora/`, separate from `bootstrap/` (ADR 0001). Owner
modules follow the proposed allocations in `.remora/tasks.json`. Ten interfaces, each
with exactly one owner task. Work another task contributes is expressed as that task
consuming the owner's interface ("depends on"), never as a shared owner. A dependency is
allowed only on an interface whose owner is the same task or a transitive prerequisite;
`tests/contracts/test_permission_matrix.py` checks this against `.remora/tasks.json`.

| Interface | Owner module | Owner task | Depends on | Consumers | Purpose |
| --- | --- | --- | --- | --- | --- |
| `state-backend` | `src/remora/state/` | P05 | `plan-compiler` | P02a (conformance fixtures), P06-P12 | Pure `compute_transition`; `apply_transition` with CAS on an expected head; `read_state`; `lookup_receipt`; `create_snapshot`/`verify_snapshot` |
| `publisher` | `src/remora/publication/` | P05 | `state-backend` | P02a, P06, P07, P08, P09 | `conditional_ref_update` (transport chosen by P02a), `publish_candidate` into generation-specific refs from a clean Git environment, `read_back_effect` |
| `execution` | `src/remora/runtime/` | P06 | `state-backend`, `publisher` | P02a (joint A17), P02b, P06, P08, P11 | `start`, `checkpoint`, `stop_request`, events `stop_confirmed` and `authority_lost`, `status` |
| `reviewer-launch` | `src/remora/review/launch.py` | P08 | `state-backend`, `plan-compiler`; conforms to the `execution` contract without depending on P06's module | P02b, P08, P09 | `launch_review` (fresh clone, writable scratch, no developer session), `collect_result` (infrastructure outcome separate from verdict) |
| `command-envelope` | `src/remora/commands/` | P05 | — | P07, P10, P11 | `derive_command_id` (deterministic), `validate_envelope`; receipts are `state-backend` records |
| `command-ingestion` | `src/remora/github/commands.py` | P07 | `command-envelope`, `state-backend` | P07, P10, P11 | `poll_commands`, `parse_and_authenticate`, `submit` (dedup by `command_id` through state receipts), `post_terminal_command` |
| `board-projection` | `src/remora/github/projection.py` | P07 | `state-backend` | P07, P10, P11 | Pure `compute_projection`; `read_projection`; `reconcile_projection` that never changes state |
| `plan-compiler` | `src/remora/plan/` (its schemas in `src/remora/contracts/`, also P03) | P03 | — | P04, P05, P07, P08, P09, P10 | `load_plan`, `validate`, `compile_task_revision`, `readiness`, `build_review_packet` |
| `evidence-records` | `src/remora/review/evidence.py` | P08 | `plan-compiler` (evidence and verdict record schemas), `state-backend` | P08, P09, P11, P12 | `record_check_evidence`, `validate_verdict`, `record_manual_acceptance` (`unverified_pilot`) |
| `trusted-evidence` | `src/remora/evidence/` | P09 | `evidence-records`, `state-backend` | P09, P10, P11, P12 | `verify_trusted_ci`, `evaluate_completion_gate` |

Rules:

1. **One authority path.** Every authoritative change goes through
   `state-backend.apply_transition`. Ingesters, projectors, publishers and runtimes submit
   commands or read state; none keeps a private ledger.
2. **Authentication comes from transport plus enrollment.** No operation accepts a
   model-supplied actor or `worker_id` as identity (plan section 4).
3. **Ambiguity is explicit.** Every write may return `AmbiguousWrite`; callers look up the
   stable command ID or idempotency key before retrying. `Conflict` means reread and
   recompute.
4. **Fencing.** Every command carries the claim generation; `publisher` and
   `state-backend` reject stale generations; `execution.authority_lost` obliges the
   supervisor to stop.
5. **Stop is two facts.** Authority revocation (state) and physical termination
   (`stop_confirmed` with evidence) are distinct; without observed termination the state
   stays `stop_requested` or `stop_uncertain` (plan section 9).
6. **Infrastructure outcomes are not verdicts.** `reviewer-launch.collect_result` reports
   them separately; `evidence-records.validate_verdict` never turns them into PASS.
7. **Shared schemas.** Task, criterion, revision, packet and review schemas are owned by
   P03 (`src/remora/contracts/`); others consume them. A change by a non-owner needs a
   shared-interface reservation and an explicit dependency update.
8. **Fixtures are not owners.** P02b builds fixtures of the `execution` and
   `reviewer-launch` contracts in its own experiment paths (`contract_fixture_task`); P02a
   builds `state-backend`/`publisher` conformance fixtures likewise. Production owners stay
   as listed.
9. **Compatibility with the bootstrap.** P03's packet/review fields stay compatible with
   `bootstrap/core.py` (see `docs/research/P01/handoff-P03.md`) so bootstrap completions
   can be imported with their manual provenance.

## Consequences

P02a can write conformance fixtures against `state-backend` and `publisher` while P02b
writes fixtures against `execution` and `reviewer-launch`; their joint M0 stop test meets
at `stop_request` → `authority_lost`/`stop_confirmed`. P03 can publish schemas without
waiting for either spike.

These are proposals. If P02a selects gh-aw, `state-backend` and `publisher` become an
adapter over gh-aw's supported protocol, and their operations must be re-validated against
it rather than imposing the local layout (plan section 4). Changes to this index require a
new `interfaces` version and an update to this ADR.
