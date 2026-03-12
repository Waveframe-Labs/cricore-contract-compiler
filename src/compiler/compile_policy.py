"""
---
title: "CRI-CORE Governance Policy Compiler"
filetype: "operational"
type: "specification"
domain: "governance"
version: "0.1.2"
doi: "TBD-0.1.2"
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
  - "../../schema/policy.schema.json"
  - "./contract_hash.py"

anchors:
  - "CRI-CORE-POLICY-COMPILER-v0.1.2"
---
"""

from __future__ import annotations

from typing import Any, Dict

from .contract_hash import compute_contract_hash


class PolicyCompilationError(Exception):
    """
    Raised when a governance policy cannot be compiled into a
    deterministic contract artifact.
    """
    pass


def compile_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compile a governance policy into a CRI-CORE compiled contract artifact.

    This compiler performs structural transformation only.
    It does not interpret governance semantics.

    Expected input:
        validated governance policy

    Output:
        compiled contract artifact compatible with CRI-CORE
    """

    if not isinstance(policy, dict):
        raise PolicyCompilationError("policy must be an object")

    contract_id = policy.get("contract_id")
    contract_version = policy.get("contract_version")

    if not contract_id:
        raise PolicyCompilationError("policy missing contract_id")

    if not contract_version:
        raise PolicyCompilationError("policy missing contract_version")

    authority = policy.get("authority", {})
    artifacts = policy.get("artifacts", {})
    stages = policy.get("stages", {})

    compiled: Dict[str, Any] = {
        "contract_id": contract_id,
        "contract_version": contract_version,
        "authority_requirements": {},
        "artifact_requirements": {},
        "stage_requirements": {},
        "invariants": {}
    }

    # Authority requirements
    if authority:
        compiled["authority_requirements"] = {
            "required_roles": authority.get("required_roles", []),
            "separation_of_duties": authority.get("separation_of_duties", False)
        }

    # Artifact requirements
    if artifacts:
        compiled["artifact_requirements"] = {
            "required_artifacts": artifacts.get("required", [])
        }

    # Stage requirements
    if stages:
        compiled["stage_requirements"] = {
            "allowed_transitions": stages.get("allowed_transitions", [])
        }

    # Structural invariants
    if authority.get("separation_of_duties"):
        compiled["invariants"]["separation_of_duties"] = True

    # Deterministic cryptographic binding
    # Hash must be computed before adding the hash field itself
    contract_hash = compute_contract_hash(compiled)

    compiled["contract_hash"] = contract_hash

    return compiled