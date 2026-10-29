import copy
import json
import subprocess
import unittest
from unittest.mock import patch

from bootstrap.core import Invalid, STATUSES, load
from bootstrap.github import GitHub, apply, managed_issues, preview


class FakeGitHub:
    """Persist remote state across setup calls, including partial failures."""

    def __init__(self):
        self.milestones = []
        self.issues = []
        self.projects = []
        self.items = []
        self.fields = [{"id": "status", "name": "Status", "type": "ProjectV2SingleSelectField",
                        "options": [{"id": "todo", "name": "Todo"}]}]
        self.writes = []
        self.fail_after_issue_create = False

    def rest(self, path, payload=None):
        if payload is None:
            if "/assignees/" in path:
                return None
            return {"full_name": "owner/remora", "archived": False, "has_issues": True}
        self.writes.append((path, copy.deepcopy(payload)))
        if path.endswith("/milestones"):
            result = {**payload, "number": len(self.milestones) + 1}
            self.milestones.append(result)
        elif path.endswith("/issues"):
            result = {**payload, "number": len(self.issues) + 1,
                      "html_url": f"https://github.com/owner/remora/issues/{len(self.issues)+1}"}
            self.issues.append(result)
            if self.fail_after_issue_create:
                self.fail_after_issue_create = False
                raise Invalid("Simulated lost acknowledgment after commit")
        else:
            raise AssertionError(path)
        return copy.deepcopy(result)

    def pages(self, path):
        return copy.deepcopy(self.milestones if "/milestones?" in path else self.issues)

    def graphql(self, query, variables):
        self.writes.append(("graphql", copy.deepcopy(variables)))
        self.fields[0]["options"] = [{**o, "id": f"option-{i}"}
                                     for i, o in enumerate(variables["input"]["singleSelectOptions"])]
        return {"updateProjectV2Field": {"projectV2Field": {"id": "status"}}}

    def run(self, *args, payload=None):
        def arg(name):
            return args[args.index(name) + 1]
        action = args[1]
        if action == "list":
            return {"projects": copy.deepcopy(self.projects)}
        if action == "create":
            result = {"id": "project-1", "number": 1, "title": arg("--title"),
                      "url": "https://github.com/users/owner/projects/1", "closed": False}
            self.projects.append(result)
        elif action == "view":
            return copy.deepcopy(self.projects[0])
        elif action == "item-list":
            return {"items": copy.deepcopy(self.items), "totalCount": len(self.items)}
        elif action == "field-list":
            return {"fields": copy.deepcopy(self.fields)}
        elif action == "field-create":
            result = {"id": arg("--name"), "name": arg("--name"), "type": "ProjectV2Field"}
            self.fields.append(result)
        elif action == "link":
            result = None
        elif action == "item-add":
            result = {"id": f"item-{len(self.items)+1}", "content": {"url": arg("--url")}}
            self.items.append(result)
        elif action == "item-edit":
            item = next(i for i in self.items if i["id"] == arg("--id"))
            option = next(o for o in self.fields[0]["options"] if o["id"] == arg("--single-select-option-id"))
            item["status"] = option["name"]
            result = None
        else:
            raise AssertionError(args)
        self.writes.append((action, args))
        return copy.deepcopy(result)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load()
        self.gh = FakeGitHub()

    def run_apply(self):
        return apply(self.manifest, "owner/remora", "owner", "human", None, self.gh)

    def test_offline_preview_does_not_construct_transport(self):
        with patch("bootstrap.github.GitHub", side_effect=AssertionError("network")):
            result = preview(self.manifest, "owner/remora", "owner", "human", None)
        self.assertEqual(result["mode"], "dry_run_no_network")
        self.assertEqual(len(result["issues"]), 13)

    def test_invalid_repository_cannot_be_shell_or_url(self):
        with self.assertRaises(Invalid):
            preview(self.manifest, "https://github.com/owner/remora;echo no", "owner", "human", None)

    def test_first_import_creates_complete_backlog(self):
        result = self.run_apply()
        self.assertEqual(len(self.gh.milestones), 5)
        self.assertEqual(len(self.gh.issues), 13)
        self.assertEqual(len(self.gh.items), 13)
        self.assertEqual(len(result["issues"]), 13)
        self.assertTrue(all(i["status"] == "Todo" for i in self.gh.items))
        self.assertEqual([o["name"] for o in self.gh.fields[0]["options"]], list(STATUSES))

    def test_rerun_preserves_active_status_and_issue_edits(self):
        self.run_apply()
        self.gh.items[0]["status"] = "In Progress"
        self.gh.issues[0]["body"] += "\nMaintainer notes preserved."
        self.gh.writes.clear()
        self.run_apply()
        self.assertEqual(len(self.gh.issues), 13)
        self.assertEqual(len(self.gh.items), 13)
        self.assertEqual(len(self.gh.projects), 1)
        self.assertEqual(self.gh.items[0]["status"], "In Progress")
        self.assertTrue(self.gh.issues[0]["body"].endswith("Maintainer notes preserved."))
        self.assertEqual([w[0] for w in self.gh.writes], ["link"])

    def test_lost_create_ack_is_reused_on_sequential_retry(self):
        self.gh.fail_after_issue_create = True
        with self.assertRaisesRegex(Invalid, "lost acknowledgment"):
            self.run_apply()
        self.assertEqual(len(self.gh.issues), 1)
        self.run_apply()
        self.assertEqual(len(self.gh.issues), 13)
        self.assertEqual(len(self.gh.items), 13)

    def test_missing_initial_status_repaired_after_interrupted_add(self):
        self.run_apply()
        del self.gh.items[0]["status"]
        self.run_apply()
        self.assertEqual(self.gh.items[0]["status"], "Todo")

    def test_duplicate_markers_fail_before_mutation(self):
        self.run_apply()
        self.gh.issues.append(copy.deepcopy(self.gh.issues[0]))
        self.gh.writes.clear()
        with self.assertRaisesRegex(Invalid, "Duplicate"):
            self.run_apply()
        self.assertEqual(self.gh.writes, [])

    def test_missing_marker_does_not_create_a_second_task(self):
        self.gh.issues.append({"title": "[P01] Existing task", "body": "marker removed"})
        with self.assertRaisesRegex(Invalid, "no Remora marker"):
            self.run_apply()
        self.assertEqual(self.gh.writes, [])

    def test_changed_task_digest_fails_before_mutation(self):
        self.run_apply()
        self.gh.issues[0]["body"] = self.gh.issues[0]["body"].replace("Task SHA-256:", "old digest:")
        self.gh.writes.clear()
        with self.assertRaisesRegex(Invalid, "digest differs"):
            self.run_apply()
        self.assertEqual(self.gh.writes, [])

    def test_populated_project_fields_are_not_replaced(self):
        self.run_apply()
        self.gh.fields[0]["options"] = self.gh.fields[0]["options"][:1]
        self.gh.writes.clear()
        with self.assertRaisesRegex(Invalid, "Add them manually"):
            self.run_apply()
        self.assertEqual(self.gh.writes, [])

    def test_ambiguous_project_selection_fails(self):
        self.run_apply()
        self.gh.projects.append(copy.deepcopy(self.gh.projects[0]))
        self.gh.writes.clear()
        with self.assertRaisesRegex(Invalid, "Several projects"):
            self.run_apply()
        self.assertEqual(self.gh.writes, [])

    def test_pull_request_marker_is_not_imported_as_issue(self):
        self.run_apply()
        pr = {**self.gh.issues[0], "pull_request": {"url": "fixture"}}
        self.assertEqual(managed_issues([pr], self.manifest), {})


class TransportTests(unittest.TestCase):
    @patch("bootstrap.github.subprocess.run")
    def test_structured_json_payload_uses_stdin(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '{"number": 1}', "")
        body = "line one\n$(do-not-run) `literal`"
        GitHub().rest("repos/owner/remora/issues", {"body": body})
        args, kwargs = run.call_args
        self.assertEqual(args[0][-2:], ["--input", "-"])
        self.assertEqual(json.loads(kwargs["input"])["body"], body)
        self.assertEqual(kwargs["env"]["GH_HOST"], "github.com")
        self.assertNotIn("shell", kwargs)

    @patch("bootstrap.github.subprocess.run")
    def test_rest_pages_are_flattened(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '[[{"id": 1}],[{"id": 2}]]', "")
        self.assertEqual(GitHub().pages("repos/o/r/issues"), [{"id": 1}, {"id": 2}])
        self.assertIn("--paginate", run.call_args.args[0])
        self.assertIn("--slurp", run.call_args.args[0])

    @patch("bootstrap.github.subprocess.run")
    def test_graphql_errors_fail_even_with_zero_exit(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '{"errors": [{"message": "denied"}]}', "")
        with self.assertRaisesRegex(Invalid, "GraphQL"):
            GitHub().graphql("query { viewer { login } }", {})

    @patch("bootstrap.github.subprocess.run")
    def test_failed_mutation_is_not_blindly_retried(self, run):
        run.return_value = subprocess.CompletedProcess([], 1, "", "network failure")
        with self.assertRaisesRegex(Invalid, "no automatic write retry"):
            GitHub().rest("repos/o/r/issues", {"title": "task"})
        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
