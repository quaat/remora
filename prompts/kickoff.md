# Start Remora development

You are developing **Remora — attach to a repo. Keep the work moving.**

Read `AGENTS.md`, `README.md`, `docs/plan/remora-adoption.md`, the revision-5 plan
and `docs/development/workflow.md`. Run the bootstrap checks and tests. Inspect
the existing repository/Project state before making assumptions about progress.

Start with **P01 — Reuse and authority decision**. If it is already integrated,
report that evidence and identify the next dependency-eligible task for human
assignment. Do not repeat completed work or start a task another executor owns.

For an unstarted P01:

1. Read its exact task packet with `python3 -m bootstrap task P01`. Confirm the
   accountable human and proposed paths/criteria; capture the starting commit.
2. Inspect pinned Weave and upstream source, licenses and supported interfaces.
   The source plan's earlier observations are evidence leads, not current proof.
3. Produce the reuse inventory, responsibilities/code comparison baseline,
   proposed internal interfaces, and versioned machine-readable permission matrix
   with separate setup/runtime roles and supervisor/Actions placements. Record
   unknowns and concrete blockers. Do not invent supported APIs or token scopes.
4. Prepare the P02a/P02b test contracts and P03 schema handoff. Preserve their
   parallelism and the joint M0 stop-path gate. Do not select a production backend
   or implement the complete controller during P01.
5. Run relevant checks, commit the candidate and prepare a frozen review packet.
   Obtain an independent review using `prompts/reviewer.md`; retain all findings
   and task-wide round counts. Do not merge or mark Done yourself.

The maintainer controls GitHub writes and assignment. If GitHub resources have
not been imported, show the bootstrap preview and document the exact apply command
for the maintainer. Do not create a second Project or backlog by guessing.

At handoff provide changed files, acceptance evidence, candidate/base and packet
digest, unresolved questions, review count and the next human action. Stop at the
P01 boundary until the prerequisite acceptance needed by later tasks is recorded.
