"""
---
title: "CRI-CORE Contract Compiler Policy Schema Validation Test"
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
  - "../../schema/policy.schema.json"

anchors:
  - "CRI-CORE-POLICY-SCHEMA-VALIDATION-TEST-v0.1.0"
---
"""

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
