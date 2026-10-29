# Bootstrap development workflow

## Assign

The human reviews the task definition, approves the proposed paths and criterion
breakdown, confirms completed prerequisites by inspecting integration evidence,
and records one executor in the issue timeline. Keep the human as issue assignee.
Move the issue from Todo to Ready for Development, then In Progress when work
starts. Do this manually until P07 is qualified. A second agent must not infer
ownership from the board or self-assign.

Use `agent/P01-short-description` branches and separate worktrees for explicitly
parallel assignments. Do not use a shared writable checkout across agents.
Before touching a shared schema or root configuration, coordinate the scope.

## Implement and verify

Read `AGENTS.md` and the assigned task. Use its acceptance criteria as the work
boundary. Keep user-facing documentation current. Run the bootstrap checks and
task-specific checks; record exact commands and failures honestly. Scope changes
need an issue decision and updated task definition before fresh evidence is bound.

Commit the candidate before preparing review. The packet command requires a
clean working tree and a base that is an ancestor of HEAD. Replace placeholders:

```bash
mkdir -p .remora-local
python3 -m bootstrap review-packet P01 --base BASE_SHA --developer DEVELOPER_ID > .remora-local/P01-packet.json
python3 -m bootstrap review-template .remora-local/P01-packet.json > .remora-local/P01-review.json
```

The ignored directory keeps generated packet files from making the checkout dirty.
Keep durable copies with the PR/issue or an approved artifact store; ignored files
alone are not a checkpoint. The packet includes full criterion text/digests, the
task digest, candidate/base, diff digest and policy-file hashes. The reviewer must
read the previous issue review history; this bootstrap cannot authenticate it.

Move to In Review. Start a fresh independent reviewer, preferably using another
provider, with the exact candidate, packet, prior findings and writable scratch.
Use `prompts/reviewer.md`. The reviewer checks out the exact commit in its own
workspace and verifies the packet against the diff and committed policy. It runs
checks independently and fills the review JSON with actual provenance.

```bash
python3 -m bootstrap review-check .remora-local/P01-packet.json .remora-local/P01-review.json
```

This checks format and bindings only. It does not verify executor identity,
artifact authenticity, current branch head, review count or trusted CI provenance.
A fabricated identity or log reference can pass a format check. The human must
verify those facts and ensure the PR still matches the candidate before merging.

## Rework and finish

Keep task-wide completed PASS/CHANGES_REQUESTED rounds in the issue, default 3.
Keep infrastructure retries and UNVERIFIED retries separately, default 2 each.
Exhaustion pauses work for a human decision; no attempt or branch resets counters.
CHANGES_REQUESTED returns the task to Ready with prior findings retained.
UNVERIFIED means missing evidence, never PASS; the human decides how to obtain it.
Any new candidate or relevant task/policy change requires a fresh packet/review.

PASS remains In Review until a human verifies checks, authenticates the review,
checks current base/candidate and integrates. Only then record the merge SHA or
accepted non-code artifact, acceptance decision, review count and limitations;
move to Done and close the issue. Reassess dependents from accepted completions.
Bootstrap completions retain their manual evidence provenance during later import.

Use a short issue comment at assignment, checkpoint, review dispatch/result,
human decision and integration. Include task/candidate identity and the next
action. Agent text cannot impersonate the human. A maintainer's explicit task
instruction can authorize routine progress comments; without it, prepare drafts.
