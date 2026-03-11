"""
---
title: "CRI-CORE Contract Hash Determinism Tests"
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

ai_assisted: "partial"

dependencies:
  - "../../src/compiler/compile_policy.py"

anchors:
  - "CRI-CORE-CONTRACT-HASH-DETERMINISM-TEST-v0.1.0"
---
"""

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