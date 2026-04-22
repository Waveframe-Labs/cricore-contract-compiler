"""
---
title: "CRI-CORE Governance Policy Compiler"
filetype: "operational"
type: "specification"
domain: "governance"
version: "0.2.0"
doi: "TBD-0.2.0"
status: "Active"
created: "2026-03-11"
updated: "2026-03-20"

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
  - "CRI-CORE-POLICY-COMPILER-v0.2.0"
---
"""

from __future__ import annotations

from typing import Any, Dict, List

from .contract_hash import compute_contract_hash


class PolicyCompilationError(Exception):
    pass


def compile_policy(policy: Dict[str, Any]) -> Dict[str, Any]:

    if not isinstance(policy, dict):
        raise PolicyCompilationError("policy must be an object")

    contract_id = policy.get("contract_id")
    contract_version = policy.get("contract_version")

    if not contract_id:
        raise PolicyCompilationError("policy missing contract_id")

    if not contract_version:
        raise PolicyCompilationError("policy missing contract_version")

    compiled: Dict[str, Any] = {
        "contract_id": contract_id,
        "contract_version": contract_version,
        "authority_requirements": {},
        "artifact_requirements": {},
        "stage_requirements": {},
        "invariants": {},
    }

    authority = policy.get("authority", {})
    if authority:
        required_roles = authority.get("required_roles")
        if required_roles is not None:
            compiled["authority_requirements"]["required_roles"] = required_roles

        separation_of_duties = authority.get("separation_of_duties")
        if separation_of_duties is not None:
            compiled["authority_requirements"]["separation_of_duties"] = (
                separation_of_duties
            )
            compiled["invariants"]["separation_of_duties"] = separation_of_duties

    artifacts = policy.get("artifacts", {})
    if artifacts:
        required_artifacts = artifacts.get("required")
        if required_artifacts is not None:
            compiled["artifact_requirements"]["required_artifacts"] = (
                required_artifacts
            )

    stages = policy.get("stages", {})
    if stages:
        allowed_transitions = stages.get("allowed_transitions")
        if allowed_transitions is not None:
            compiled["stage_requirements"]["allowed_transitions"] = (
                allowed_transitions
            )

    constraints: List[Dict[str, Any]] = policy.get("constraints", [])

    separation_rules = []

    for constraint in constraints:
        if constraint.get("type") == "separation_of_duties":
            roles = constraint.get("roles", [])

            if not isinstance(roles, list) or len(roles) < 2:
                raise PolicyCompilationError(
                    "separation_of_duties constraint must define at least two roles"
                )

            separation_rules.append(roles)

    if separation_rules:
        compiled["invariants"]["separation_of_duties"] = separation_rules

    contract_hash = compute_contract_hash(compiled)
    compiled["contract_hash"] = contract_hash

    return compiled
