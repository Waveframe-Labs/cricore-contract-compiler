"""
---
title: "CRI-CORE Policy Compiler CLI"
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
  - "./compile_policy_file.py"

anchors:
  - "CRI-CORE-POLICY-COMPILER-CLI-v0.1.0"
---
"""

from __future__ import annotations

import argparse
from pathlib import Path

from compiler.compile_policy_file import compile_policy_file


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Compile a governance policy into a CRI-CORE compiled contract."
    )

    parser.add_argument(
        "policy",
        type=Path,
        help="Path to governance policy JSON file",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Output path for compiled contract JSON",
    )

    args = parser.parse_args()

    output_path = compile_policy_file(args.policy, args.output)

    print(f"Compiled contract written to: {output_path}")