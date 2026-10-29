import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from bootstrap.core import (ARCHITECTURE, PLAN, POLICY, ROOT, TASKS, Invalid, candidates,
                            check_review, digest, load, review_packet, review_template, validate)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load()
        self.source = (ROOT / PLAN).read_bytes()

    def test_complete_graph_and_source(self):
        self.assertEqual(len(validate(self.manifest, self.source)), 13)
        self.assertEqual(len(self.manifest["milestones"]), 5)
        self.assertEqual(sum(len(t["acceptance_criteria"]) for t in self.manifest["tasks"]), 38)

    def test_only_p01_initially_eligible(self):
        self.assertEqual(candidates(self.manifest, []), ["P01"])

    def test_spikes_and_schema_can_run_in_parallel(self):
        self.assertEqual(candidates(self.manifest, ["P01"]), ["P02a", "P02b", "P03"])

    def test_reviewer_does_not_wait_for_developer(self):
        tasks = candidates(self.manifest, ["P01", "P02a", "P02b", "P03", "P05"])
        self.assertIn("P06", tasks)
        self.assertIn("P08", tasks)
        self.assertNotIn("P09", tasks)

    def test_unknown_completion_fails(self):
        with self.assertRaisesRegex(Invalid, "Unknown"):
            candidates(self.manifest, ["P99"])

    def test_inconsistent_completion_fails(self):
        with self.assertRaisesRegex(Invalid, "prerequisites"):
            candidates(self.manifest, ["P05"])

    def test_plan_byte_change_fails(self):
        with self.assertRaisesRegex(Invalid, "digest"):
            validate(self.manifest, self.source + b"\n")

    def test_dependency_drift_fails(self):
        self.manifest["tasks"][0]["depends_on"] = ["P12"]
        with self.assertRaisesRegex(Invalid, "drifted"):
            validate(self.manifest, self.source)

    def test_missing_task_fails(self):
        self.manifest["tasks"].pop()
        with self.assertRaisesRegex(Invalid, "task IDs"):
            validate(self.manifest, self.source)

    def test_duplicate_criterion_fails(self):
        task = self.manifest["tasks"][0]
        task["acceptance_criteria"].append(task["acceptance_criteria"][0])
        with self.assertRaisesRegex(Invalid, "duplicate criterion"):
            validate(self.manifest, self.source)

    def test_criterion_text_drift_fails(self):
        self.manifest["tasks"][0]["acceptance_criteria"][0]["text"] = "Weakened requirement"
        with self.assertRaisesRegex(Invalid, "checklist drifted"):
            validate(self.manifest, self.source)

    def test_unrestricted_scope_fails(self):
        self.manifest["tasks"][0]["allowed_paths"] = ["**/*"]
        with self.assertRaisesRegex(Invalid, "scope path"):
            validate(self.manifest, self.source)

    def test_cycle_even_with_correspondingly_revised_source_fails(self):
        # Simulate a deliberately changed source and manifest; graph validation still applies.
        modified = self.source.replace(b"**Dependencies:** none.", b"**Dependencies:** P02a.", 1)
        self.manifest["source_sha256"] = digest(modified)
        task = self.manifest["tasks"][0]
        task["depends_on"] = ["P02a"]
        task["source_excerpt"] = task["source_excerpt"].replace("**Dependencies:** none.", "**Dependencies:** P02a.")
        with self.assertRaisesRegex(Invalid, "cycle"):
            validate(self.manifest, modified)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in (PLAN, TASKS, POLICY, ARCHITECTURE):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "baseline")
        self.base = self.run_git("rev-parse", "HEAD").strip()
        (self.root / "result.txt").write_text("P01 fixture deliverable\n")
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "candidate")
        self.packet = review_packet(self.root, "P01", self.base, "developer-session")
        self.review = review_template(self.packet)
        self.review["reviewer"] = {"identity": "reviewer-session", "provider": "fixture", "tool_version": "1"}

    def run_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def passing_review(self):
        result = copy.deepcopy(self.review)
        result["verdict"] = "PASS"
        result["summary"] = "Fixture inspection complete"
        for criterion in result["criteria"]:
            criterion["status"] = "satisfied"
            criterion["findings"] = "Inspected fixture"
            criterion["evidence"] = [{
                "check_id": "fixture-inspection", "executor": "reviewer-session",
                "environment": "fixture-v1", "source_sha": self.packet["candidate_sha"],
                "artifact": "fixture://inspection", "provenance": "human inspection fixture",
                "exit_status": 0, "independently_executed": True,
            }]
        return result

    def test_deterministic_packet(self):
        self.assertEqual(self.packet, review_packet(self.root, "P01", self.base, "developer-session"))

    def test_unverified_is_valid_format_but_not_pass(self):
        check_review(self.packet, self.review)
        self.assertEqual(self.review["verdict"], "UNVERIFIED")

    def test_complete_pass_format(self):
        check_review(self.packet, self.passing_review())

    def test_dirty_tree_cannot_freeze(self):
        (self.root / "result.txt").write_text("changed")
        with self.assertRaisesRegex(Invalid, "working-tree"):
            review_packet(self.root, "P01", self.base, "developer")

    def test_unknown_task_fails(self):
        with self.assertRaisesRegex(Invalid, "Unknown task"):
            review_packet(self.root, "P99", self.base, "developer")

    def test_stale_candidate_rejected(self):
        self.review["candidate_sha"] = self.base
        with self.assertRaisesRegex(Invalid, "candidate_sha"):
            check_review(self.packet, self.review)

    def test_tampered_packet_rejected(self):
        self.packet["base_sha"] = "altered"
        with self.assertRaisesRegex(Invalid, "modified"):
            check_review(self.packet, self.review)

    def test_developer_cannot_self_identify_as_reviewer(self):
        self.review["reviewer"]["identity"] = "developer-session"
        with self.assertRaisesRegex(Invalid, "Developer"):
            check_review(self.packet, self.review)

    def test_missing_identity_rejected(self):
        self.review["reviewer"]["tool_version"] = "REQUIRED"
        with self.assertRaisesRegex(Invalid, "provenance"):
            check_review(self.packet, self.review)

    def test_duplicate_criteria_rejected(self):
        self.review["criteria"].append(copy.deepcopy(self.review["criteria"][0]))
        with self.assertRaisesRegex(Invalid, "duplicate"):
            check_review(self.packet, self.review)

    def test_pass_without_evidence_rejected(self):
        result = self.passing_review()
        result["criteria"][0]["evidence"] = []
        with self.assertRaisesRegex(Invalid, "missing"):
            check_review(self.packet, result)

    def test_pass_with_unverified_criterion_rejected(self):
        self.review["verdict"] = "PASS"
        with self.assertRaisesRegex(Invalid, "unverified"):
            check_review(self.packet, self.review)

    def test_supplied_logs_cannot_be_independent_pass(self):
        result = self.passing_review()
        result["criteria"][0]["evidence"][0]["independently_executed"] = False
        with self.assertRaisesRegex(Invalid, "independently executed"):
            check_review(self.packet, result)

    def test_failed_check_rejected_for_pass(self):
        result = self.passing_review()
        result["criteria"][0]["evidence"][0]["exit_status"] = 1
        with self.assertRaisesRegex(Invalid, "successful"):
            check_review(self.packet, result)

    def test_wrong_source_in_evidence_rejected(self):
        result = self.passing_review()
        result["criteria"][0]["evidence"][0]["source_sha"] = self.base
        with self.assertRaisesRegex(Invalid, "different candidate"):
            check_review(self.packet, result)

    def test_naive_boolean_string_rejected(self):
        result = self.passing_review()
        result["criteria"][0]["evidence"][0]["independently_executed"] = "true"
        with self.assertRaisesRegex(Invalid, "boolean"):
            check_review(self.packet, result)


if __name__ == "__main__":
    unittest.main()
