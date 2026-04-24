---
title: "CRI-CORE Contract Compiler - Repository Overview"
filetype: "documentation"
type: "overview"
domain: "governance-tooling"
version: "0.2.1"
doi: "TBD-0.2.1"
status: "Active"
created: "2026-03-11"
updated: "2026-04-23"

author:
  name: "Waveframe Labs"
  email: "swright@waveframelabs.org"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

license: "Apache-2.0"

ai_assisted: "partial"
---

# CRI-CORE Contract Compiler

The CRI-CORE Contract Compiler is a deterministic compiler for governance
policies into CRI-CORE contract artifacts.

It bridges governance design and runtime enforcement by converting a
human-authored JSON policy into a stable, machine-readable compiled contract.
The compiled contract can then be consumed by CRI-CORE enforcement systems.

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
    "contract_version": "0.2.1",
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
  "contract_version": "0.2.1"
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
  "contract_version": "0.2.1",
  "authority_requirements": {},
  "approval_requirements": {},
  "artifact_requirements": {},
  "stage_requirements": {},
  "invariants": {},
  "contract_hash": "..."
}
```

The compiler maps policy fields into compiled contract fields as follows:

- `policy.authority.required_roles` becomes `authority_requirements.required_roles`.
- `policy.approvals.thresholds` becomes `approval_requirements.thresholds`.
- `policy.artifacts.required` becomes `artifact_requirements.required_artifacts`.
- `policy.stages.allowed_transitions` becomes `stage_requirements.allowed_transitions`.
- `constraints[type="separation_of_duties"]` becomes `invariants.separation_of_duties`.

Empty compiled sections remain present as empty objects to keep the contract
shape stable for downstream validation and hashing.

## Determinism

Compiled contracts are hashed with SHA-256 after canonicalizing the compiled
structure with sorted JSON keys. This keeps the contract hash stable for the
same compiled policy content.

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
Proposal Wrapper
        |
CRI-CORE Kernel
        |
Commit Decision
```

The compiler sits upstream of CRI-CORE runtime enforcement. It produces the
structural contract artifact that downstream systems can evaluate.

## Non-Responsibilities

The compiler does not:

- Execute governance validation.
- Interpret policy semantics beyond structural compilation.
- Perform runtime decision logic.
- Enforce governance rules.

All runtime enforcement is handled by CRI-CORE or other downstream systems.

## Project Status

Version `0.2.1` extends the compiler with approval-threshold requirements
alongside the core policy-to-contract mappings, minimal compile-time
validation, stable compiled contract shape, and deterministic contract hashing.

The project remains in early development.

## License

Apache-2.0

Copyright 2026 Waveframe Labs.
