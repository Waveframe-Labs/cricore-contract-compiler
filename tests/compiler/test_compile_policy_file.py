"""
---
title: "CRI-CORE Policy File Compiler Integration Tests"
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
  - "../../src/compiler/compile_policy_file.py"

anchors:
  - "CRI-CORE-POLICY-FILE-COMPILER-TESTS-v0.1.0"
---
"""

import json
from pathlib import Path

from compiler.compile_policy_file import compile_policy_file
from compiler.compile_policy import compile_policy


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
        compiled = json.load(f)

    expected = compile_policy(policy)

    assert compiled == expected
    