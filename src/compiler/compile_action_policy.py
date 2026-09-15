"""Compile closed action policies without evaluating runtime authorization."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any, Dict

from jsonschema import Draft202012Validator

from .compile_policy import PolicyCompilationError
from .contract_hash import compute_contract_hash


_VALIDATOR = Draft202012Validator(json.loads(
    files("compiler").joinpath("schemas/action_policy.schema.json").read_text(
        encoding="utf-8"
    )
))


def compile_action_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    """Return a detached, canonical compiled_action_contract.v1 contract.

    Only create and modify are supported. Missing actions remain missing;
    empty allow lists grant no permission. Deny takes precedence within each
    action, and required_role is an additional requirement, never a grant.
    Targets are opaque strings. No authorization or filesystem operations
    are performed. Invalid input raises PolicyCompilationError.
    """
    error = next(_VALIDATOR.iter_errors(policy), None)
    if error is not None:
        path = ".".join(str(part) for part in error.absolute_path) or "policy"
        raise PolicyCompilationError(f"{path}: {error.message}")

    actions = {}
    for action, block in sorted(policy["action_requirements"].items()):
        allow = {(rule["match"], rule["value"]) for rule in block["allow"]}
        deny = {(rule["match"], rule["value"]) for rule in block["deny"]}
        if allow & deny:
            raise PolicyCompilationError(
                f"action_requirements.{action}: identical allow and deny selectors"
            )
        # Build fresh containers at every level, preserving literal strings.
        actions[action] = {
            "required_role": block["required_role"],
            "allow": [{"match": match, "value": value} for match, value in sorted(allow)],
            "deny": [{"match": match, "value": value} for match, value in sorted(deny)],
        }

    compiled = {
        "schema_version": "compiled_action_contract.v1",
        "contract_id": policy["contract_id"],
        "contract_version": policy["contract_version"],
        "action_requirements": actions,
    }
    compiled["contract_hash"] = compute_contract_hash(compiled)
    return json.loads(json.dumps(compiled, sort_keys=True))
