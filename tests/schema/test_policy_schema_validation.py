import json
from pathlib import Path

import pytest
import jsonschema


SCHEMA_PATH = Path("schema/policy.schema.json")
VALID_FIXTURES = Path("tests/fixtures/policies/valid")
INVALID_FIXTURES = Path("tests/fixtures/policies/invalid")


@pytest.fixture(scope="module")
def policy_schema():
    with SCHEMA_PATH.open() as f:
        return json.load(f)


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def test_valid_policies_pass_schema(policy_schema):
    valid_files = sorted(VALID_FIXTURES.glob("*.json"))

    assert valid_files, "No valid policy fixtures found."

    for file in valid_files:
        policy = load_json(file)

        try:
            jsonschema.validate(instance=policy, schema=policy_schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"{file} should be valid but failed validation:\n{e}")


def test_invalid_policies_fail_schema(policy_schema):
    invalid_files = sorted(INVALID_FIXTURES.glob("*.json"))

    assert invalid_files, "No invalid policy fixtures found."

    for file in invalid_files:
        policy = load_json(file)

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=policy, schema=policy_schema)


@pytest.mark.parametrize("targets", [
    {"allow": [{"value": "README.md"}]},
    {"allow": [{"match": "exact"}]},
    {"allow": [{"match": "glob", "value": "README.md"}]},
    {"allow": [{"match": 1, "value": "README.md"}]},
    {"allow": [{"match": "exact", "value": ""}]},
    {"allow": [{"match": "exact", "value": 1}]},
    {"allow": {}},
    {"deny": "deployment/"},
    {"unknown": []},
    {"allow": [{"match": "exact", "value": "README.md", "extra": True}]},
])
def test_invalid_target_sections_fail_schema(policy_schema, targets):
    policy = {
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": targets,
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=policy, schema=policy_schema)


@pytest.mark.parametrize("targets", [
    {},
    {"allow": []},
    {"deny": []},
    {"allow": [], "deny": []},
])
def test_empty_target_sections_fail_schema(policy_schema, targets):
    policy = {
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": targets,
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=policy, schema=policy_schema)


@pytest.mark.parametrize("value", ["", " ", "\t", "\r\n"])
def test_blank_target_rule_values_fail_schema(policy_schema, value):
    policy = {
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": {
            "allow": [{"match": "exact", "value": value}],
        },
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=policy, schema=policy_schema)


@pytest.mark.parametrize("targets", [
    {"allow": [{"match": "exact", "value": "README.md"}]},
    {"deny": [{"match": "prefix", "value": "deployment/"}]},
    {
        "allow": [{"match": "exact", "value": "README.md"}],
        "deny": [],
    },
    {
        "allow": [],
        "deny": [{"match": "prefix", "value": "deployment/"}],
    },
])
def test_nonempty_target_sections_pass_schema(policy_schema, targets):
    policy = {
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": targets,
    }

    jsonschema.validate(instance=policy, schema=policy_schema)
