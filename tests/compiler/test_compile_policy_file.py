import json
from pathlib import Path

from compiler.compile_policy import compile_policy
from compiler.compile_policy_file import compile_policy_file


def test_compile_policy_file_pipeline(tmp_path: Path):

    policy = {
        "contract_id": "example-policy",
        "contract_version": "0.1.0",
        "authority": {
            "required_roles": ["proposer", "reviewer"],
            "separation_of_duties": True
        }
    }

    policy_file = tmp_path / "policy.json"
    output_file = tmp_path / "compiled_contract.json"

    with policy_file.open("w") as f:
        json.dump(policy, f)

    written_path = compile_policy_file(policy_file, output_file)

    assert written_path.exists()
    assert written_path == output_file

    with output_file.open() as f:
        artifact = json.load(f)

    expected = compile_policy(policy)

    # verify compiler metadata
    assert "_compiler" in artifact
    assert artifact["_compiler"]["tool"] == "cricore-contract-compiler"
    assert artifact["_compiler"]["contract_hash"] == expected["contract_hash"]

    # compare compiled contract surface
    contract_surface = {
        k: v for k, v in artifact.items()
        if k != "_compiler"
    }

    assert contract_surface == expected
