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

## CLI Usage

Compile a governance policy into a compiled contract artifact:

```bash
cricore-compile-policy policy.json compiled_contract.json
```

The output is a deterministic JSON artifact that includes compiler metadata,
compiled governance requirements, invariants, and a contract hash.

## Python Usage

The compiler can also be used programmatically:

```python
from compiler.compile_policy import compile_policy

policy = {
    "contract_id": "finance-policy",
    "contract_version": "0.3.0",
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

## Policy Input

Policies are JSON objects with a required contract identity:

```json
{
  "contract_id": "finance-policy",
  "contract_version": "0.3.0"
}
```

The compiler currently recognizes these optional sections:

- `authority.required_roles`: list of role names required by the contract.
- `approvals.thresholds`: list of threshold-based approval requirements.
- `artifacts.required`: list of required governance artifact names.
- `stages.allowed_transitions`: list of allowed lifecycle transition objects.
- `constraints`: list of explicit structural constraints.

`contract_version` must follow semantic version format: `X.Y.Z`.

## Compiled Output

The compiled contract always includes these top-level sections:

```json
{
  "contract_id": "finance-policy",
  "contract_version": "0.3.0",
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
    "version": "0.2.0",
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

Version `0.3.0` aligns the compiler with the CRI-CORE structured execution model,
ensuring deterministic contract identity, stable output structure, and compatibility
with downstream proposal normalization and enforcement.

## License

Apache-2.0

Copyright 2026 Waveframe Labs.
