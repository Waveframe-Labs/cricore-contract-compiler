"""
---
title: "CRI-CORE Policy Loader Tests"
filetype: "documentation"
type: "specification"
domain: "governance"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-03-11"
updated: "2026-03-11"

author:
  name: "Shawn C. Wright"
  email: "swright@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

license: "Apache-2.0"

copyright:
  holder: "Waveframe Labs"
  year: "2026"

ai_assisted: "partial"

dependencies:
  - "../../src/compiler/load_policy.py"

anchors:
  - "CRI-CORE-POLICY-LOADER-TESTS-v0.1.0"
---
"""

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
        