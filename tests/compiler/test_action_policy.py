import copy
import hashlib
import json
from importlib.resources import files
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from compiler import compile_action_policy
from compiler.compile_action_policy import compile_action_policy as module_api
from compiler.compile_policy import PolicyCompilationError


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "actions"
INPUT_SCHEMA = json.loads(files("compiler").joinpath(
    "schemas/action_policy.schema.json"
).read_text(encoding="utf-8"))
OUTPUT_SCHEMA = json.loads(files("compiler").joinpath(
    "schemas/compiled_action_contract.schema.json"
).read_text(encoding="utf-8"))


def read_fixture(name, kind="policy"):
    return json.loads((FIXTURES / f"{name}.{kind}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["create-only", "modify-only", "mixed"])
def test_exact_output_fixtures(name):
    policy = read_fixture(name)
    expected = read_fixture(name, "compiled")
    assert module_api is compile_action_policy
    assert compile_action_policy(policy) == expected
    Draft202012Validator(INPUT_SCHEMA).validate(policy)
    Draft202012Validator(OUTPUT_SCHEMA).validate(expected)
    unsigned = {k: v for k, v in expected.items() if k != "contract_hash"}
    digest = hashlib.sha256(json.dumps(
        unsigned, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    assert expected["contract_hash"] == digest
    del unsigned["schema_version"]
    assert hashlib.sha256(json.dumps(
        unsigned, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest() != digest


def test_canonical_order_is_independent_of_all_input_ordering():
    policy = read_fixture("mixed")
    for block in policy["action_requirements"].values():
        block["allow"] += [{"match": "prefix", "value": "z/"},
                           {"match": "exact", "value": "a"}]
        block["deny"] += [{"match": "exact", "value": "z/private"},
                          {"match": "prefix", "value": "a/private/"}]

    def reverse(value):
        if isinstance(value, dict):
            return {k: reverse(v) for k, v in reversed(list(value.items()))}
        if isinstance(value, list):
            return [reverse(v) for v in reversed(value)]
        return value

    compiled = compile_action_policy(policy)
    assert json.dumps(compiled) == json.dumps(compile_action_policy(reverse(policy)))
    for block in compiled["action_requirements"].values():
        for effect in ("allow", "deny"):
            assert block[effect] == sorted(block[effect], key=lambda r: (r["match"], r["value"]))


@pytest.mark.parametrize("action", ["create", "modify"])
@pytest.mark.parametrize("field", ["required_role", "allow", "deny"])
def test_action_changes_affect_identity_without_affecting_other_action(action, field):
    policy = read_fixture("mixed")
    before = compile_action_policy(policy)
    block = policy["action_requirements"][action]
    if field == "required_role":
        block[field] = "another-role"
    else:
        block[field].append({"match": "exact", "value": "another-target"})
    after = compile_action_policy(policy)
    other = "modify" if action == "create" else "create"
    assert before["action_requirements"][other] == after["action_requirements"][other]
    assert before["contract_hash"] != after["contract_hash"]


def test_action_identifier_and_identity_fields_affect_hash():
    policy = read_fixture("create-only")
    before = compile_action_policy(policy)
    policy["action_requirements"]["modify"] = policy["action_requirements"].pop("create")
    assert compile_action_policy(policy)["contract_hash"] != before["contract_hash"]
    for key, value in [("contract_id", "another-id"), ("contract_version", "2.0.1")]:
        changed = read_fixture("create-only")
        changed[key] = value
        assert compile_action_policy(changed)["contract_hash"] != before["contract_hash"]


@pytest.mark.parametrize("role", [None, "creator"])
def test_empty_allow_and_deny_lists_preserve_no_grant(role):
    policy = read_fixture("create-only")
    block = {"required_role": role, "allow": [], "deny": []}
    policy["action_requirements"]["create"] = block
    assert compile_action_policy(policy)["action_requirements"] == {"create": block}
    block["deny"] = [{"match": "prefix", "value": "private/"}]
    assert compile_action_policy(policy)["action_requirements"] == {"create": block}


def test_selectors_can_overlap_and_have_different_effects_across_actions():
    policy = read_fixture("mixed")
    selector = {"match": "prefix", "value": "generated/"}
    policy["action_requirements"]["modify"]["deny"] = [selector]
    compiled = compile_action_policy(policy)
    assert compiled["action_requirements"] == policy["action_requirements"]
    # Same value with a distinct match is not an identical selector.
    policy["action_requirements"]["create"]["deny"] = [{**selector, "match": "exact"}]
    assert compile_action_policy(policy)["action_requirements"] == policy["action_requirements"]


@pytest.mark.parametrize("value", [
    "../outside", "/absolute", "C:\\Repo\\File", "a//b", "a/./b", "README.md",
    "readme.md", "*.py", " leading/trailing ", " ", "\t", "\n", "\x00", "caf\u00e9/", "cafe\u0301/",
])
def test_targets_are_literal_nonempty_strings(value):
    policy = read_fixture("create-only")
    policy["action_requirements"]["create"]["allow"][0]["value"] = value
    assert compile_action_policy(policy)["action_requirements"]["create"]["allow"][0]["value"] == value


def test_no_input_mutation_or_aliasing_even_when_input_containers_are_shared():
    policy = read_fixture("create-only")
    policy["action_requirements"]["modify"] = policy["action_requirements"]["create"]
    original = copy.deepcopy(policy)
    compiled = compile_action_policy(policy)
    second = compile_action_policy(policy)
    assert policy == original
    compiled["action_requirements"]["create"]["allow"][0]["value"] = "changed"
    compiled["action_requirements"]["create"]["deny"].clear()
    assert compiled["action_requirements"]["modify"] == original["action_requirements"]["modify"]
    assert policy == original
    assert second == compile_action_policy(original)
    policy["action_requirements"]["create"]["allow"].clear()
    assert second == compile_action_policy(original)


INVALID_REPLACEMENTS = [
    ((), value) for value in [None, [], "policy", 1, True]
] + [
    (("schema_version",), value) for value in [None, "", "action_policy.v2", "compiled_action_contract.v1", 1, {}, []]
] + [
    (("contract_id",), value) for value in [None, "", 1, True, [], {}]
] + [
    (("contract_version",), value) for value in [None, "", 1, True, [], {}, "1.0", "1.0.0\n", "\u0661.0.0", "1.0.0-beta"]
] + [
    (("action_requirements",), value) for value in [None, [], "create", 1, True, {}, {"delete": {}}]
] + [
    (("action_requirements", "create"), value) for value in [None, [], "create", 1, True, {}]
] + [
    (("action_requirements", "create", "required_role"), value) for value in ["", 1, True, [], {}, ["creator"]]
] + [
    (("action_requirements", "create", effect), value)
    for effect in ["allow", "deny"] for value in [None, {}, "target", 1, True, [None], [[]], [1], ["target"], [{}]]
] + [
    (("action_requirements", "create", "allow", 0, "match"), value)
    for value in [None, "", "glob", "regex", "Exact", 1, True, [], {}]
] + [
    (("action_requirements", "create", "allow", 0, "value"), value)
    for value in [None, "", 1, True, [], {}]
]


@pytest.mark.parametrize("path,value", INVALID_REPLACEMENTS)
def test_wrong_types_and_values_reject_in_api_and_schema(path, value):
    policy = read_fixture("mixed")
    if path:
        parent = policy
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
    else:
        policy = value
    with pytest.raises(PolicyCompilationError):
        compile_action_policy(policy)
    assert not Draft202012Validator(INPUT_SCHEMA).is_valid(policy)


@pytest.mark.parametrize("path", [
    ("schema_version",), ("contract_id",), ("contract_version",), ("action_requirements",),
    ("action_requirements", "create", "required_role"),
    ("action_requirements", "create", "allow"), ("action_requirements", "create", "deny"),
    ("action_requirements", "create", "allow", 0, "match"),
    ("action_requirements", "create", "allow", 0, "value"),
])
def test_missing_fields_reject(path):
    policy = read_fixture("mixed")
    parent = policy
    for key in path[:-1]:
        parent = parent[key]
    del parent[path[-1]]
    with pytest.raises(PolicyCompilationError):
        compile_action_policy(policy)
    assert not Draft202012Validator(INPUT_SCHEMA).is_valid(policy)


@pytest.mark.parametrize("path,extra", [
    ((), field) for field in ["authority", "approvals", "artifacts", "stages", "constraints", "targets", "contract_hash", "source", "approval", "lineage", "bundle", "receipt", "unknown"]
] + [
    (("action_requirements",), "delete"), (("action_requirements",), "CREATE"),
    (("action_requirements", "create"), "unknown"),
    (("action_requirements", "create", "allow", 0), "unknown"),
    (("action_requirements", "create", "deny", 0), "unknown"),
])
def test_closed_objects_reject_extra_fields(path, extra):
    policy = read_fixture("mixed")
    parent = policy
    for key in path:
        parent = parent[key]
    parent[extra] = {}
    with pytest.raises(PolicyCompilationError):
        compile_action_policy(policy)
    assert not Draft202012Validator(INPUT_SCHEMA).is_valid(policy)


@pytest.mark.parametrize("action", ["create", "modify"])
@pytest.mark.parametrize("effect", ["allow", "deny"])
def test_duplicate_rules_reject(action, effect):
    policy = read_fixture("mixed")
    rule = {"match": "exact", "value": "duplicate"}
    policy["action_requirements"][action][effect] = [rule, dict(reversed(list(rule.items())))]
    with pytest.raises(PolicyCompilationError):
        compile_action_policy(policy)
    assert not Draft202012Validator(INPUT_SCHEMA).is_valid(policy)


@pytest.mark.parametrize("action", ["create", "modify"])
@pytest.mark.parametrize("match", ["exact", "prefix"])
def test_identical_allow_deny_selectors_reject(action, match):
    policy = read_fixture("mixed")
    rule = {"match": match, "value": "same-target"}
    policy["action_requirements"][action]["allow"] = [rule]
    policy["action_requirements"][action]["deny"] = [dict(rule)]
    original = copy.deepcopy(policy)
    with pytest.raises(PolicyCompilationError, match="identical allow and deny"):
        compile_action_policy(policy)
    assert policy == original


@pytest.mark.parametrize("schema", [INPUT_SCHEMA, OUTPUT_SCHEMA])
def test_packaged_schemas_are_valid(schema):
    Draft202012Validator.check_schema(schema)


def test_output_schema_is_closed_at_each_level():
    validator = Draft202012Validator(OUTPUT_SCHEMA)
    for path in [(), ("action_requirements",), ("action_requirements", "create"),
                 ("action_requirements", "create", "allow", 0)]:
        compiled = read_fixture("mixed", "compiled")
        parent = compiled
        for key in path:
            parent = parent[key]
        parent["extra"] = True
        assert not validator.is_valid(compiled)
    for field in read_fixture("mixed", "compiled"):
        compiled = read_fixture("mixed", "compiled")
        del compiled[field]
        assert not validator.is_valid(compiled)
    for digest in [None, 1, "", "g" * 64, "a" * 63, "a" * 65, "a" * 64 + "\n"]:
        compiled = read_fixture("mixed", "compiled")
        compiled["contract_hash"] = digest
        assert not validator.is_valid(compiled)


def test_packaged_legacy_schema_matches_repository_schema():
    packaged = files("compiler").joinpath("schemas/policy.schema.json").read_bytes()
    source = Path("schema/policy.schema.json").read_bytes()
    assert packaged.replace(b"\r\n", b"\n") == source.replace(b"\r\n", b"\n")
