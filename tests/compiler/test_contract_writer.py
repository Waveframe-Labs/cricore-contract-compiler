"""
---
title: "CRI-CORE Compiled Contract Writer Tests"
filetype: "documentation"
type: "specification"
domain: "governance"
version: "0.1.1"
doi: "TBD-0.1.1"
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
  - "../../src/compiler/write_compiled_contract.py"
  - "../../src/compiler/compile_policy.py"

anchors:
  - "CRI-CORE-CONTRACT-WRITER-TESTS-v0.1.1"
---
"""

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

    written_path = write_compiled_contract(policy, output_file)

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

    assert written_contract == compiled
