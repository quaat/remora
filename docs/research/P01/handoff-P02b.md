# Handoff to P02b — runtime isolation and reviewer-launch spike

From: P01 (proposed, pending acceptance). P02b runs alongside P02a with a fixture
authority, establishes the runtime side of A07/A17 and A19, and joins P02a before M0 exit.
Runtime failures block P06/P08, not the backend assessment (plan section 11).

## 1. Execution/stop interface (from ADR 0002)

Owner module `src/remora/runtime/` (production owner P06); P02b builds the contract
fixture. Operations (`contracts/interfaces.v1.json`, interface `execution`):

| Operation | Direction | Contract |
| --- | --- | --- |
| `start(job_id, role, task_id, claim_generation, packet_digest, checkout_spec, runtime_profile_id, limits)` | call | Starts one sandbox with a private checkout of the exact SHA; **no GitHub credential** inside; returns `execution_id`, status `active`. Errors: `ProfileUnavailable`, `CapabilityMismatch`, `AuthorityNotHeld` |
| `checkpoint(execution_id)` | call | Exports a bundle and digest; `acknowledged=false` until the publisher acknowledges it. Unacknowledged work is not recoverable after host loss |
| `stop_request(execution_id, stop_id, reason)` | call | Idempotent by `stop_id`; authority is revoked in state before or with the call |
| `stop_confirmed` | event | Only after observed termination, with method, exit status, observer and last acknowledged checkpoint |
| `authority_lost` | event | Cause `lease_margin`, `offline_grace`, `revoked` or `generation_superseded`; the supervisor stops the process and refuses publication |
| `status(execution_id)` | call | Session status (`pending`, `active`, `awaiting_input`, `error`, `complete`, `stale`) and stop state (`none`, `stop_requested`, `stop_confirmed`, `stop_uncertain`) |

## 2. Reviewer-launch fixture contract (for P08 without P06)

Interface `reviewer-launch` (owner P08, `src/remora/review/launch.py`):

- `launch_review` takes a frozen review packet digest, `candidate_sha`, `base_sha`, review
  claim generation, runtime profile and provider. It calls `execution.start` with role
  `reviewer`, a **fresh clone and session per job**, and **writable scratch** (issue #6's
  round-3 reviewer could not run checks for lack of a writable temp dir; `weave-inventory.md` §G).
- No developer session, cache, workspace or credential is reachable.
- `collect_result` returns the review result, per-check evidence and a separate
  infrastructure outcome (`ok`, `timeout`, `tool_unavailable`, `crashed`). An infrastructure
  failure is never a verdict.
- Fixture: a fixed public candidate repository with known-good and known-failing checks;
  expected outputs are a successful check run in scratch, a failing check reported as
  failing, and a timeout reported as infrastructure outcome.

## 3. Runtime tests

| Test | Required outcome |
| --- | --- |
| A19 host credentials | Candidate code cannot read host GitHub tokens, `~/.config/gh`, SSH keys, provider credential files, or the supervisor's environment |
| A19 Docker socket and mounts | No `/var/run/docker.sock`, home directory or host root mount; mount table recorded |
| A19 egress | Direct TCP, DNS, IPv6 and proxy-bypass attempts to non-allowed destinations fail under the selected profile; allowed list recorded |
| A19 proxy misuse | With Docker Sandboxes, the `github` secret service is **not** configured; any configured provider proxy cannot be used for GitHub writes |
| A07 runtime | A partitioned supervisor stops execution after the offline-grace interval; the record reports uncertainty instead of confirmation |
| A17 runtime | Connected stop terminates the process within the documented target; `stop_confirmed` carries evidence; termination of child processes is verified |
| Writable reviewer scratch | Reviewer runs the fixture checks in scratch with the root filesystem otherwise read-only where the toolchain allows |
| Devcontainer refusal | `initializeCommand`, `mounts`, `workspaceMount`, `privileged`, `capAdd`, `securityOpt`, `runArgs`, Compose files and Features are refused or require human approval (`runtime-and-identities.md` §E.3) |
| Candidate hooks | Publication imports candidate material into a clean Git environment; candidate Git hooks, credential helpers and filters never run with publication credentials |

## 4. Credential-separation negative tests (from the permission matrix)

`developer-sandbox` and `reviewer-sandbox` hold no credential (`contracts/permission-matrix.v1.json`).
Prove, under the selected profile:

1. No GitHub token in the sandbox environment, files or keyring; `gh auth status` fails.
2. Docker Sandboxes `ssh.agentForwardingEnabled=false` (default is `true`), skills off,
   `browser.enabled=false`, clone mode or mountless workspace, no local stdio MCP servers,
   no `sbx secret set github`; record `sbx settings ls --json` and `sbx policy ls`.
3. A model-provider key placed in the sandbox is readable by candidate code; either use a
   host-side injecting proxy or record the exposure explicitly (`runtime-and-identities.md` §F).
4. The supervisor's state/publication credential cannot be reached through any proxy the
   model can invoke.

## 5. Host requirements to record

- Docker Sandboxes (`S-docker-sbx-install`): macOS 14+ on Apple silicon; Windows 11 x86-64
  with Windows Hypervisor Platform; Linux **Ubuntu 24.04 or later** on x86-64 or Arm64 with
  KVM and the user in the `kvm` group; nested virtualization inside VMs; `sbx login` required.
  Ubuntu derivatives are not supported.
- The bootstrap host is **Debian 11**, outside that list; `/dev/kvm` was not visible from
  the research sandbox, which is inconclusive (README Q11).
- Rootless OCI (`S-docker-rootless`, `S-docker-rootless-tips`): `newuidmap`/`newgidmap`,
  at least 65,536 subordinate IDs; cgroup limits apply only with cgroup v2 and systemd and are
  otherwise **silently ignored**, so `doctor` must fail closed when limits are not enforced.
- Record kernel, runtime versions, settings and the exact profile for each supported host.

## 6. Joint M0 stop-path gate (with P02a)

M0 exits only when, on the backend P02a selects and the runtime P02b selects:

1. An authorized stop command is accepted once (command receipt), and one transition records
   `stop_requested` and revokes publication authority for the generation (P02a side).
2. The connected supervisor observes the revocation within the measured poll interval and
   calls `execution.stop_request`.
3. The process tree terminates within the documented connected-stop target, and
   `stop_confirmed` with termination evidence is recorded as a **separate** fact.
4. Any publication or transition from the stopped generation after revocation is rejected.
5. Partitioned variant: no `stop_confirmed` is recorded; the state remains
   `stop_requested`/`stop_uncertain`; strict tasks are not reassigned; physical capacity is
   not refunded on expiry alone (A27).
6. Report times for each step. Fixture success alone is insufficient (plan section 11, P02a
   acceptance).
