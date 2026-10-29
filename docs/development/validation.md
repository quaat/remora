# Bootstrap validation

Date: 29 October 2026

Environment: Python 3.12.14, Linux, local Git fixture repositories.

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 45 tests passed |
| `python3 -m bootstrap check` | 13 tasks, 5 milestones, 28 source scenarios validated |
| Source plan integrity | Byte-for-byte revision-5 copy; SHA-256 bound in manifest |
| Initial dependency candidates | P01 only |
| After P01 | P02a, P02b and P03 eligible in dependency simulation |
| GitHub dry-run CLI | Offline preview of expected backlog and board settings |

The tests exercise source/criterion drift, missing tasks, cycles, invalid scopes,
dependency consistency, immutable candidate packets, dirty-tree rejection,
candidate/policy/criterion bindings, reviewer provenance shape, duplicate criteria,
missing and failed evidence, and independent-execution flags.

Fake GitHub tests exercise complete setup, sequential idempotency, preservation
of active statuses and issue edits, simulated successful writes with lost
acknowledgment, partially initialized items, duplicate markers, missing markers,
changed task digests, populated Project field protection, ambiguous Project
selection, structured stdin payloads, pagination, API errors and no blind retries.

These are bootstrap tests. They do not establish the planned A01–A28 release
guarantees. No live GitHub mutation, hosted Actions run, provider session,
container containment test or distributed lease experiment was performed.
There is no repository URL yet and no implementation milestone is marked complete.

Required next validation: the maintainer's first GitHub import/CI run, followed
by the P01 decision work and P02a/P02b live experiments. Preserve any failures as
evidence; do not convert a mocked test result into a live-conformance claim.
