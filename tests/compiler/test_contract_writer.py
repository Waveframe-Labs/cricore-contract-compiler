import json
from pathlib import Path

from compiler.compile_policy import compile_policy
from compiler.write_compiled_contract import write_compiled_contract


def test_compiled_contract_is_written(tmp_path: Path):

    policy = {
        "contract_id": "example-policy",
        "contract_version": "0.1.0"
    }

    output_file = tmp_path / "compiled_contract.json"

    compiled = compile_policy(policy)

    written_path = write_compiled_contract(compiled, output_file)

    assert written_path.exists()
    assert written_path == output_file


def test_written_contract_matches_compiled_output(tmp_path: Path):

    policy = {
        "contract_id": "example-policy",
        "contract_version": "0.1.0",
        "authority": {
            "required_roles": ["proposer", "reviewer"],
            "separation_of_duties": True
        }
    }

    output_file = tmp_path / "compiled_contract.json"

    compiled = compile_policy(policy)

    write_compiled_contract(compiled, output_file)

    with output_file.open() as f:
        written_contract = json.load(f)

    # Verify compiler metadata
    assert "_compiler" in written_contract
    assert written_contract["_compiler"]["tool"] == "cricore-contract-compiler"
    assert written_contract["_compiler"]["version"] == "0.4.0"
    assert written_contract["_compiler"]["contract_hash"] == compiled["contract_hash"]

    # Compare the actual compiled contract surface
    contract_surface = {
        k: v for k, v in written_contract.items()
        if k != "_compiler"
    }

    assert contract_surface == compiled
