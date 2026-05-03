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
