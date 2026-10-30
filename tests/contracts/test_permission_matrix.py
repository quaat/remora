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
TASKS = ROOT / ".remora" / "tasks.json"
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

    def test_supervisors_control_execution_in_both_placements(self):
        for name, placement in self.placements():
            supervisor = [r for r in placement["roles"] if r["id"] == "supervisor-runtime"][0]
            self.assertIn("execution_control", supervisor["authorities"], name)

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


REQUIRED_RULES = {
    "RS-state-immutable": {"deletion", "non_fast_forward"},
    "RS-candidates-immutable": {"deletion", "non_fast_forward"},
    "RS-state-writers": {"creation", "update"},
    "RS-candidates-writers": {"creation", "update"},
    "RS-main": {"pull_request", "required_status_checks", "non_fast_forward", "deletion"},
    "RS-main-integrator": {"update"},
}
HUMAN_BYPASS_ACTOR_TYPES = {"RepositoryRole", "Team"}
CONTENTS_WRITE_CAPABILITIES = {"state_branch_write", "candidate_publication", "setup"}


def holds(role, resource, levels):
    return [p for p in role["permissions"] if p["resource"] == resource and p["level"] in levels]


class ForbiddenPermissionTests(Fixtures):
    """must_not_have is backed by machine-checkable forbidden_permissions."""

    def test_permissions_never_match_forbidden_entries(self):
        for placement, role in self.all_roles():
            for forbidden in role["forbidden_permissions"]:
                for perm in holds(role, forbidden["resource"], forbidden["levels"]):
                    allowed_by = forbidden.get("unless")
                    self.assertTrue(allowed_by is not None and perm.get("when") == allowed_by,
                                    "%s/%s holds forbidden %s %s" % (placement, role["id"], perm["resource"], perm["level"]))

    def test_credentialed_runtime_roles_declare_forbidden_permissions(self):
        for placement, role in self.all_roles():
            if role["phase"] == "runtime" and role["credential_types"] != ["human_account"]:
                self.assertTrue(role["forbidden_permissions"], "%s/%s" % (placement, role["id"]))

    def test_forbidden_unless_references_real_decision_options(self):
        options = {p["id"]: {o["id"] for o in p["options"]} for p in self.matrix["decision_points"]}
        for placement, role in self.all_roles():
            for forbidden in role["forbidden_permissions"]:
                if "unless" in forbidden:
                    self.assertIn(forbidden["unless"]["option"], options[forbidden["unless"]["decision_point"]])

    def test_contents_write_only_on_publishing_or_setup_roles(self):
        for placement, role in self.all_roles():
            if holds(role, "contents", ("write", "full")):
                self.assertTrue(CONTENTS_WRITE_CAPABILITIES & set(role["authorities"]),
                                "%s/%s holds Contents write without publication authority" % (placement, role["id"]))

    def test_contents_write_forbidden_for_ci_projection_and_actions_supervisor(self):
        cases = [("supervisor_hosted", "trusted-ci"), ("actions_hosted", "trusted-ci"),
                 ("supervisor_hosted", "projection-only"), ("actions_hosted", "projection-only"),
                 ("actions_hosted", "supervisor-runtime")]
        for placement, role_id in cases:
            role = [r for r in self.matrix["placements"][placement]["roles"] if r["id"] == role_id][0]
            forbidden = {(f["resource"], level) for f in role["forbidden_permissions"] if "unless" not in f
                         for level in f["levels"]}
            self.assertLessEqual({("contents", "write"), ("contents", "full")}, forbidden, "%s/%s" % (placement, role_id))


class RulesetContentTests(Fixtures):
    """Rulesets carry their required rules and the writers are subject to the immutable ones."""

    def test_rulesets_contain_required_rules(self):
        rulesets = self.rulesets()
        for ruleset_id, required in REQUIRED_RULES.items():
            self.assertIn(ruleset_id, rulesets)
            self.assertLessEqual(required, set(rulesets[ruleset_id]["rules"]), ruleset_id)

    def test_writer_rulesets_name_exactly_one_integration_actor(self):
        rulesets = self.rulesets()
        for ruleset_id in ("RS-state-writers", "RS-candidates-writers"):
            actors = rulesets[ruleset_id]["bypass_actors"]
            self.assertEqual(len(actors), 1, ruleset_id)
            self.assertEqual(actors[0]["actor_type"], "Integration", ruleset_id)

    def test_target_refs(self):
        rulesets = self.rulesets()
        for ruleset_id in ("RS-state-immutable", "RS-state-writers"):
            self.assertEqual(rulesets[ruleset_id]["target_refs"], ["refs/heads/harness/state"])
        for ruleset_id in ("RS-candidates-immutable", "RS-candidates-writers"):
            self.assertEqual(rulesets[ruleset_id]["target_refs"], ["refs/heads/agent/**/*"])

    def test_writers_and_contents_holders_are_subject_to_immutable_rulesets(self):
        for name, placement in self.placements():
            for role in placement["roles"]:
                relations = {(e["ruleset"], e["relation"]) for e in role["enforcement"]}
                must = set()
                if "state_branch_write" in role["authorities"] or holds(role, "contents", ("write", "full")):
                    must.add(("RS-state-immutable", "subject_to"))
                if "candidate_publication" in role["authorities"] or holds(role, "contents", ("write", "full")):
                    must.add(("RS-candidates-immutable", "subject_to"))
                self.assertLessEqual(must, relations, "%s/%s" % (name, role["id"]))

    def test_main_merge_enforcement_is_an_explicit_decision(self):
        points = [p for p in self.matrix["decision_points"] if p["parameter"] == "main_merge_enforcement"]
        self.assertEqual(len(points), 1)
        point = points[0]
        for source in ("S-gh-fgpat", "S-gh-rest-pulls", "S-gh-pr-approve-required"):
            self.assertIn(source, point["sources"])
        self.assertIn("interaction", point)
        fallback = [p for p in self.matrix["decision_points"] if p["parameter"] == "main_merge_block_unavailable"]
        self.assertEqual(len(fallback), 1)
        self.assertEqual(fallback[0]["recommended"], "disable_autonomous_execution")

    def test_approval_count_never_blocks_machine_merges(self):
        """Contents write includes the merge endpoints; only an update restriction blocks machine merges."""
        evidence = [p for p in self.evidence["permissions"]
                    if p["resource"] == "contents" and p["credential"] == "fine_grained_pat"][0]
        self.assertIn("pulls/{pull_number}/merge", evidence["notes"])
        point = [p for p in self.matrix["decision_points"] if p["parameter"] == "main_merge_enforcement"][0]
        rulesets = self.rulesets()
        for option in point["options"]:
            self.assertIsInstance(option["main_update_restricted"], bool, option["id"])
            for ruleset_id in option["main_rulesets"]:
                self.assertIn("refs/heads/main", rulesets[ruleset_id]["target_refs"], option["id"])
            restricted = any("update" in rulesets[r]["rules"] for r in option["main_rulesets"])
            self.assertEqual(option["main_update_restricted"], restricted,
                             "%s: the restriction must come from the option's rulesets" % option["id"])
            self.assertEqual(option["machine_can_merge_without_bypass"], not option["main_update_restricted"],
                             option["id"])
            self.assertEqual("EXPOSURE" in option["effect"], option["machine_can_merge_without_bypass"], option["id"])
            if option["machine_can_merge_without_bypass"]:
                self.assertIn("Contents write", option["effect"], option["id"])
                self.assertIn("merge", option["effect"], option["id"])
        self.assertTrue(any(o["machine_can_merge_without_bypass"] for o in point["options"]),
                        "the exposed options must stay visible as documented alternatives")

    def test_recommended_configuration_keeps_github_merge_block(self):
        points = {p["id"]: p for p in self.matrix["decision_points"]}
        point = [p for p in points.values() if p["parameter"] == "main_merge_enforcement"][0]
        recommended = [o for o in point["options"] if o["id"] == point["recommended"]][0]
        self.assertFalse(recommended["machine_can_merge_without_bypass"])
        self.assertTrue(recommended["main_update_restricted"])
        rulesets = self.rulesets()
        restricting = [r for r in rulesets.values()
                       if "refs/heads/main" in r["target_refs"] and "update" in r["rules"]]
        self.assertEqual([r["id"] for r in restricting], ["RS-main-integrator"])
        integrator = restricting[0]
        self.assertEqual(integrator["bypass_actors"], [], "no unconditional bypass on the merge block")
        self.assertTrue(integrator["conditional_bypass_actors"])
        requirements = recommended.get("requires", [])
        for actor in integrator["conditional_bypass_actors"]:
            self.assertIn(actor["actor_type"], HUMAN_BYPASS_ACTOR_TYPES)
            self.assertEqual(actor["bypass_mode"], "pull_request")
            self.assertIn(actor["when"], requirements, "the bypass must be enabled by the recommended options")
            self.assertEqual(points[actor["when"]["decision_point"]]["recommended"], actor["when"]["option"])
        self.assertEqual(rulesets["RS-main"]["bypass_actors"], [])
        self.assertNotIn("conditional_bypass_actors", rulesets["RS-main"],
                         "a bypass on RS-main would also skip the pull-request and trusted-CI rules")
        for name, placement in self.placements():
            for role in placement["roles"]:
                relations = {(e["ruleset"], e["relation"]) for e in role["enforcement"]}
                if role["id"] == "human-integrator":
                    self.assertIn(("RS-main-integrator", "conditional_bypass_actor"), relations)
                    continue
                if role["bypass_account_credentials"]["policy"] == "holder_is_bypass_account":
                    self.assertEqual(role["id"], "setup-operator")
                    self.assertIn(("RS-main-integrator", "held_by_bypass_account"), relations)
                    self.assertEqual(role["phase"], "setup")
                    continue
                self.assertFalse([r for r in relations if r[1] in ("bypass_actor", "conditional_bypass_actor")
                                  and r[0] in ("RS-main", "RS-main-integrator")], "%s/%s" % (name, role["id"]))
                if holds(role, "contents", ("write", "full")):
                    self.assertIn(("RS-main-integrator", "subject_to"), relations, "%s/%s" % (name, role["id"]))

    def test_bypass_account_credentials_cannot_merge(self):
        """A credential of the RS-main-integrator bypass account may serve a role only without Contents write."""
        for name, placement in self.placements():
            for role in placement["roles"]:
                where = "%s/%s" % (name, role["id"])
                policy = role["bypass_account_credentials"]
                writes = holds(role, "contents", ("write", "full"))
                if role["phase"] == "runtime" and writes:
                    self.assertEqual(policy["policy"], "forbidden", where)
                if policy["policy"] == "allowed_without_contents_write":
                    self.assertEqual(writes, [], where)
                if policy["policy"] == "holder_is_bypass_account":
                    self.assertIn(role["id"], ("setup-operator", "human-integrator"), where)
                if policy["policy"] == "not_applicable":
                    self.assertEqual(role["credential_types"], ["none"], where)
                if role["credential_types"] == ["none"]:
                    self.assertEqual(policy["policy"], "not_applicable", where)
                for credential_type in policy["exempt_credential_types"]:
                    self.assertIn(credential_type, role["credential_types"], where)
                    exempt_writes = [p for p in writes if p["credential_type"] == credential_type]
                    self.assertEqual(exempt_writes, [], "%s exempts %s, which holds Contents write" % (where, credential_type))
                if policy["policy"] in ("forbidden", "allowed_without_contents_write"):
                    self.assertTrue(any("RS-main-integrator bypass actor" in text for text in role["must_not_have"]),
                                    "%s must state the rule in must_not_have" % where)
                    relations = {(e["ruleset"], e["relation"]) for e in role["enforcement"]}
                    self.assertNotIn(("RS-main-integrator", "held_by_bypass_account"), relations, where)

    def test_conditional_bypass_is_human_only_and_audited(self):
        documented = self.evidence["rulesets"]
        points = {p["id"]: {o["id"] for o in p["options"]} for p in self.matrix["decision_points"]}
        for ruleset in self.matrix["rulesets"]:
            for actor in ruleset.get("conditional_bypass_actors", []):
                self.assertEqual(ruleset["id"], "RS-main-integrator", "conditional bypass only on the merge block")
                self.assertIn(actor["actor_type"], documented["bypass_actor_types_rest"])
                self.assertIn(actor["actor_type"], HUMAN_BYPASS_ACTOR_TYPES)
                self.assertEqual(actor["bypass_mode"], "pull_request")
                self.assertIn(actor["when"]["option"], points[actor["when"]["decision_point"]])

    def test_recommended_options_are_mutually_consistent(self):
        points = {p["id"]: p for p in self.matrix["decision_points"]}
        for point in points.values():
            recommended = [o for o in point["options"] if o["id"] == point["recommended"]][0]
            for requirement in recommended.get("requires", []):
                self.assertEqual(points[requirement["decision_point"]]["recommended"], requirement["option"],
                                 "%s recommends %s, which requires %s=%s" % (
                                     point["id"], recommended["id"], requirement["decision_point"], requirement["option"]))


class ScopeTests(Fixtures):
    """Each role states repository selection and Project scope per credential type (plan section 10)."""

    EXPECTED_SELECTION = {
        "github_app_installation": "this_repository_only", "fine_grained_pat": "this_repository_only",
        "classic_pat": "all_accessible_repositories", "oauth_gh_cli": "all_accessible_repositories",
        "github_token": "workflow_repository_only", "human_account": "repository_role", "none": "none",
    }

    def test_repository_selection_covers_credentials(self):
        for placement, role in self.all_roles():
            selection = {e["credential_type"]: e for e in role["scope"]["repository_selection"]}
            self.assertEqual(set(selection), set(role["credential_types"]), role["id"])
            for credential_type, entry in selection.items():
                self.assertEqual(entry["selection"], self.EXPECTED_SELECTION[credential_type], role["id"])
                if credential_type not in ("human_account", "none"):
                    self.assertIn(entry.get("source"), self.source_ids, role["id"])

    def test_project_scope_matches_project_permissions(self):
        for placement, role in self.all_roles():
            scopes = {e["credential_type"]: e for e in role["scope"]["project_scope"]}
            self.assertEqual(set(scopes), set(role["credential_types"]), role["id"])
            for credential_type, entry in scopes.items():
                has_project = any(p["credential_type"] == credential_type and p["resource"].startswith("projects_")
                                  for p in role["permissions"])
                self.assertEqual(entry["scope"] != "none", has_project, "%s/%s" % (role["id"], credential_type))
                if has_project:
                    self.assertIn(entry.get("source"), self.source_ids, role["id"])
            if any(e["scope"] != "none" for e in scopes.values()):
                self.assertTrue(any("user-owned" in c for c in role["scope"]["caveats"]), role["id"])


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
                self.assertIn({"ruleset": "RS-main", "relation": "subject_to"}, role["enforcement"],
                              "%s/%s must be subject to RS-main (pull request and trusted-CI checks)" % (placement, role["id"]))
                self.assertFalse([e for e in declared if e["relation"] == "bypass_actor"])
        self.assertGreater(checked, 0)


class VersionAndDecisionTests(Fixtures):
    """(7) Semver matrix version; undecided parameters stay explicit decision points."""

    def test_matrix_version_is_semver(self):
        self.assertRegex(self.matrix["matrix_version"], SEMVER)
        self.assertEqual(self.matrix["schema_version"], 1)

    def test_versioning_rule_is_recorded(self):
        note = self.matrix["versioning"]
        self.assertIn("acceptance", note)
        if self.matrix["status"] == "proposed":
            self.assertEqual(self.matrix["matrix_version"], "1.0.0", "no bump before human acceptance")

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
        for credential in profile["credentials"]:
            reported = credential["scopes_reported"]
            pending = credential.get("scopes_pending", [])
            self.assertIn("repo", reported)
            self.assertTrue(all(isinstance(x, str) and x for x in reported + pending))
            self.assertEqual(set(reported) & set(pending), set(), "a scope cannot be both reported and pending")
            self.assertIn("not inspected", credential["note"])
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
        for required in ("state-backend", "publisher", "execution", "reviewer-launch", "command-envelope",
                         "command-ingestion", "board-projection", "plan-compiler", "evidence-records",
                         "trusted-evidence"):
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
        allowed = {"id", "owner_module", "owner_task", "contract_fixture_task", "consumers", "depends_on_interfaces",
                   "conforms_to", "status", "operations"}
        for interface in index["interfaces"]:
            self.assertLessEqual(set(interface), allowed, "%s carries split-ownership fields" % interface["id"])
            self.assertIsInstance(interface["owner_task"], str)
        execution = [i for i in index["interfaces"] if i["id"] == "execution"][0]
        self.assertLessEqual({"start", "checkpoint", "stop_request", "stop_confirmed", "authority_lost"},
                             {op["name"] for op in execution["operations"]})
        self.assertIn("P02b", execution["consumers"])


class InterfaceOwnershipTests(unittest.TestCase):
    """One owner per interface, owner modules inside the owner's allocation, dependencies follow the task DAG."""

    @classmethod
    def setUpClass(cls):
        cls.index = load(INTERFACES)
        cls.tasks = {t["id"]: t for t in load(TASKS)["tasks"]}

    def prerequisites(self, task_id):
        seen, stack = set(), list(self.tasks[task_id]["depends_on"])
        while stack:
            current = stack.pop()
            if current not in seen:
                seen.add(current)
                stack.extend(self.tasks[current]["depends_on"])
        return seen

    def test_owner_module_within_owner_task_allowed_paths(self):
        for interface in self.index["interfaces"]:
            prefixes = [p[:-2] for p in self.tasks[interface["owner_task"]]["allowed_paths"] if p.endswith("/**")]
            self.assertTrue(any(interface["owner_module"].startswith(prefix) for prefix in prefixes),
                            "%s not in %s allocation" % (interface["owner_module"], interface["owner_task"]))

    def test_owner_modules_are_distinct(self):
        modules = [i["owner_module"] for i in self.index["interfaces"]]
        self.assertEqual(len(modules), len(set(modules)))

    def test_dependencies_respect_task_order(self):
        by_id = {i["id"]: i for i in self.index["interfaces"]}
        for interface in self.index["interfaces"]:
            owner = interface["owner_task"]
            for dependency in interface["depends_on_interfaces"]:
                self.assertIn(dependency, by_id, interface["id"])
                dep_owner = by_id[dependency]["owner_task"]
                self.assertTrue(dep_owner == owner or dep_owner in self.prerequisites(owner),
                                "%s (%s) depends on %s (%s), which is not a prerequisite" %
                                (interface["id"], owner, dependency, dep_owner))
            for contract in interface.get("conforms_to", []):
                self.assertIn(contract, by_id, interface["id"])


if __name__ == "__main__":
    unittest.main()
