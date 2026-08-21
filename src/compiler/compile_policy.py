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

    if "targets" in policy:
        compiled["target_requirements"] = _compile_target_requirements(
            policy["targets"]
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


def _compile_target_requirements(targets: Any) -> Dict[str, List[Dict[str, str]]]:
    if not isinstance(targets, dict):
        raise PolicyCompilationError("targets must be an object")

    unknown_properties = set(targets) - {"allow", "deny"}
    if unknown_properties:
        raise PolicyCompilationError("targets contains unsupported properties")

    allow_rules = _compile_target_rules(targets.get("allow", []), "allow")
    deny_rules = _compile_target_rules(targets.get("deny", []), "deny")
    if not allow_rules and not deny_rules:
        raise PolicyCompilationError(
            "targets must contain at least one allow or deny rule"
        )

    return {
        "allow": allow_rules,
        "deny": deny_rules,
    }


def _compile_target_rules(rules: Any, collection_name: str) -> List[Dict[str, str]]:
    if not isinstance(rules, list):
        raise PolicyCompilationError(
            f"targets.{collection_name} must be a list of target rules"
        )

    compiled_rules: List[Dict[str, str]] = []
    for rule in rules:
        if not isinstance(rule, dict):
            raise PolicyCompilationError(
                f"targets.{collection_name} must contain target rule objects"
            )

        if set(rule) != {"match", "value"}:
            raise PolicyCompilationError(
                f"targets.{collection_name} rules require only match and value"
            )

        match = rule["match"]
        value = rule["value"]
        if not isinstance(match, str) or match not in {"exact", "prefix"}:
            raise PolicyCompilationError(
                "target rule match must be exact or prefix"
            )
        if not isinstance(value, str) or not value or value.isspace():
            raise PolicyCompilationError("target rule value must be a non-empty string")

        compiled_rules.append({"match": match, "value": value})

    return compiled_rules
