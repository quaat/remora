"""Offline plan checks and candidate-bound review packets; no execution authority."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plan/generic-agentic-harness-plan.md"
TASKS = ".remora/tasks.json"
POLICY = ".remora/bootstrap-policy.json"
ARCHITECTURE = "docs/decisions/0001-bootstrap-boundary.md"
STATUSES = ("Todo", "Ready for Development", "In Progress", "In Review", "Done")


class Invalid(ValueError):
    """An input cannot be accepted by the bootstrap tooling."""


def digest(value: Any) -> str:
    data = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_sections(text: str) -> dict[str, dict[str, Any]]:
    pattern = re.compile(r"^### (P\d{2}[ab]?) — (.+) \((M\d)\)\n", re.M)
    result = {}
    for match in pattern.finditer(text):
        end = re.search(r"^###? ", text[match.end():], re.M)
        body = text[match.end():match.end() + end.start() if end else len(text)].strip()
        deps = re.search(r"\*\*Dependencies:\*\* (.*?)\. \*\*Scope:", body)
        if not deps:
            raise Invalid(f"Missing dependency declaration: {match[1]}")
        result[match[1]] = {
            "title": match[2], "milestone": match[3], "source_excerpt": body,
            "depends_on": re.findall(r"P\d{2}[ab]?", deps[1]),
        }
    return result


def validate(manifest: dict, source: bytes) -> list[str]:
    if manifest.get("schema_version") != 1 or manifest.get("source_revision") != 5:
        raise Invalid("Unsupported manifest schema or source revision")
    if manifest.get("source_sha256") != digest(source):
        raise Invalid("Approved source digest changed; review the plan revision explicitly")
    sections = source_sections(source.decode())
    tasks = manifest.get("tasks", [])
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)) or set(ids) != set(sections):
        raise Invalid("Duplicate, missing, or unexpected task IDs")
    milestone_ids = [m["id"] for m in manifest["milestones"]]
    if len(milestone_ids) != len(set(milestone_ids)):
        raise Invalid("Duplicate milestone IDs")
    by_id = {t["id"]: t for t in tasks}
    for task in tasks:
        task_id = task["id"]
        for key, value in sections[task_id].items():
            if task.get(key) != value:
                raise Invalid(f"{task_id}: {key} drifted from revision 5")
        if task["milestone"] not in milestone_ids:
            raise Invalid(f"{task_id}: unknown milestone")
        for field in ("allowed_paths", "deliverables", "exclusions", "verification",
                      "architecture", "acceptance_criteria"):
            if not task.get(field):
                raise Invalid(f"{task_id}: missing {field}")
        if type(task.get("review_limit")) is not int or task["review_limit"] < 1:
            raise Invalid(f"{task_id}: invalid review limit")
        for path in task["allowed_paths"]:
            if path.startswith("/") or ".." in path.split("/") or path in ("*", "**", "**/*"):
                raise Invalid(f"{task_id}: unsafe or unrestricted scope path")
        ac_ids = [c["id"] for c in task["acceptance_criteria"]]
        if len(ac_ids) != len(set(ac_ids)):
            raise Invalid(f"{task_id}: duplicate criterion")
        for criterion in task["acceptance_criteria"]:
            if not criterion.get("text") or not criterion.get("verification"):
                raise Invalid(f"{task_id}: incomplete acceptance criterion")
        acceptance = sections[task_id]["source_excerpt"].split("**Acceptance:** ", 1)[1].strip()
        if " ".join(c["text"] for c in task["acceptance_criteria"]) != acceptance:
            raise Invalid(f"{task_id}: acceptance checklist drifted from source")
        if any(dep not in by_id for dep in task["depends_on"]):
            raise Invalid(f"{task_id}: unresolved dependency")
    visited, active, order = set(), set(), []

    def visit(task_id: str) -> None:
        if task_id in active:
            raise Invalid(f"Dependency cycle at {task_id}")
        if task_id in visited:
            return
        active.add(task_id)
        for dep in by_id[task_id]["depends_on"]:
            visit(dep)
        active.remove(task_id)
        visited.add(task_id)
        order.append(task_id)

    for task_id in ids:
        visit(task_id)
    scenarios = re.findall(r"^\| (A\d{2}) \|", source.decode(), re.M)
    if scenarios != [f"A{i:02d}" for i in range(1, 29)]:
        raise Invalid("Expected all 28 source acceptance scenarios")
    return order


def load(root: Path = ROOT) -> dict:
    manifest = read_json(root / TASKS)
    validate(manifest, (root / PLAN).read_bytes())
    return manifest


def task_for(manifest: dict, task_id: str) -> dict:
    for task in manifest["tasks"]:
        if task["id"] == task_id:
            return task
    raise Invalid(f"Unknown task: {task_id}")


def candidates(manifest: dict, completed: list[str]) -> list[str]:
    """Human-declared completion simulation, not a readiness/claim authority."""
    known = {t["id"] for t in manifest["tasks"]}
    done = set(completed)
    if not done <= known:
        raise Invalid("Unknown completed task ID")
    for task in manifest["tasks"]:
        if task["id"] in done and not set(task["depends_on"]) <= done:
            raise Invalid(f"{task['id']}: declared completion omits prerequisites")
    return [t["id"] for t in manifest["tasks"]
            if t["id"] not in done and set(t["depends_on"]) <= done]


def issue_body(task: dict, source_sha: str) -> str:
    marker = f"<!-- remora:task:{task['id']} -->"
    criteria = "\n".join(f"- [ ] **{c['id']}** {c['text']}\n  Verification: {c['verification']}"
                         for c in task["acceptance_criteria"])
    scope = "\n".join(f"- `{p}`" for p in task["allowed_paths"])
    return f"""{marker}
## {task['id']} — {task['title']}

Milestone: **{task['milestone']}** · Dependencies: **{', '.join(task['depends_on']) or 'none'}**
Review budget: **0/{task['review_limit']}** · Mode: **human-operated bootstrap**

## Approved revision-5 task text

{task['source_excerpt']}

## Proposed repository allocation

Maintainer confirms paths, owner and criterion breakdown before assignment.
This allocation supplements the source; it never narrows its acceptance requirements.

{scope}

Deliverables: {'; '.join(task['deliverables'])}

Exclusions: {'; '.join(task['exclusions'])}

Architecture: {task['architecture']}

## Acceptance checklist

{criteria}

## Development and review record

Record assignment, candidate/base SHA, packet digest, checks with provenance,
reviewer identity, all prior findings, task-wide rounds, and integration evidence
in comments. A model PASS is advisory during bootstrap. A human owns assignment
and merge; no second executor may self-claim this task. Issue closure alone is
not completion. Use `prompts/developer.md` and `prompts/reviewer.md`.

Source: `docs/plan/generic-agentic-harness-plan.md`, revision 5.
Source SHA-256: `{source_sha}`
Task SHA-256: `{digest(task)}`
"""


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    if result.returncode:
        raise Invalid("Git command failed: " + result.stderr.decode(errors="replace").strip())
    return result.stdout


def review_packet(root: Path, task_id: str, base: str, developer: str) -> dict:
    if git(root, "status", "--porcelain").strip():
        raise Invalid("Commit or remove all working-tree changes before freezing a packet")
    manifest = load(root)
    task = task_for(manifest, task_id)
    head = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    base_sha = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").decode().strip()
    git(root, "merge-base", "--is-ancestor", base_sha, head)
    bindings = {}
    for path in (PLAN, TASKS, POLICY, ARCHITECTURE):
        committed = git(root, "show", f"{head}:{path}")
        if committed != (root / path).read_bytes():
            raise Invalid(f"Uncommitted policy at {path}")
        bindings[path] = digest(committed)
    packet = {
        "schema_version": 1, "mode": "bootstrap_advisory", "task_id": task_id,
        "task_digest": digest(task), "source_revision": 5,
        "candidate_sha": head, "base_sha": base_sha, "developer": developer,
        "policy_bindings": bindings,
        "diff_sha256": digest(git(root, "diff", "--no-ext-diff", "--no-textconv", "--binary", base_sha, head)),
        "task": task,
        "criteria": [{**c, "digest": digest(c)} for c in task["acceptance_criteria"]],
        "review_limit": task["review_limit"],
        "prior_findings_instruction": "Read all task issue review comments; counters are manually maintained during bootstrap.",
    }
    return {**packet, "packet_digest": digest(packet)}


def check_packet(packet: dict) -> None:
    raw = {k: v for k, v in packet.items() if k != "packet_digest"}
    if packet.get("packet_digest") != digest(raw):
        raise Invalid("Packet was modified after freezing")
    if packet.get("schema_version") != 1 or packet.get("mode") != "bootstrap_advisory":
        raise Invalid("Unsupported packet")
    if packet.get("task_digest") != digest(packet["task"]):
        raise Invalid("Packet task digest mismatch")
    expected = [{**c, "digest": digest(c)} for c in packet["task"]["acceptance_criteria"]]
    if packet.get("criteria") != expected:
        raise Invalid("Packet criterion drift")


def review_template(packet: dict) -> dict:
    check_packet(packet)
    return {
        "schema_version": 1, "packet_digest": packet["packet_digest"],
        "task_id": packet["task_id"], "task_digest": packet["task_digest"],
        "candidate_sha": packet["candidate_sha"], "base_sha": packet["base_sha"],
        "reviewer": {"identity": "REQUIRED", "provider": "REQUIRED", "tool_version": "REQUIRED"},
        "verdict": "UNVERIFIED", "summary": "Required evidence has not yet been collected.",
        "criteria": [{"id": c["id"], "digest": c["digest"], "status": "unverified",
                      "findings": "Pending independent review", "evidence": []} for c in packet["criteria"]],
    }


def check_review(packet: dict, review: dict) -> None:
    """Validate shape/binding only. Identity and evidence trust require a human."""
    check_packet(packet)
    if review.get("schema_version") != 1:
        raise Invalid("Unsupported review schema")
    for key in ("packet_digest", "task_id", "task_digest", "candidate_sha", "base_sha"):
        if review.get(key) != packet[key]:
            raise Invalid(f"Review has stale or mismatched {key}")
    reviewer = review.get("reviewer", {})
    if any(not reviewer.get(k) or reviewer[k] == "REQUIRED"
           for k in ("identity", "provider", "tool_version")):
        raise Invalid("Reviewer provenance is incomplete")
    if reviewer["identity"] == packet["developer"]:
        raise Invalid("Developer cannot be the designated independent reviewer")
    verdict = review.get("verdict")
    if verdict not in ("PASS", "CHANGES_REQUESTED", "UNVERIFIED") or not review.get("summary"):
        raise Invalid("Invalid verdict or missing summary")
    expected = {c["id"]: c["digest"] for c in packet["criteria"]}
    entries = review.get("criteria", [])
    if len(entries) != len(expected) or {c["id"] for c in entries} != set(expected):
        raise Invalid("Missing or duplicate review criteria")
    for item in entries:
        if item.get("digest") != expected[item["id"]] or item.get("status") not in (
            "satisfied", "violated", "unverified"
        ) or not item.get("findings"):
            raise Invalid("Invalid criterion result")
        if verdict == "PASS" and (item["status"] != "satisfied" or not item.get("evidence")):
            raise Invalid("PASS cannot cover missing or unverified criteria")
        for evidence in item.get("evidence", []):
            required = ("check_id", "executor", "environment", "source_sha", "artifact", "provenance")
            if any(not evidence.get(k) for k in required):
                raise Invalid("Incomplete per-check evidence provenance")
            if type(evidence.get("independently_executed")) is not bool:
                raise Invalid("Evidence needs an explicit independently_executed boolean")
            if evidence["source_sha"] != packet["candidate_sha"]:
                raise Invalid("Evidence refers to a different candidate")
            if type(evidence.get("exit_status")) is not int:
                raise Invalid("Evidence needs an integer exit_status (0 for accepted human inspection)")
            if verdict == "PASS" and (evidence["exit_status"] != 0 or not evidence["independently_executed"]):
                raise Invalid("PASS requires successful independently executed evidence")
