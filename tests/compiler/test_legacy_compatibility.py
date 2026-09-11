import json
import sys
from pathlib import Path

import pytest

from compiler.cli import main
from compiler.compile_policy import PolicyCompilationError, compile_policy
from compiler.compile_policy_file import compile_policy_file


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "legacy"


@pytest.mark.parametrize("policy_path", sorted(FIXTURES.glob("*.policy.json")), ids=lambda p: p.stem)
def test_historical_legacy_outputs_and_artifact_bytes(policy_path, tmp_path, monkeypatch):
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    expected_text = policy_path.with_name(policy_path.name.replace(".policy.", ".compiled.")).read_text(encoding="utf-8")
    assert json.dumps(compile_policy(policy), indent=2) + "\n" == expected_text
    expected_bytes = policy_path.with_name(policy_path.name.replace(".policy.", ".artifact.")).read_bytes()
    for mode in ["file", "cli"]:
        output = tmp_path / f"{mode}.json"
        if mode == "file":
            compile_policy_file(policy_path, output)
        else:
            monkeypatch.setattr(sys, "argv", ["cricore-compile-policy", str(policy_path), str(output)])
            main()
        # Text-mode newline translation is platform-specific; JSON bytes are fixed.
        assert output.read_bytes().replace(b"\r\n", b"\n") == expected_bytes.replace(b"\r\n", b"\n")


RESTRICTED_PAYLOADS = [
    {"action_requirements": value} for value in [None, {}, [], {"create": {"required_role": None, "allow": [], "deny": []}}]
] + [
    {"schema_version": value} for value in [None, "", 1, {}, [], "action_policy.v1", "unknown.v1", "compiled_action_contract.v1"]
] + [
    {"schema_version": "action_policy.v1", "action_requirements": {"create": {"required_role": None, "allow": [], "deny": []}}}
]


@pytest.mark.parametrize("restricted", RESTRICTED_PAYLOADS)
@pytest.mark.parametrize("mixed", [False, True])
def test_legacy_python_file_and_cli_reject_action_payloads(restricted, mixed, tmp_path, monkeypatch):
    policy = {"contract_id": "restricted", "contract_version": "1.0.0", **restricted}
    if mixed:
        policy.update(authority={"required_roles": ["maintainer"]}, targets={"allow": [{"match": "prefix", "value": "generated/"}]})
    with pytest.raises(PolicyCompilationError, match="compile_action_policy"):
        compile_policy(policy)
    source = tmp_path / "policy.json"
    source.write_text(json.dumps(policy), encoding="utf-8")
    output = tmp_path / "output.json"
    for existing in [False, True]:
        if existing:
            output.write_bytes(b"existing artifact")
        for mode in ["file", "cli"]:
            with pytest.raises(PolicyCompilationError, match="compile_action_policy"):
                if mode == "file":
                    compile_policy_file(source, output)
                else:
                    monkeypatch.setattr(sys, "argv", ["cricore-compile-policy", str(source), str(output)])
                    main()
            if existing:
                assert output.read_bytes() == b"existing artifact"
            else:
                assert not output.exists()
