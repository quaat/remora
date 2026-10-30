"""Every unverified item from the P01 research has a stable ID and a documented route.

Standard library only. These tests check document cross-references, not the truth of the
items themselves.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P01 = ROOT / "docs" / "research" / "P01"
ROUTING = P01 / "unverified-routing.json"
EVIDENCE = P01 / "permission-evidence.json"
UPSTREAM = P01 / "upstream-surfaces.md"
INVENTORY = P01 / "weave-inventory.md"
MATRIX = ROOT / "contracts" / "permission-matrix.v1.json"
ROUTE_DOCUMENTS = {"handoff-P02a.md", "handoff-P02b.md", "handoff-P03.md", "README.md"}


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def section(text, heading_pattern):
    match = re.search(heading_pattern, text, re.M)
    if not match:
        raise AssertionError("missing section " + heading_pattern)
    rest = text[match.end():]
    end = re.search(r"^## ", rest, re.M)
    return rest[:end.start()] if end else rest


def mentions(text, item_id):
    return re.search(r"(?<![A-Za-z0-9-])%s(?![0-9])" % re.escape(item_id), text) is not None


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routing = json.loads(read(ROUTING))
        cls.items = cls.routing["items"]
        cls.by_source = {}
        for item in cls.items:
            cls.by_source.setdefault(item["source"], []).append(item)

    def test_ids_are_unique_and_stable_format(self):
        ids = [i["id"] for i in self.items]
        self.assertEqual(len(ids), len(set(ids)))
        for item_id in ids:
            self.assertRegex(item_id, r"^U-(PE|US|WI|PM)-[0-9]{2}$")

    def test_every_permission_evidence_item_has_an_id(self):
        evidence = json.loads(read(EVIDENCE))["unverified"]
        routed = self.by_source["docs/research/P01/permission-evidence.json"]
        self.assertEqual([i["text"] for i in routed], evidence)
        self.assertEqual([i["source_ref"] for i in routed], ["unverified[%d]" % n for n in range(len(evidence))])

    def test_every_upstream_section5_item_has_an_id(self):
        body = section(read(UPSTREAM), r"^## 5\. Unknowns.*$")
        numbers = [int(n) for n in re.findall(r"^([0-9]+)\. \*\*", body, re.M)]
        self.assertTrue(numbers)
        routed = self.by_source["docs/research/P01/upstream-surfaces.md"]
        self.assertEqual([i["source_ref"] for i in routed], ["§5 item %d" % n for n in numbers])

    def test_every_inventory_section_h_bullet_has_an_id(self):
        body = section(read(INVENTORY), r"^## H\. Unknowns.*$")
        titles = [t.rstrip(".") for t in re.findall(r"^- \*\*(.+?)\*\*", body, re.M)]
        self.assertTrue(titles)
        routed = self.by_source["docs/research/P01/weave-inventory.md"]
        self.assertEqual([i["source_ref"] for i in routed], ["§H '%s'" % t for t in titles])

    def test_each_id_appears_where_it_is_routed(self):
        readme = read(P01 / "README.md")
        for item in self.items:
            self.assertTrue(set(item["documented_in"]) <= ROUTE_DOCUMENTS, item["id"])
            self.assertTrue(item["documented_in"], item["id"])
            for name in item["documented_in"]:
                self.assertTrue(mentions(read(P01 / name), item["id"]), "%s missing from %s" % (item["id"], name))
            self.assertTrue(mentions(readme, item["id"]), "%s missing from README" % item["id"])
            for task, handoff in (("P02a", "handoff-P02a.md"), ("P02b", "handoff-P02b.md")):
                if any(route.startswith(task) for route in item["routed_to"]):
                    self.assertIn(handoff, item["documented_in"], item["id"])


class MatrixUnverifiedTests(unittest.TestCase):
    """Role- and ruleset-level unverified entries in the matrix carry a routed ID."""

    ENTRY = re.compile(r"^(U-(?:PE|US|WI|PM)-[0-9]{2})(?:, (U-(?:PE|US|WI|PM)-[0-9]{2}))*: \S")

    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(read(MATRIX))
        cls.routing = {i["id"]: i for i in json.loads(read(ROUTING))["items"]}
        cls.entries = []
        for ruleset in cls.matrix["rulesets"]:
            cls.entries += [("ruleset " + ruleset["id"], u) for u in ruleset["unverified"]]
        for name, placement in cls.matrix["placements"].items():
            for role in placement["roles"]:
                cls.entries += [("%s/%s" % (name, role["id"]), u) for u in role["unverified"]]

    def cited(self, entry):
        return re.findall(r"U-(?:PE|US|WI|PM)-[0-9]{2}", entry.split(": ", 1)[0])

    def test_every_matrix_entry_cites_a_routed_id(self):
        self.assertTrue(self.entries)
        for where, entry in self.entries:
            self.assertRegex(entry, self.ENTRY, where)
            for item_id in self.cited(entry):
                self.assertIn(item_id, self.routing, "%s cites unknown %s" % (where, item_id))

    def test_every_matrix_level_item_is_cited_and_documented(self):
        cited = {i for _, entry in self.entries for i in self.cited(entry)}
        for item_id, item in self.routing.items():
            if item["source"] == "contracts/permission-matrix.v1.json":
                self.assertIn(item_id, cited, "%s is not cited by any matrix entry" % item_id)
                self.assertTrue(any(item["text"] in entry for _, entry in self.entries), item_id)

    def test_evidence_list_is_carried_verbatim_at_top_level(self):
        evidence = json.loads(read(EVIDENCE))["unverified"]
        self.assertLessEqual(set(evidence), set(self.matrix["unverified"]))


class DocumentConsistencyTests(unittest.TestCase):
    def test_p02a_weave_sloc_subtotal_is_the_sum_of_its_parts(self):
        body = section(read(P01 / "handoff-P02a.md"), r"^## 3\. Weave numbers.*$")
        parts = [int(n) for n in re.findall(r"^\| [^*|][^|]* \| ([0-9]+) \|$", body, re.M)]
        subtotal = re.search(r"\*\*Subtotal \(upper bound\)\*\* \| \*\*([0-9]+)\*\* \(\+([0-9]+) with `reconcile.py` = ([0-9]+)\)", body)
        self.assertTrue(parts and subtotal)
        self.assertEqual(sum(parts), int(subtotal.group(1)))
        self.assertEqual(int(subtotal.group(1)) + int(subtotal.group(2)), int(subtotal.group(3)))

    def test_weave_sloc_totals_and_parts_agree_across_documents(self):
        documents = [P01 / "handoff-P02a.md", P01 / "contract-comparison.md", P01 / "weave-inventory.md",
                     ROOT / "docs" / "decisions" / "0003-backend-preference-and-authority.md"]
        parts = [168, 106, 106, 28, 34, 265]
        reconcile = 121
        subtotal, total = sum(parts), sum(parts) + reconcile
        self.assertEqual((subtotal, total), (707, 828))
        for path in documents:
            text = read(path)
            for number in set(parts) | {reconcile, subtotal, total}:
                self.assertRegex(text, r"(?<![0-9.:-])%d(?![0-9])" % number, "%s lacks %d" % (path.name, number))
            for stale in (610, 731):
                self.assertNotRegex(text, r"(?<![0-9.:,-])%d(?![0-9])" % stale, "%s has stale total %d" % (path.name, stale))

    def test_every_matrix_decision_point_is_a_readme_question(self):
        readme = read(P01 / "README.md")
        for point in json.loads(read(MATRIX))["decision_points"]:
            self.assertTrue(mentions(readme, point["id"]), point["id"])


if __name__ == "__main__":
    unittest.main()
