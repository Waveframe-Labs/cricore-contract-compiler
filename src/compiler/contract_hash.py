"""
---
title: "CRI-CORE Contract Hash Utility"
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

ai_assisted: "partial"

anchors:
  - "CRI-CORE-CONTRACT-HASH-v0.1.0"
---
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, Any


def compute_contract_hash(contract: Dict[str, Any]) -> str:
    """
    Compute deterministic SHA256 hash of compiled contract.
    """

    canonical = json.dumps(
        contract,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()
    