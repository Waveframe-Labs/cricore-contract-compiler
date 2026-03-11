"""
---
title: "CRI-CORE Policy File Compiler Entrypoint"
filetype: "operational"
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
  - "./load_policy.py"
  - "./compile_policy.py"
  - "./write_compiled_contract.py"

anchors:
  - "CRI-CORE-POLICY-FILE-COMPILER-v0.1.0"
---
"""

from __future__ import annotations

from pathlib import Path

from compiler.load_policy import load_policy
from compiler.compile_policy import compile_policy
from compiler.write_compiled_contract import write_compiled_contract


def compile_policy_file(policy_path: Path, output_path: Path) -> Path:
    """
    Compile a governance policy file into a compiled contract artifact.

    Steps:
    1. Load policy from disk
    2. Compile policy into contract structure
    3. Write compiled contract artifact

    Returns:
        Path to the compiled contract artifact.
    """

    policy = load_policy(policy_path)

    compiled_contract = compile_policy(policy)

    written_path = write_compiled_contract(compiled_contract, output_path)

    return written_path
    