"""
---
title: "CRI-CORE Compiled Contract Artifact Writer"
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
  - "./compile_policy.py"

anchors:
  - "CRI-CORE-COMPILED-CONTRACT-WRITER-v0.1.0"
---
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from compiler.compile_policy import compile_policy


class ContractWriteError(Exception):
    """
    Raised when a compiled contract artifact cannot be written.
    """
    pass


def write_compiled_contract(policy: Dict[str, Any], output_path: Path) -> Path:
    """
    Compile a governance policy and write the compiled contract artifact.

    Returns the path to the written contract file.
    """

    compiled_contract = compile_policy(policy)

    if not isinstance(output_path, Path):
        raise ContractWriteError("output_path must be a pathlib.Path")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ContractWriteError(
            f"failed to create output directory: {exc}"
        ) from exc

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                compiled_contract,
                f,
                indent=2,
                sort_keys=True
            )
            f.write("\n")
    except OSError as exc:
        raise ContractWriteError(
            f"failed to write compiled contract: {exc}"
        ) from exc

    return output_path
