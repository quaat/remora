# Remora

**Remora — attach to a repo. Keep the work moving.**

Remora is a planned, reusable development harness that turns an approved project
plan into dependency-aware work, independent review, and evidence-backed delivery
through GitHub Issues, Projects and pull requests.

This repository is the **working development bootstrap, version 0.0.1**. It contains
the approved revision-5 plan and tools to start building Remora. The distributed
controller, sandbox workers and trusted evidence gate are not implemented yet.

## Start locally

Requires Python **3.11 or newer** (validated on 3.12.14) and Git. There are **no
third-party Python dependencies** and no package installation step.

```bash
python3 -m bootstrap check
python3 -m unittest discover -s tests -v
python3 -m bootstrap candidates
python3 -m bootstrap task P01
```

The first dependency candidate is P01. `candidates` is an offline planning aid;
it does not claim work or verify remote completion evidence.

## Put it in your new repository

Create an **empty GitHub repository** named `remora`, then run these commands from
the extracted directory, replacing `YOUR-LOGIN`:

```bash
git init -b main
git add .
git commit -m "Initialize Remora development bootstrap"
git remote add origin git@github.com:YOUR-LOGIN/remora.git
git push -u origin main
```

Use an existing authenticated GitHub CLI (`gh`). First preview the backlog setup:

```bash
python3 -m bootstrap github --repo YOUR-LOGIN/remora --owner YOUR-LOGIN --human YOUR-LOGIN
```

That command performs **no network operations**. When ready, add `--apply` to
create/reuse five milestones, thirteen task issues and a GitHub Project. Pass
`--project NUMBER` to reuse a selected Project. Run setup from **one trusted
operator session**. It preserves existing issues and nonempty task statuses;
it is not safe to run concurrent importers. See [GitHub setup](docs/development/github-setup.md).

All tasks initially enter Todo. In the Project UI, choose **Board** layout, group
by **Status**, save the view, confirm P01's scope allocation, and move P01 to
Ready for Development. The statuses are Todo, Ready for Development, In Progress,
In Review and Done; extra fields are Review, Needs human and Blocked by.

Then give Claude Code [the kickoff instruction](prompts/kickoff.md).
`AGENTS.md` is the common contract; `CLAUDE.md` directs Claude to it.

## What works now

| Capability | Bootstrap status |
| --- | --- |
| Approved plan copy and task/dependency checks | Implemented; source integrity checked |
| Issue-ready tasks with scope allocations and 38 criterion IDs | Implemented; allocations need maintainer confirmation |
| GitHub milestones, issues and Project setup | Implemented; mocked tests, awaiting a live repository run |
| Candidate-bound review packets and verdict-format checks | Implemented; advisory, human-authenticated |
| Local tests and GitHub Actions CI | Local suite verified; hosted workflow awaits first push |
| Distributed claims, runtime containment, independent review queue | Planned in P02a/P02b/P05/P06/P08 |
| Trusted CI provenance and Done gate | Planned in P09 |
| Autonomous operation | Disabled until qualification and explicit cutover |

## Can Remora build itself?

Yes, in stages. Start with a human assigning one active coding executor at a time,
an independent review session, and human integration. Use the bootstrap tools to
structure that work. P02a/P02b/P03 can be developed in parallel only when a human
assigns disjoint work and manages shared interfaces; the bootstrap does not
provide distributed ownership.

M2 demonstrates the new system on disposable work in `unverified_pilot` mode.
P09 introduces trusted evidence gates. Move Remora's own live backlog to the
implemented controller only after the relevant qualification tests pass and an
explicit cutover record retires the bootstrap convention. Weave's separate live
cutover remains P12. See [dogfooding](docs/development/dogfooding.md).

## Repository map

- `docs/plan/generic-agentic-harness-plan.md`: exact revision-5 source, unchanged.
- `docs/plan/remora-adoption.md`: naming, path allocation and bootstrap overlay.
- `.remora/tasks.json`: issue/task manifest tied to the source digest.
- `bootstrap/`: temporary standard-library tools, separate from the future product.
- `prompts/`: kickoff, developer and independent reviewer instructions.
- `tests/`: offline regression tests; no GitHub account or provider key required.
- `docs/development/`: setup, review workflow, handoff and self-hosting boundaries.

The product Python modules will live under `src/remora/`. No code has been copied
from Weave or upstream projects. P01 must inspect licenses before reuse; the
maintainer still needs to choose Remora's distribution license.
