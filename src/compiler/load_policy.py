"""
---
title: "CRI-CORE Governance Policy Loader"
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

anchors:
  - "CRI-CORE-POLICY-LOADER-v0.1.0"
---
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class PolicyLoadError(Exception):
    """
    Raised when a governance policy cannot be loaded or parsed.
    """
    pass


def load_policy(policy_path: Path) -> Dict[str, Any]:
    """
    Load a governance policy from disk.

    Structural guarantees:
    - file must exist
    - file must be JSON
    - root object must be a dictionary
    """

    if not isinstance(policy_path, Path):
        raise PolicyLoadError("policy_path must be a pathlib.Path")

    if not policy_path.exists():
        raise PolicyLoadError("policy file does not exist")

    if not policy_path.is_file():
        raise PolicyLoadError("policy path is not a file")

    try:
        raw = policy_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyLoadError(f"failed to read policy file: {exc}") from exc

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PolicyLoadError(f"invalid JSON in policy file: {exc}") from exc

    if not isinstance(obj, dict):
        raise PolicyLoadError("policy file must contain a JSON object")

    return obj
