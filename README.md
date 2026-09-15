<p align="center">
  <img src="https://raw.githubusercontent.com/Waveframe-Labs/.github/main/assets/branding/canon_wf_logo_extended.png" width="700">
</p>

# CRI-CORE Contract Compiler

The CRI-CORE Contract Compiler is a deterministic compiler for governance
policies into CRI-CORE contract artifacts.

It bridges governance design and runtime enforcement by converting a
human-authored JSON policy into a stable, machine-readable compiled contract.
The compiled contract is a required input to CRI-CORE and defines the
governance constraints evaluated at the execution boundary.

The compiler does not execute governance logic, make runtime decisions, or
enforce policy. Its role is limited to producing reproducible contract
artifacts with a stable structure and deterministic hash.

## Installation

Install from PyPI:

```bash
pip install cricore-contract-compiler
```

Requires Python 3.9 or later.

## Action policy API (unreleased)

Use the distinct public API for independent file creation and modification
requirements:

```python
from compiler import compile_action_policy

policy = {
    "schema_version": "action_policy.v1",
    "contract_id": "repository-file-policy",
    "contract_version": "2.0.0",
    "action_requirements": {
        "create": {
            "required_role": None,
            "allow": [{"match": "prefix", "value": "generated/"}],
            "deny": [{"match": "prefix", "value": "generated/private/"}],
        },
        "modify": {
            "required_role": "repository-maintainer",
            "allow": [{"match": "exact", "value": "README.md"}],
            "deny": [],
        },
    },
}
compiled = compile_action_policy(policy)
```

The module import `from compiler.compile_action_policy import compile_action_policy`
is also supported. Invalid input raises
`compiler.compile_policy.PolicyCompilationError`.

The result has exactly `schema_version: compiled_action_contract.v1`,
`contract_id`, `contract_version`, `action_requirements`, and `contract_hash`.
See the complete [mixed output fixture](tests/fixtures/actions/mixed.compiled.json),
[create-only fixture](tests/fixtures/actions/create-only.compiled.json), and
[modify-only fixture](tests/fixtures/actions/modify-only.compiled.json).

The input is closed at every object level. It requires the exact discriminator,
a nonempty string contract ID, an `X.Y.Z` version, and at least one action.
The only actions are `create` and `modify`; omitted actions remain omitted.
Each present action requires exactly `required_role`, `allow`, and `deny`.
Roles are null or nonempty strings. Rules require exactly `match` (`exact` or
`prefix`) and a nonempty string `value`.

- An absent action or no matching allow, including an empty allow list, grants
  no permission. A required role is an additional requirement, never a grant.
- Deny takes precedence within the same action. Other actions' rules and roles
  have no effect.
- Duplicate selectors within an action's allow or deny list reject compilation.
  Identical allow/deny selectors within one action also reject; distinct
  overlapping selectors remain representable. Selectors may be reused across
  actions with different effects and roles.
- Target strings remain exact, including case, whitespace, Unicode, separators,
  and wildcard characters. Nonempty whitespace strings are literal values;
  the compiler performs no path validation, normalization, or wildcard expansion.

Rules sort by `(match, value)` in Python string order and object keys sort
lexicographically. The result contains fresh nested containers. SHA-256 covers
the entire output except `contract_hash`, including the schema discriminator,
using the established `json.dumps(sort_keys=True, separators=(",", ":"))`
UTF-8 convention (with the default ASCII escaping).

Schemas ship in the wheel and sdist and can be read without a checkout:

```python
import json
from importlib.resources import files

schema = json.loads(files("compiler").joinpath(
    "schemas/action_policy.schema.json"
).read_text(encoding="utf-8"))
```

`schemas/compiled_action_contract.schema.json` describes the output;
`schemas/policy.schema.json` retains the legacy input schema. The action schemas
validate structure and duplicate rules; the compiler additionally checks
allow/deny contradictions. Schema validation alone does not verify a hash.

Ledger owns authority identity, semantic provenance, policy-path grammar, and
publication. Guard owns runtime enforcement, containment, and operation
preconditions. This API only produces compiler contracts.

The legacy Python, file, and CLI entrypoints reject any top-level
`action_requirements` or explicit `schema_version`, including mixed inputs.
They retain historical outputs, hashes, and writer metadata for supported legacy
inputs. The CLI remains a legacy compiler; serialize action API results directly
with `json.dumps` when needed. The legacy artifact writer adds `_compiler`
metadata and does not produce the exact action output envelope.

Published `0.4.0` cannot acquire this capability retroactively. Future consumers
must require the named new API and validate its exact output; a missing API must
fail without legacy fallback. This unreleased change leaves package version and
legacy writer metadata unchanged; distribution version alone is not a capability
check.

## Legacy CLI Usage

Compile a governance policy into a compiled contract artifact:

```bash
cricore-compile-policy policy.json compiled_contract.json
```

The output is a deterministic JSON artifact that includes compiler metadata,
compiled governance requirements, invariants, and a contract hash.

## Legacy Python Usage

The compiler can also be used programmatically:

```python
from compiler.compile_policy import compile_policy

policy = {
    "contract_id": "finance-policy",
    "contract_version": "1.0.0",
    "authority": {
        "required_roles": ["proposer", "reviewer"]
    },
    "approvals": {
        "thresholds": [
            {
                "field": "amount",
                "operator": ">",
                "value": 1000,
                "requires_role": "approver"
            }
        ]
    },
    "artifacts": {
        "required": ["proposal", "approval"]
    },
    "stages": {
        "allowed_transitions": [
            {"from": "proposed", "to": "approved"}
        ]
    },
    "constraints": [
        {
            "type": "separation_of_duties",
            "roles": ["proposer", "reviewer"]
        }
    ]
}

compiled_contract = compile_policy(policy)
```

## Legacy Policy Input

Policies are JSON objects with a required contract identity:

```json
{
  "contract_id": "finance-policy",
  "contract_version": "1.0.0"
}
```

The compiler currently recognizes these optional sections:

- `authority.required_roles`: list of role names required by the contract.
- `approvals.thresholds`: list of threshold-based approval requirements.
- `artifacts.required`: list of required governance artifact names.
- `stages.allowed_transitions`: list of allowed lifecycle transition objects.
- `constraints`: list of explicit structural constraints.
- `targets.allow` / `targets.deny`: optional opaque target-scoping rules using
  `exact` or `prefix` matching.

`contract_version` must follow semantic version format: `X.Y.Z`.
`contract_version` is assigned by the policy owner and is independent of the
compiler package version.

## Legacy Compiled Output

The compiled contract always includes these top-level sections:

```json
{
  "contract_id": "finance-policy",
  "contract_version": "1.0.0",
  "authority_requirements": {},
  "approval_requirements": {},
  "artifact_requirements": {},
  "stage_requirements": {},
  "invariants": {},
  "contract_hash": "..."
}
```

The required core identity fields of every compiled contract are:

- `contract_id`
- `contract_version`
- `contract_hash`

These are the only identity fields emitted by the compiler. The compiler does
not emit aliases such as `id` or `version`.

The compiler maps policy fields into compiled contract fields as follows:

- `policy.authority.required_roles` becomes `authority_requirements.required_roles`.
- `policy.approvals.thresholds` becomes `approval_requirements.thresholds`.
- `policy.artifacts.required` becomes `artifact_requirements.required_artifacts`.
- `policy.stages.allowed_transitions` becomes `stage_requirements.allowed_transitions`.
- `constraints[type="separation_of_duties"]` becomes `invariants.separation_of_duties`.

Empty compiled sections remain present as empty objects to keep the contract
shape stable for downstream validation and hashing.

## Legacy Target Scoping

Target scope defines which resources an automated action may or may not change.

```json
{
  "targets": {
    "allow": [
      {"match": "exact", "value": "README.md"}
    ],
    "deny": [
      {"match": "prefix", "value": "deployment/"}
    ]
  }
}
```

When `targets` is present, it maps directly to the optional compiled section:

```json
{
  "target_requirements": {
    "allow": [
      {"match": "exact", "value": "README.md"}
    ],
    "deny": [
      {"match": "prefix", "value": "deployment/"}
    ]
  }
}
```

Supported match types are exactly `exact` and literal `prefix`; matching is
case-sensitive against the opaque target supplied by Guard. Deny rules take
precedence over allow rules. A nonempty allow list blocks unmatched targets,
while an empty or absent allow list allows targets unless denied. Missing or
invalid execution targets fail closed whenever `target_requirements` exists.
The format supports neither globs nor regular expressions, and the compiler
performs no implicit or filesystem normalization. The compiler defines and
hashes these constraints, but Guard enforces them at runtime.

## Contract Identity Guarantee

The compiler produces a deterministic contract identity composed of:

- `contract_id`
- `contract_version`
- `contract_hash`

The `contract_hash` is computed from the canonical compiled contract structure
using sorted JSON serialization.

For identical policy inputs, the compiler guarantees identical contract hashes.

This identity is used by downstream systems (e.g., CRI-CORE) to verify that a
proposal references the exact contract used for evaluation. Mismatches result
in enforcement failure.

## Contract Pass-Through Requirement

Compiled contracts must be passed through downstream systems without
modification.

In particular:

- Contract identity fields (`contract_id`, `contract_version`, `contract_hash`)
  must not be altered.
- Downstream components must not recompute or overwrite the contract hash.

CRI-CORE enforces this at evaluation time. Any mismatch between a proposal's
declared contract hash and the compiled contract hash will result in a blocked
decision.

## Determinism

Compiled contracts are hashed with SHA-256 after canonicalizing the compiled
structure using sorted JSON keys.

This ensures:

- identical policy inputs produce identical compiled outputs
- identical compiled outputs produce identical contract hashes

This determinism is required for reproducible enforcement and contract identity
verification in CRI-CORE.

Written artifacts also include `_compiler` metadata:

```json
{
  "_compiler": {
    "tool": "cricore-contract-compiler",
    "version": "0.4.0",
    "contract_hash": "..."
  }
}
```

## Validation

The compiler performs minimal compile-time validation for:

- Policy root type.
- Required `contract_id`.
- Required semantic `contract_version`.
- `authority.required_roles` as a list of strings.
- `approvals.thresholds` as a list of threshold objects.
- `artifacts.required` as a list of strings.
- `stages.allowed_transitions` as a list of transition objects.
- Separation-of-duties constraints with at least two roles.

The JSON schema in `schema/policy.schema.json` defines the supported policy
surface. Runtime enforcement remains outside this package.

## Position in the Governance Pipeline

```text
Governance Policy
        |
Contract Compiler
        |
Compiled Contract
        |
Proposal Normalizer
        |
CRI-CORE Kernel
        |
Commit Decision
```

The compiler sits upstream of CRI-CORE runtime enforcement. It produces the
structural contract artifact that downstream systems can evaluate.

## Role in the Execution Protocol

The compiler is responsible for defining governance constraints in a
deterministic, machine-readable form.

Within the CRI-CORE execution model:

- The compiler defines contract identity and constraints
- The proposal normalizer constructs canonical proposals referencing the contract
- CRI-CORE evaluates whether the proposed action is admissible

The compiler does not participate in runtime evaluation.
It defines the contract that runtime enforcement depends on.

## Non-Responsibilities

The compiler does not:

- Execute governance validation.
- Interpret policy semantics beyond structural compilation.
- Perform runtime decision logic.
- Enforce governance rules.
- Modify or interpret proposal data at runtime.

All runtime enforcement is handled by CRI-CORE or other downstream systems.

## Forward Compatibility

Compiled contracts may include additional sections beyond those currently
enforced by CRI-CORE (e.g., approval requirements, artifact requirements,
stage constraints, invariants).

These fields are preserved for forward compatibility and may be enforced by
future versions of the execution pipeline.

## Project Status

To validate a checkout, run `python -m pytest -q`. For fresh wheel/sdist builds,
strict metadata checks, a clean wheel install, installed public API/schema/CLI
acceptance, and the complete suite against the installed package, install
`build` and `twine` and run `python scripts/check_package.py`. The check keeps
its artifacts and isolated environment under `.cache/` in this repository.

Version `0.4.0` adds deterministic target scoping to contract identity while
preserving legacy target-free compiled outputs and hashes. Runtime enforcement
of target requirements requires a Guard version that supports
`target_requirements`; no migration is required.

## License

Apache-2.0

Copyright 2026 Waveframe Labs.
