# GitHub setup and recovery

The importer targets github.com and uses an existing operator-authenticated `gh`.
No login, token minting, repository creation or permission modification happens
automatically. Review `gh auth status` locally. Repository issue/milestone writes
and Project writes are separate capabilities. For the CLI's OAuth/classic-token
flow, its documented Project scope is `project`; use `gh auth refresh -s project`
only when that is appropriate to your authentication method. Fine-grained/App
configurations require their own supported account/Project permissions; do not
copy OAuth scope names into an App permission matrix.

Run `python3 -m bootstrap github --repo OWNER/REPO --owner OWNER --human LOGIN`
to inspect a deterministic, offline preview. Add `--project NUMBER` to select an
existing Project. Add `--apply` only when ready for the described remote writes.
The authenticated human needs permission to assign the selected human login.

Setup creates or reuses:

- Five named milestones and thirteen issues with stable Remora task markers.
- A Project titled `Remora — OWNER/REPO`, unless a number is supplied.
- Five Status options and three optional text fields.
- Project membership for every task, with initial status Todo.

It does not create native issue-dependency links: the checked repository manifest
and task text carry dependencies during bootstrap. It does not register workers,
protect branches, create runtime credentials or enable an autonomous controller.

In the Project UI, select Board layout, group by Status and save. Disable any
Project workflow that automatically marks closed issues/merged PRs Done until
you have checked its behavior against manual acceptance. Set branch protection
for `main` after CI has run: require PR review and the `bootstrap` check, restrict
bypass as appropriate, and keep automatic merge off. These protections help the
manual process; they do not implement P09's trusted verification workflow.

## Reruns and interruptions

Only one operator may import at a time. GitHub creation APIs plus list-before-write
do not provide a distributed lock. Stable markers and full paginated issue reads
allow sequential reruns to reuse tasks. Duplicate markers, changed task digests
or ambiguous project names stop the command. Existing issue prose and nonempty
board statuses are preserved; proposed task updates need manual review.

A populated Project's Status options are never replaced. If options are missing,
add them manually and rerun. Empty Projects may have their Status options set to
the five Remora values. Limits of 1,000 Projects/items and 100 fields fail closed
rather than silently ignoring a partial list. The importer is for this small
bootstrap backlog, not the future 500-task qualification requirement.

On a failed or timed-out write, inspect the remote resource before retrying.
Do not run another importer concurrently. A successful-but-unacknowledged create
may already be present. Rerun after it is visible; manually reconcile duplicates
if GitHub visibility was delayed. There is no transactional rollback; do not
delete resources blindly. Save the returned mapping in an operator-controlled
location for reference, but remote markers remain the rerun lookup mechanism.

## Credential boundaries

The bootstrap runs in a trusted operator session. Do not mount its `gh` credentials
into a model sandbox. Branch patterns are repository enforcement rules, not token
permissions. P01 defines the exact versioned permission matrix and P10 generates
the complete runtime credential specification. This starter does not pretend
that those unimplemented deliverables exist.

Implementation references checked 29 October 2026:

- https://cli.github.com/manual/gh_api
- https://cli.github.com/manual/gh_project
- https://cli.github.com/manual/gh_project_field-create
- https://cli.github.com/manual/gh_project_item-add
- https://docs.github.com/en/graphql/reference/projects

Offline fake-API tests validate request construction, pagination handling and rerun
behavior. Live GitHub behavior still needs validation after a repository is created.
