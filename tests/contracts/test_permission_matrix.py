"""Standard-library checks for the P01 permission matrix, pins and interface index.

These tests check structure and internal consistency against the P01 research
evidence. They do not establish that GitHub behaves as documented; live
behaviour belongs to P02a/P02b and later qualification.
"""

import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "contracts" / "permission-matrix.v1.json"
SCHEMA = ROOT / "contracts" / "permission-matrix.schema.json"
PINS = ROOT / "contracts" / "upstream-pins.v1.json"
INTERFACES = ROOT / "contracts" / "interfaces.v1.json"
EVIDENCE = ROOT / "docs" / "research" / "P01" / "permission-evidence.json"
PINS_WEAVE = ROOT / "docs" / "research" / "P01" / "pins-weave.json"
PINS_UPSTREAM = ROOT / "docs" / "research" / "P01" / "pins-upstream.json"

SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
REQUIRED_ROLES = {
    "setup-operator", "supervisor-runtime", "actions-publisher-fallback", "developer-sandbox",
    "reviewer-sandbox", "trusted-ci", "human-integrator", "projection-only",
}
SANDBOX_ROLES = ("developer-sandbox", "reviewer-sandbox")
KNOWN_TASKS = {"P01", "P02a", "P02b", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10", "P11", "P12"}


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# --- Minimal JSON Schema subset validator (fails closed on unknown keywords) ---

ANNOTATIONS = {"$schema", "$id", "title", "description", "$comment", "default", "examples"}
SUPPORTED = {"type", "required", "properties", "additionalProperties", "items", "enum", "const", "pattern",
             "minItems", "uniqueItems", "minLength", "minProperties", "$ref", "$defs"}
TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def schema_errors(instance, schema, root, path="$"):
    unknown = set(schema) - SUPPORTED - ANNOTATIONS
    if unknown:
        raise AssertionError("Unsupported schema keyword(s) %s at %s" % (sorted(unknown), path))
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise AssertionError("Only local $defs references are supported: %s" % ref)
        return schema_errors(instance, root["$defs"][ref[len("#/$defs/"):]], root, path)
    errors = []
    if "type" in schema:
        allowed = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(TYPES[t](instance) for t in allowed):
            return ["%s: expected type %s" % (path, allowed)]
    if "const" in schema and instance != schema["const"]:
        errors.append("%s: expected const %r" % (path, schema["const"]))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("%s: %r not in enum" % (path, instance))
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append("%s: string too short" % path)
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append("%s: %r does not match %s" % (path, instance, schema["pattern"]))
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append("%s: fewer than %d items" % (path, schema["minItems"]))
        if schema.get("uniqueItems"):
            seen = [json.dumps(item, sort_keys=True) for item in instance]
            if len(seen) != len(set(seen)):
                errors.append("%s: duplicate items" % path)
        if "items" in schema:
            for index, item in enumerate(instance):
                errors += schema_errors(item, schema["items"], root, "%s[%d]" % (path, index))
    if isinstance(instance, dict):
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append("%s: fewer than %d properties" % (path, schema["minProperties"]))
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("%s: missing required %r" % (path, key))
        properties = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                errors += schema_errors(value, properties[key], root, "%s.%s" % (path, key))
            elif extra is False:
                errors.append("%s: unexpected property %r" % (path, key))
            elif isinstance(extra, dict):
                errors += schema_errors(value, extra, root, "%s.%s" % (path, key))
    return errors


class Fixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = load(MATRIX)
        cls.schema = load(SCHEMA)
        cls.evidence = load(EVIDENCE)
        cls.source_ids = {s["id"] for s in cls.evidence["sources"]}
        cls.evidence_permissions = {}
        for item in cls.evidence["permissions"]:
            cls.evidence_permissions.setdefault((item["resource"], item["credential"]), []).append(item)

    def placements(self):
        return self.matrix["placements"].items()

    def all_roles(self):
        for name, placement in self.placements():
            for role in placement["roles"]:
                yield name, role

    def rulesets(self):
        return {r["id"]: r for r in self.matrix["rulesets"]}


class SchemaTests(Fixtures):
    """(1) The matrix satisfies the key structural rules of its JSON Schema."""

    def test_schema_declares_draft_2020_12(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_matrix_validates_against_schema(self):
        self.assertEqual(schema_errors(self.matrix, self.schema, self.schema), [])

    def test_validator_is_not_vacuous(self):
        broken = copy.deepcopy(self.matrix)
        del broken["decision_points"]
        broken["unexpected"] = True
        broken["placements"]["supervisor_hosted"]["roles"][0]["phase"] = "always"
        broken["placements"]["actions_hosted"]["roles"][1]["permissions"].append({"credential_type": "github_app_installation"})
        errors = schema_errors(broken, self.schema, self.schema)
        joined = "\n".join(errors)
        for fragment in ("missing required 'decision_points'", "unexpected property 'unexpected'",
                         "'always' not in enum", "missing required 'permission_name'"):
            self.assertIn(fragment, joined)


class EvidenceResolutionTests(Fixtures):
    """(2) Sources resolve to permission-evidence.json and names match the evidence."""

    def test_every_permission_matches_evidence_for_its_credential_type(self):
        for placement, role in self.all_roles():
            for perm in role["permissions"]:
                where = "%s/%s/%s/%s" % (placement, role["id"], perm["credential_type"], perm["resource"])
                self.assertIn(perm["credential_type"], role["credential_types"], where)
                self.assertIn(perm["source"], self.source_ids, where)
                candidates = self.evidence_permissions.get((perm["resource"], perm["credential_type"]))
                self.assertTrue(candidates, "no evidence row for " + where)
                match = [c for c in candidates if c["permission_name"] == perm["permission_name"]
                         and c["source"] == perm["source"] and perm["level"] in c["levels"]]
                self.assertTrue(match, "permission name/level/source not in evidence: " + where)
                self.assertFalse(perm["permission_name"].startswith("("), "documented gap used as permission: " + where)
                if "parameter_name" in perm:
                    self.assertEqual(perm["parameter_name"], match[0].get("parameter_name"), where)

    def test_all_other_source_references_resolve(self):
        refs = []
        for procedure in self.matrix["expiry_revocation_procedures"].values():
            refs += procedure["sources"]
        for ruleset in self.matrix["rulesets"]:
            refs += ruleset["sources"]
        for point in self.matrix["decision_points"]:
            refs += point["sources"]
        self.assertTrue(refs)
        self.assertEqual(sorted(set(refs) - self.source_ids), [])

    def test_conditional_permissions_reference_real_decision_options(self):
        options = {p["id"]: {o["id"] for o in p["options"]} for p in self.matrix["decision_points"]}
        for placement, role in self.all_roles():
            for perm in role["permissions"]:
                if "when" in perm:
                    point, option = perm["when"]["decision_point"], perm["when"]["option"]
                    self.assertIn(point, options, role["id"])
                    self.assertIn(option, options[point], role["id"])

    def test_expiry_references_cover_role_credentials(self):
        table = self.matrix["expiry_revocation_procedures"]
        self.assertEqual(set(table), set(self.matrix["credential_types"]))
        for placement, role in self.all_roles():
            self.assertEqual(set(role["expiry_revocation"]["procedures"]), set(role["credential_types"]), role["id"])

    def test_rulesets_use_documented_rule_and_bypass_vocabulary(self):
        documented = self.evidence["rulesets"]
        for ruleset in self.matrix["rulesets"]:
            self.assertLessEqual(set(ruleset["rules"]), set(documented["rule_types"]), ruleset["id"])
            for actor in ruleset["bypass_actors"]:
                self.assertIn(actor["actor_type"], documented["bypass_actor_types_rest"], ruleset["id"])
                self.assertIn(actor["bypass_mode"], documented["bypass_modes"], ruleset["id"])
                self.assertNotEqual(actor["bypass_mode"], "exempt", "exempt leaves no audit entry")

    def test_matrix_carries_every_evidence_unverified_item(self):
        self.assertLessEqual(set(self.evidence["unverified"]), set(self.matrix["unverified"]))


class SingleAuthorityTests(Fixtures):
    """(3) Per placement, one state-branch writer, one candidate publisher, one writer per state kind."""

    def test_exactly_one_default_placement_and_required_roles(self):
        defaults = [name for name, p in self.placements() if p["default"]]
        self.assertEqual(defaults, ["supervisor_hosted"])
        union = set()
        for name, placement in self.placements():
            ids = [r["id"] for r in placement["roles"]]
            self.assertEqual(len(ids), len(set(ids)), name)
            union |= set(ids)
        self.assertEqual(union, REQUIRED_ROLES)
        supervisor_ids = {r["id"] for r in self.matrix["placements"]["supervisor_hosted"]["roles"]}
        self.assertNotIn("actions-publisher-fallback", supervisor_ids)

    def test_single_writer_per_single_authority_capability(self):
        for name, placement in self.placements():
            for capability in ("state_branch_write", "candidate_publication"):
                holders = [r["id"] for r in placement["roles"] if capability in r["authorities"]]
                self.assertEqual(len(holders), 1, "%s %s: %s" % (name, capability, holders))
            for capability in self.matrix["single_authority_capabilities"]:
                holders = [r["id"] for r in placement["roles"] if capability in r["authorities"]]
                self.assertLessEqual(len(holders), 1, "%s %s: %s" % (name, capability, holders))

    def test_state_branch_writer_differs_by_placement(self):
        writers = {name: [r["id"] for r in p["roles"] if "state_branch_write" in r["authorities"]][0]
                   for name, p in self.placements()}
        self.assertEqual(writers, {"supervisor_hosted": "supervisor-runtime",
                                   "actions_hosted": "actions-publisher-fallback"})

    def test_authority_map_has_one_writer_per_authoritative_state_kind(self):
        kinds = {k["id"]: k for k in self.matrix["state_kinds"]}
        for name, placement in self.placements():
            roles = {r["id"]: r for r in placement["roles"]}
            amap = placement["authority_map"]
            self.assertEqual(set(amap), set(kinds), name)
            for kind_id, entry in amap.items():
                kind = kinds[kind_id]
                if kind["authoritative"]:
                    writer = entry["writer_role"]
                    self.assertIn(writer, roles, "%s/%s" % (name, kind_id))
                    capability = kind["required_capability"]
                    self.assertIn(capability, roles[writer]["authorities"], "%s/%s" % (name, kind_id))
                    others = [r for r in roles if r != writer and capability in roles[r]["authorities"]]
                    self.assertEqual(others, [], "%s/%s second authority" % (name, kind_id))
                    self.assertNotIn("projection_writers", entry)
                else:
                    self.assertIsNone(entry["writer_role"], "%s/%s projection has no authority" % (name, kind_id))
                    self.assertTrue(set(kind["derived_from"]) <= set(kinds))
                    for writer in entry["projection_writers"]:
                        self.assertIn("board_projection", roles[writer]["authorities"])
            self.assertEqual(roles["projection-only"]["authorities"], ["board_projection"], name)

    def test_only_the_state_writer_bypasses_writer_rulesets(self):
        for name, placement in self.placements():
            for ruleset_id, capability in (("RS-state-writers", "state_branch_write"),
                                           ("RS-candidates-writers", "candidate_publication")):
                bypassers = [r["id"] for r in placement["roles"]
                             if {"ruleset": ruleset_id, "relation": "bypass_actor"} in r["enforcement"]]
                holders = [r["id"] for r in placement["roles"] if capability in r["authorities"]]
                self.assertEqual(bypassers, holders, "%s %s" % (name, ruleset_id))
            for role in placement["roles"]:
                for item in role["enforcement"]:
                    if item["ruleset"] in ("RS-main", "RS-state-immutable", "RS-candidates-immutable"):
                        self.assertNotEqual(item["relation"], "bypass_actor", "%s/%s" % (name, role["id"]))
        for ruleset_id in ("RS-main", "RS-state-immutable", "RS-candidates-immutable"):
            self.assertEqual(self.rulesets()[ruleset_id]["bypass_actors"], [], ruleset_id)

    def test_enforcement_references_existing_rulesets(self):
        known = self.rulesets()
        for placement, role in self.all_roles():
            for item in role["enforcement"]:
                self.assertIn(item["ruleset"], known, role["id"])


class SandboxTests(Fixtures):
    """(4) Developer/reviewer sandboxes hold no credential with write permissions."""

    def test_sandboxes_have_no_credentials_or_authority(self):
        seen = set()
        for placement, role in self.all_roles():
            if role["id"] in SANDBOX_ROLES:
                seen.add(role["id"])
                self.assertEqual(role["credential_types"], ["none"], role["id"])
                self.assertEqual(role["permissions"], [], role["id"])
                self.assertEqual(role["authorities"], [], role["id"])
                self.assertFalse(any(e["relation"] == "bypass_actor" for e in role["enforcement"]))
                self.assertTrue(any("GitHub token" in m for m in role["must_not_have"]), role["id"])
        self.assertEqual(seen, set(SANDBOX_ROLES))

    def test_no_write_level_permission_on_any_sandbox(self):
        writes = set(self.matrix["write_levels"])
        for placement, role in self.all_roles():
            if role["id"] in SANDBOX_ROLES:
                self.assertFalse([p for p in role["permissions"] if p["level"] in writes])


class SetupRuntimeSeparationTests(Fixtures):
    """(5) Setup-only permissions never appear on runtime roles."""

    def test_setup_only_permissions_absent_from_runtime_roles(self):
        setup_only = {(item["resource"], level) for item in self.matrix["setup_only_permissions"]
                      for level in item["levels"]}
        for placement, role in self.all_roles():
            if role["phase"] == "runtime":
                held = {(p["resource"], p["level"]) for p in role["permissions"]}
                self.assertEqual(held & setup_only, set(), "%s/%s" % (placement, role["id"]))
                self.assertNotIn("setup", role["authorities"], role["id"])

    def test_phases(self):
        for placement, role in self.all_roles():
            expected = "setup" if role["id"] == "setup-operator" else "runtime"
            self.assertEqual(role["phase"], expected, role["id"])

    def test_setup_role_holds_setup_only_permissions(self):
        setup = [r for r in self.matrix["placements"]["supervisor_hosted"]["roles"] if r["id"] == "setup-operator"][0]
        self.assertIn(("rulesets_admin", "write"), {(p["resource"], p["level"]) for p in setup["permissions"]})


class MainRulesetTests(Fixtures):
    """(6) Contents write includes merge, so every holder declares the main ruleset."""

    def test_contents_write_holders_are_subject_to_main_ruleset(self):
        main_rulesets = {r["id"] for r in self.matrix["rulesets"] if "refs/heads/main" in r["target_refs"]}
        self.assertTrue(main_rulesets)
        evidence = [p for p in self.evidence["permissions"]
                    if p["resource"] == "contents" and p["credential"] == "fine_grained_pat"][0]
        self.assertIn("pulls/{pull_number}/merge", evidence["notes"])
        checked = 0
        for placement, role in self.all_roles():
            writes_contents = any(p["resource"] == "contents" and p["level"] in ("write", "full")
                                  for p in role["permissions"])
            if writes_contents or "repository_role" in role:
                checked += 1
                declared = [e for e in role["enforcement"] if e["ruleset"] in main_rulesets]
                self.assertTrue(declared, "%s/%s lacks a main ruleset" % (placement, role["id"]))
                self.assertFalse([e for e in declared if e["relation"] == "bypass_actor"])
        self.assertGreater(checked, 0)


class VersionAndDecisionTests(Fixtures):
    """(7) Semver matrix version; undecided parameters stay explicit decision points."""

    def test_matrix_version_is_semver(self):
        self.assertRegex(self.matrix["matrix_version"], SEMVER)
        self.assertEqual(self.matrix["schema_version"], 1)

    def test_decision_points_present_and_undecided_ones_are_open(self):
        points = self.matrix["decision_points"]
        self.assertTrue(points)
        ids = [p["id"] for p in points]
        self.assertEqual(len(ids), len(set(ids)))
        for point in points:
            options = [o["id"] for o in point["options"]]
            self.assertGreaterEqual(len(options), 2, point["id"])
            self.assertIn(point["recommended"], options, point["id"])
            if point["status"] == "undecided":
                self.assertNotIn("decision", point, point["id"])
            else:
                self.assertIn(point.get("decision"), options, point["id"])
                self.assertTrue(point.get("decision_record"), point["id"])
        if any(p["status"] == "undecided" for p in points):
            self.assertEqual(self.matrix["status"], "proposed")
        parameters = {p["parameter"] for p in points}
        for required in ("project_owner", "supervisor_credential_kind", "candidate_workflow_edits",
                         "admin_bypass", "app_key_as_actions_secret"):
            self.assertIn(required, parameters)

    def test_bootstrap_profile_is_recorded_not_promoted(self):
        profile = self.matrix["bootstrap_profile"]
        self.assertEqual(profile["repository"], "quaat/remora")
        self.assertIsNone(profile["github_app"])
        self.assertFalse(profile["autonomous_execution"])
        self.assertEqual({c["credential_type"] for c in profile["credentials"]}, {"oauth_gh_cli"})
        self.assertLessEqual({"repo", "project"}, set(profile["credentials"][0]["scopes_reported"]))
        ids = {p["id"] for p in self.matrix["decision_points"]}
        self.assertLessEqual(set(profile["decision_point_values"]), ids)


class PinConsistencyTests(unittest.TestCase):
    """(8) The consolidated pin file equals the two research pin files."""

    def test_consolidated_pins_match_research_files(self):
        pins, weave, upstream = load(PINS), load(PINS_WEAVE), load(PINS_UPSTREAM)
        self.assertEqual(pins["schema_version"], 1)
        expected = {p["name"]: p for p in weave["pins"] + upstream["pins"]}
        actual = {p["name"]: p for p in pins["pins"]}
        self.assertEqual(len(actual), len(pins["pins"]), "duplicate pin names")
        self.assertEqual(actual, expected)
        self.assertEqual(pins["related_fetches"], weave["related_fetches"])
        self.assertEqual(pins["documentation_fetches"], upstream["documentation_fetches"])
        self.assertEqual(pins["pinned_at"], max(p["fetched_at"] for p in expected.values()))
        for pin in pins["pins"]:
            self.assertRegex(pin["commit"], r"^[0-9a-f]{40}$")
            self.assertRegex(pin["license"]["sha256"], r"^[0-9a-f]{64}$")


class InterfaceIndexTests(unittest.TestCase):
    """The internal interface index is well formed and names owners and consumers."""

    def test_interface_index_structure(self):
        index = load(INTERFACES)
        self.assertEqual(index["schema_version"], 1)
        ids = [i["id"] for i in index["interfaces"]]
        self.assertEqual(len(ids), len(set(ids)))
        for required in ("state-backend", "publisher", "execution", "reviewer-launch", "command-ingestion",
                         "board-projection", "plan-compiler", "evidence-records", "trusted-evidence"):
            self.assertIn(required, ids)
        for interface in index["interfaces"]:
            self.assertTrue(interface["owner_module"].startswith("src/remora/"), interface["id"])
            self.assertIn(interface["owner_task"], KNOWN_TASKS, interface["id"])
            self.assertTrue(interface["consumers"], interface["id"])
            self.assertLessEqual(set(interface["consumers"]), KNOWN_TASKS, interface["id"])
            self.assertEqual(interface["status"], "proposed")
            names = [op["name"] for op in interface["operations"]]
            self.assertEqual(len(names), len(set(names)), interface["id"])
            for operation in interface["operations"]:
                for key in ("inputs", "outputs", "errors"):
                    self.assertIsInstance(operation[key], list, "%s.%s" % (interface["id"], operation["name"]))
        execution = [i for i in index["interfaces"] if i["id"] == "execution"][0]
        self.assertLessEqual({"start", "checkpoint", "stop_request", "stop_confirmed", "authority_lost"},
                             {op["name"] for op in execution["operations"]})
        self.assertIn("P02b", execution["consumers"])


if __name__ == "__main__":
    unittest.main()
