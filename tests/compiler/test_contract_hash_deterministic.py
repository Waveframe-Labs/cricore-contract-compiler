from compiler.compile_policy import compile_policy


def test_contract_hash_is_deterministic():

    policy = {
        "contract_id": "finance-policy",
        "contract_version": "0.1.0",
        "authority": {
            "required_roles": ["proposer", "reviewer"],
            "separation_of_duties": True
        }
    }

    compiled_a = compile_policy(policy)
    compiled_b = compile_policy(policy)

    assert compiled_a["contract_hash"] == compiled_b["contract_hash"]
