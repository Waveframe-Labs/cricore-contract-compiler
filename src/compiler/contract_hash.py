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
    
