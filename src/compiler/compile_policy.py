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
updated: "2026-04-22"

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

import json
import re
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

    if not isinstance(contract_version, str) or not re.match(
        r"^\d+\.\d+\.\d+$", contract_version
    ):
        raise PolicyCompilationError(
            "contract_version must follow semantic versioning (X.Y.Z)"
        )

    compiled: Dict[str, Any] = {
        "contract_id": contract_id,
        "contract_version": contract_version,
        "authority_requirements": {},
        "approval_requirements": {},
        "artifact_requirements": {},
        "stage_requirements": {},
        "invariants": {},
    }

    authority = policy.get("authority", {})
    if authority:
        required_roles = authority.get("required_roles")
        if required_roles is not None:
            if not isinstance(required_roles, list) or not all(
                isinstance(role, str) for role in required_roles
            ):
                raise PolicyCompilationError(
                    "required_roles must be a list of strings"
                )

            compiled["authority_requirements"]["required_roles"] = required_roles

    artifacts = policy.get("artifacts", {})
    if artifacts:
        required_artifacts = artifacts.get("required")
        if required_artifacts is not None:
            if not isinstance(required_artifacts, list) or not all(
                isinstance(artifact, str) for artifact in required_artifacts
            ):
                raise PolicyCompilationError(
                    "required artifacts must be a list of strings"
                )

            compiled["artifact_requirements"]["required_artifacts"] = (
                required_artifacts
            )

    approvals = policy.get("approvals", {})
    if approvals:
        thresholds = approvals.get("thresholds")
        if thresholds is not None:
            if not isinstance(thresholds, list) or not all(
                isinstance(threshold, dict) for threshold in thresholds
            ):
                raise PolicyCompilationError(
                    "approval thresholds must be a list of threshold objects"
                )

            compiled["approval_requirements"]["thresholds"] = thresholds

    stages = policy.get("stages", {})
    if stages:
        allowed_transitions = stages.get("allowed_transitions")
        if allowed_transitions is not None:
            if not isinstance(allowed_transitions, list) or not all(
                isinstance(transition, dict) for transition in allowed_transitions
            ):
                raise PolicyCompilationError(
                    "allowed_transitions must be a list of transition objects"
                )

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

    for key in [
        "authority_requirements",
        "approval_requirements",
        "artifact_requirements",
        "stage_requirements",
        "invariants",
    ]:
        if not compiled[key]:
            compiled[key] = {}

    canonical = json.loads(json.dumps(compiled, sort_keys=True))
    contract_hash = compute_contract_hash(canonical)
    compiled["contract_hash"] = contract_hash

    return compiled
