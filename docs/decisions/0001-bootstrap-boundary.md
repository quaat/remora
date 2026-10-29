# ADR 0001 — Human-operated bootstrap before self-hosting

Status: starter decision; maintainer confirms before P01 assignment.

## Context

Remora needs a harness to develop its harness. Depending on an unbuilt controller
for safe ownership or trustworthy review would be circular.

## Decision

Use small Python standard-library tools for plan integrity, dependency simulation,
GitHub backlog setup and frozen review packet formatting. Keep them in `bootstrap/`,
separate from future `src/remora/` product modules. A human owns task assignment,
review authentication, budgets, scope amendments and integration during this phase.
The board reflects that convention; it is not an atomic lock or a durable reducer.

Do not ship a purported secure worker image before P02b verifies its real host,
credential, egress and stop behavior. Do not select gh-aw or a narrow adapter
before P02a's concurrent experiments and explicit rejection criteria.

Self-host only through the staged cutover described in `docs/development/dogfooding.md`.
M2 and the bootstrap are different modes: bootstrap is a manual convention;
`unverified_pilot` is a future implemented controller mode with its own contracts.

## Consequences

Useful development can start now without overclaiming distributed safety.
GitHub setup requires one operator and manual recovery from ambiguous writes.
Some bootstrap code may be deleted after P03/P07/P10; reuse requires a fit check,
not preserving temporary code for its own sake.

An agent can edit instructions and policies, so these files are guidance, not an
OS security boundary. Trusted execution and provenance remain milestone work.
