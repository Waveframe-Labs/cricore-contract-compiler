"""
---
title: "CRI-CORE Compiled Contract Artifact Writer"
filetype: "operational"
type: "specification"
domain: "governance"
version: "0.1.3"
doi: "TBD-0.1.3"
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

anchors:
  - "CRI-CORE-COMPILED-CONTRACT-WRITER-v0.1.3"
---
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ContractWriteError(Exception):
    """
    Raised when a compiled contract artifact cannot be written.
    """
    pass


def write_compiled_contract(compiled_contract: Dict[str, Any], output_path: Path) -> Path:
    """
    Write a compiled contract artifact to disk.

    Returns the path to the written contract file.
    """

    if not isinstance(compiled_contract, dict):
        raise ContractWriteError("compiled_contract must be a dictionary")

    if "contract_hash" not in compiled_contract:
        raise ContractWriteError("compiled_contract missing contract_hash")

    if not isinstance(output_path, Path):
        raise ContractWriteError("output_path must be a pathlib.Path")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ContractWriteError(
            f"failed to create output directory: {exc}"
        ) from exc

    artifact = {
        "_compiler": {
            "tool": "cricore-contract-compiler",
            "version": "0.1.0",
            "contract_hash": compiled_contract["contract_hash"],
        },
        **compiled_contract,
    }

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                artifact,
                f,
                indent=2,
                sort_keys=True,
            )
            f.write("\n")
    except OSError as exc:
        raise ContractWriteError(
            f"failed to write compiled contract: {exc}"
        ) from exc

    return output_path