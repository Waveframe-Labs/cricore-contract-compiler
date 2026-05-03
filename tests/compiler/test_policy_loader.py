import json
from pathlib import Path

import pytest

from compiler.load_policy import load_policy, PolicyLoadError


def test_policy_loads_successfully(tmp_path: Path):

    policy = {
        "contract_id": "example-policy",
        "contract_version": "0.1.0"
    }

    policy_file = tmp_path / "policy.json"

    with policy_file.open("w") as f:
        json.dump(policy, f)

    loaded = load_policy(policy_file)

    assert loaded == policy


def test_missing_policy_file_fails(tmp_path: Path):

    missing_file = tmp_path / "missing.json"

    with pytest.raises(PolicyLoadError):
        load_policy(missing_file)


def test_invalid_json_fails(tmp_path: Path):

    policy_file = tmp_path / "policy.json"

    policy_file.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(PolicyLoadError):
        load_policy(policy_file)


def test_non_object_json_fails(tmp_path: Path):

    policy_file = tmp_path / "policy.json"

    policy_file.write_text('["not", "an", "object"]', encoding="utf-8")

    with pytest.raises(PolicyLoadError):
        load_policy(policy_file)
        
