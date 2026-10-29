"""Single-operator GitHub backlog setup. Never a task scheduler or lock."""

from __future__ import annotations

import json
import os
import re
import subprocess

from .core import Invalid, STATUSES, digest, issue_body


class GitHub:
    """Use the operator's gh authentication; never collect or print tokens."""

    def run(self, *args: str, payload: dict | None = None):
        command = ["gh", *args]
        if payload is not None:
            command += ["--input", "-"]
        result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                                text=True, capture_output=True, check=False, timeout=120,
                                env={**os.environ, "GH_HOST": "github.com", "GH_PROMPT_DISABLED": "1"})
        if result.returncode:
            raise Invalid("GitHub operation failed; no automatic write retry. Inspect remote state before rerunning.\n"
                          + result.stderr.strip())
        value = json.loads(result.stdout) if result.stdout.strip() else None
        if isinstance(value, dict) and value.get("errors"):
            raise Invalid("GitHub GraphQL reported errors; inspect remote state before retrying")
        return value

    def rest(self, path: str, payload: dict | None = None):
        return self.run("api", "--hostname", "github.com", "--method", "POST" if payload is not None else "GET",
                        path, payload=payload)

    def pages(self, path: str) -> list:
        pages = self.run("api", "--hostname", "github.com", "--method", "GET", "--paginate", "--slurp", path)
        return [item for page in pages for item in page]

    def graphql(self, query: str, variables: dict):
        return self.run("api", "--hostname", "github.com", "graphql", payload={"query": query, "variables": variables})["data"]


def validate_target(repo: str, owner: str, human: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise Invalid("Repository must be OWNER/REPO on github.com")
    if any(not re.fullmatch(r"[A-Za-z0-9-]+", v) for v in (owner, human)):
        raise Invalid("Use explicit GitHub owner and human logins, not @me")


def unique(items: list, key, description: str) -> dict:
    result = {}
    for item in items:
        value = key(item)
        if value is None:
            continue
        if value in result:
            raise Invalid(f"Duplicate {description}: {value}; reconcile manually")
        result[value] = item
    return result


def managed_issues(issues: list, manifest: dict) -> dict:
    known = {t["id"]: t for t in manifest["tasks"]}
    result = {}
    for issue in issues:
        if "pull_request" in issue:
            continue
        matches = re.findall(r"<!-- remora:task:(P\d{2}[ab]?) -->", issue.get("body") or "")
        if not matches:
            if any(issue.get("title", "").startswith(f"[{task_id}]") for task_id in known):
                raise Invalid("Task-like issue has no Remora marker; reconcile before importing")
            continue
        if len(matches) != 1 or matches[0] not in known or matches[0] in result:
            raise Invalid("Duplicate or unknown Remora issue marker; reconcile manually")
        task_id = matches[0]
        if f"Task SHA-256: `{digest(known[task_id])}`" not in (issue.get("body") or ""):
            raise Invalid(f"{task_id}: imported definition digest differs; no automatic overwrite")
        result[task_id] = issue
    return result


def preview(manifest: dict, repo: str, owner: str, human: str, project: int | None) -> dict:
    validate_target(repo, owner, human)
    if project is not None and project < 1:
        raise Invalid("Project number must be positive")
    return {
        "mode": "dry_run_no_network", "repository": repo, "project_owner": owner,
        "human_assignee": human, "project": project or f"Remora — {repo}",
        "milestones": [m["title"] for m in manifest["milestones"]],
        "issues": [f"[{t['id']}] {t['title']}" for t in manifest["tasks"]],
        "statuses": list(STATUSES), "extra_text_fields": ["Review", "Needs human", "Blocked by"],
        "initial_status": "Todo for all tasks; maintainer approves P01 allocation before moving it to Ready",
        "limitations": "Single operator only. No claims, workers, automatic merge or trusted evidence gates.",
    }


def project_fields(gh: GitHub, project: dict, owner: str, empty: bool) -> dict:
    number = str(project["number"])
    def read():
        data = gh.run("project", "field-list", number, "--owner", owner, "--limit", "100", "--format", "json")
        if len(data["fields"]) >= 100:
            raise Invalid("Field-list limit reached; inspect project manually")
        return unique(data["fields"], lambda x: x["name"], "Project field")
    fields = read()
    status = fields.get("Status")
    if not status or status.get("type") != "ProjectV2SingleSelectField":
        raise Invalid("Project must contain a single-select Status field")
    existing = {o["name"] for o in status.get("options", [])}
    if not set(STATUSES) <= existing:
        if not empty:
            raise Invalid("Existing Project lacks required statuses. Add them manually; populated fields are never replaced.")
        gh.graphql(
            "mutation($input: UpdateProjectV2FieldInput!) { updateProjectV2Field(input:$input) { projectV2Field { ... on ProjectV2SingleSelectField { id } } } }",
            {"input": {"fieldId": status["id"], "singleSelectOptions": [
                {"name": name, "color": color, "description": "Remora bootstrap lifecycle"}
                for name, color in zip(STATUSES, ("GRAY", "BLUE", "YELLOW", "PURPLE", "GREEN"))]}})
    for name in ("Review", "Needs human", "Blocked by"):
        if name not in fields:
            gh.run("project", "field-create", number, "--owner", owner, "--name", name,
                   "--data-type", "TEXT", "--format", "json")
        elif fields[name].get("type") != "ProjectV2Field":
            raise Invalid(f"Existing {name} field has an incompatible type; configure manually")
    fields = read()
    options = unique(fields["Status"]["options"], lambda x: x["name"], "status option")
    if not set(STATUSES) <= set(options):
        raise Invalid("Status configuration did not read back correctly")
    return fields


def apply(manifest: dict, repo: str, owner: str, human: str,
          project_number: int | None, gh: GitHub | None = None) -> dict:
    preview(manifest, repo, owner, human, project_number)
    gh = gh or GitHub()
    # Read all repository identity and duplicates before any mutation.
    repo_info = gh.rest(f"repos/{repo}")
    if repo_info.get("full_name", "").lower() != repo.lower() or repo_info.get("archived"):
        raise Invalid("Repository identity differs or is archived")
    if not repo_info.get("has_issues"):
        raise Invalid("Enable Issues before importing the backlog")
    milestones = unique(gh.pages(f"repos/{repo}/milestones?state=all&per_page=100"), lambda x: x["title"], "milestone")
    issues = managed_issues(gh.pages(f"repos/{repo}/issues?state=all&per_page=100"), manifest)
    # Validate assignee before writes (REST returns 204/no body on success).
    gh.rest(f"repos/{repo}/assignees/{human}")
    if project_number:
        project = gh.run("project", "view", str(project_number), "--owner", owner, "--format", "json")
    else:
        data = gh.run("project", "list", "--owner", owner, "--limit", "1000", "--format", "json")
        if len(data["projects"]) >= 1000:
            raise Invalid("Project-list limit reached; pass --project explicitly")
        title = f"Remora — {repo}"
        found = [p for p in data["projects"] if p["title"] == title]
        if len(found) > 1:
            raise Invalid("Several projects match; pass --project explicitly")
        project = found[0] if found else gh.run("project", "create", "--owner", owner, "--title", title, "--format", "json")
    if project.get("closed"):
        raise Invalid("Selected Project is closed")
    number = str(project["number"])
    data = gh.run("project", "item-list", number, "--owner", owner, "--limit", "1000", "--format", "json")
    if data.get("totalCount", len(data["items"])) > len(data["items"]):
        raise Invalid("Project-item limit reached; use a smaller dedicated Project")
    fields = project_fields(gh, project, owner, empty=not data["items"])
    existing_items = unique(data["items"], lambda x: x.get("content", {}).get("url"), "Project issue item")
    gh.run("project", "link", number, "--owner", owner, "--repo", repo)
    for milestone in manifest["milestones"]:
        if milestone["title"] not in milestones:
            milestones[milestone["title"]] = gh.rest(f"repos/{repo}/milestones", {
                "title": milestone["title"], "description": milestone["description"]})
    for task in manifest["tasks"]:
        task_id = task["id"]
        if task_id not in issues:
            milestone = next(m for m in manifest["milestones"] if m["id"] == task["milestone"])
            issues[task_id] = gh.rest(f"repos/{repo}/issues", {
                "title": f"[{task_id}] {task['title']}", "body": issue_body(task, manifest["source_sha256"]),
                "milestone": milestones[milestone["title"]]["number"], "assignees": [human]})
        issue = issues[task_id]
        item = existing_items.get(issue["html_url"])
        if not item:
            item = gh.run("project", "item-add", number, "--owner", owner, "--url", issue["html_url"], "--format", "json")
        # Preserve every nonempty status on reruns, including Done and active work.
        if not item.get("status"):
            todo = next(o["id"] for o in fields["Status"]["options"] if o["name"] == "Todo")
            gh.run("project", "item-edit", "--id", item["id"], "--project-id", project["id"],
                   "--field-id", fields["Status"]["id"], "--single-select-option-id", todo)
    return {"repository": repo, "project_number": project["number"], "project_id": project["id"],
            "project_url": project.get("url"), "issues": {k: v["html_url"] for k, v in issues.items()},
            "next": "In the Project UI choose Board layout, group by Status, and save the view. Confirm P01 allocation before assignment."}
