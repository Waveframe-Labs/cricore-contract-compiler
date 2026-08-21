import json
from pathlib import Path

import pytest

from compiler.compile_policy import PolicyCompilationError, compile_policy


def test_minimal_policy_compiles():

    policy = {
        "contract_id": "example-policy",
        "contract_version": "0.1.0"
    }

    compiled = compile_policy(policy)

    assert compiled["contract_id"] == "example-policy"
    assert compiled["contract_version"] == "0.1.0"

    assert compiled["authority_requirements"] == {}
    assert compiled["approval_requirements"] == {}
    assert compiled["artifact_requirements"] == {}
    assert compiled["stage_requirements"] == {}
    assert compiled["invariants"] == {}

    # cryptographic contract identity
    assert "contract_hash" in compiled
    assert isinstance(compiled["contract_hash"], str)
    assert len(compiled["contract_hash"]) == 64


def test_compiler_output_shape():

    policy = {
        "contract_id": "protocol-shape",
        "contract_version": "1.0.0",
        "authority": {
            "required_roles": ["proposer"]
        }
    }

    compiled = compile_policy(policy)

    assert "contract_id" in compiled
    assert "contract_version" in compiled
    assert "contract_hash" in compiled


def test_compiler_core_identity_is_always_present():

    policy = {
        "contract_id": "core-identity",
        "contract_version": "1.0.0",
    }

    compiled = compile_policy(policy)

    required = ["contract_id", "contract_version", "contract_hash"]

    for field in required:
        assert field in compiled


def test_authority_rules_compile():

    policy = {
        "contract_id": "finance-policy",
        "contract_version": "0.1.0",
        "authority": {
            "required_roles": ["proposer", "reviewer"],
            "separation_of_duties": True
        },
        "constraints": [
            {
                "type": "separation_of_duties",
                "roles": ["proposer", "reviewer"],
            }
        ],
    }

    compiled = compile_policy(policy)

    assert compiled["authority_requirements"]["required_roles"] == [
        "proposer",
        "reviewer",
    ]

    assert "separation_of_duties" not in compiled["authority_requirements"]
    assert compiled["invariants"]["separation_of_duties"] == [
        ["proposer", "reviewer"]
    ]

    assert "contract_hash" in compiled


def test_invalid_required_roles_type():

    policy = {
        "contract_id": "test",
        "contract_version": "1.0.0",
        "authority": {
            "required_roles": "not-a-list"
        }
    }

    with pytest.raises(PolicyCompilationError):
        compile_policy(policy)


def test_artifact_requirements_compile():

    policy = {
        "contract_id": "artifact-policy",
        "contract_version": "0.1.0",
        "artifacts": {
            "required": ["proposal", "approval"]
        }
    }

    compiled = compile_policy(policy)

    assert compiled["artifact_requirements"]["required_artifacts"] == [
        "proposal",
        "approval",
    ]

    assert "contract_hash" in compiled


def test_approval_thresholds_compile():

    policy = {
        "contract_id": "finance-core",
        "contract_version": "1.2.0",
        "authority": {
            "required_roles": ["proposer", "responsible", "accountable"]
        },
        "approvals": {
            "thresholds": [
                {
                    "field": "amount",
                    "operator": ">",
                    "value": 1000,
                    "requires_role": "approver",
                }
            ]
        },
        "constraints": [
            {
                "type": "separation_of_duties",
                "roles": ["responsible", "accountable"],
            }
        ],
    }

    compiled = compile_policy(policy)

    assert compiled["authority_requirements"]["required_roles"] == [
        "proposer",
        "responsible",
        "accountable",
    ]
    assert compiled["approval_requirements"]["thresholds"] == [
        {
            "field": "amount",
            "operator": ">",
            "value": 1000,
            "requires_role": "approver",
        }
    ]
    assert compiled["invariants"]["separation_of_duties"] == [
        ["responsible", "accountable"]
    ]


def test_invalid_approval_thresholds_type():

    policy = {
        "contract_id": "finance-core",
        "contract_version": "1.2.0",
        "approvals": {
            "thresholds": "not-a-list"
        }
    }

    with pytest.raises(PolicyCompilationError):
        compile_policy(policy)


def test_stage_transitions_compile():

    policy = {
        "contract_id": "workflow-policy",
        "contract_version": "0.1.0",
        "stages": {
            "allowed_transitions": [
                {"from": "proposed", "to": "approved"}
            ]
        }
    }

    compiled = compile_policy(policy)

    transitions = compiled["stage_requirements"]["allowed_transitions"]

    assert len(transitions) == 1
    assert transitions[0]["from"] == "proposed"
    assert transitions[0]["to"] == "approved"

    assert "contract_hash" in compiled


def test_exact_allow_target_rule_compiles():

    compiled = compile_policy({
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": {
            "allow": [{"match": "exact", "value": "README.md"}],
        },
    })

    assert compiled["target_requirements"] == {
        "allow": [{"match": "exact", "value": "README.md"}],
        "deny": [],
    }


def test_prefix_deny_target_rule_compiles():

    compiled = compile_policy({
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": {
            "deny": [{"match": "prefix", "value": "deployment/"}],
        },
    })

    assert compiled["target_requirements"] == {
        "allow": [],
        "deny": [{"match": "prefix", "value": "deployment/"}],
    }


def test_combined_target_rules_compile_deterministically():

    policy = {
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": {
            "allow": [{"match": "exact", "value": "README.md"}],
            "deny": [{"match": "prefix", "value": "deployment/"}],
        },
    }

    compiled_a = compile_policy(policy)
    compiled_b = compile_policy(policy)

    assert compiled_a["target_requirements"] == {
        "allow": [{"match": "exact", "value": "README.md"}],
        "deny": [{"match": "prefix", "value": "deployment/"}],
    }
    assert compiled_a == compiled_b
    assert compiled_a["contract_hash"] == compiled_b["contract_hash"]
    assert compiled_a["contract_hash"] != compile_policy({
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
    })["contract_hash"]


@pytest.mark.parametrize("targets", [
    {"allow": [{"value": "README.md"}]},
    {"allow": [{"match": "exact"}]},
    {"allow": [{"match": "glob", "value": "README.md"}]},
    {"allow": [{"match": 1, "value": "README.md"}]},
    {"allow": [{"match": "exact", "value": ""}]},
    {"allow": [{"match": "exact", "value": 1}]},
    {"allow": {}},
    {"deny": "deployment/"},
    {"allow": [], "unknown": []},
    {"allow": [{"match": "exact", "value": "README.md", "extra": True}]},
])
def test_invalid_target_rules_are_rejected(targets):

    with pytest.raises(PolicyCompilationError):
        compile_policy({
            "contract_id": "target-policy",
            "contract_version": "1.0.0",
            "targets": targets,
        })


@pytest.mark.parametrize("targets", [
    {},
    {"allow": []},
    {"deny": []},
    {"allow": [], "deny": []},
])
def test_empty_target_sections_are_rejected(targets):

    with pytest.raises(PolicyCompilationError):
        compile_policy({
            "contract_id": "target-policy",
            "contract_version": "1.0.0",
            "targets": targets,
        })


@pytest.mark.parametrize("value", ["", " ", "\t", "\r\n"])
def test_blank_target_rule_values_are_rejected(value):

    with pytest.raises(PolicyCompilationError):
        compile_policy({
            "contract_id": "target-policy",
            "contract_version": "1.0.0",
            "targets": {
                "allow": [{"match": "exact", "value": value}],
            },
        })


@pytest.mark.parametrize("targets", [
    {
        "allow": [{"match": "exact", "value": "README.md"}],
        "deny": [],
    },
    {
        "allow": [],
        "deny": [{"match": "prefix", "value": "deployment/"}],
    },
])
def test_target_section_with_one_empty_collection_compiles(targets):

    compiled = compile_policy({
        "contract_id": "target-policy",
        "contract_version": "1.0.0",
        "targets": targets,
    })

    assert compiled["target_requirements"] == targets


@pytest.mark.parametrize(("fixture_name", "expected_hash"), [
    ("minimal.valid.json", "85696b3e59660cfc79f4a48422f04e7c460f1b16578b4cb7429258930f35682e"),
    ("approval-threshold.valid.json", "48350c311443b6cc7f79e0ab4056b9f7d90d6c0785d3c8dea39321e6000ef23a"),
])
def test_legacy_fixture_output_and_hash_are_unchanged(fixture_name, expected_hash):

    fixture_path = Path("tests/fixtures/policies/valid") / fixture_name
    compiled = compile_policy(json.loads(fixture_path.read_text(encoding="utf-8")))

    assert compiled["contract_hash"] == expected_hash
    assert "target_requirements" not in compiled
