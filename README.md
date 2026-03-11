---
title: "CRI-CORE Contract Compiler — Repository Overview"
filetype: "documentation"
type: "overview"
domain: "governance-tooling"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-03-11"
updated: "2026-03-11"

author:
name: "Shawn C. Wright"
email: "[swright@waveframelabs.org](mailto:swright@waveframelabs.org)"
orcid: "https://orcid.org/0009-0006-6043-9295"

maintainer:
name: "Waveframe Labs"
url: "https://waveframelabs.org"

license: "Apache-2.0"

ai_assisted: "partial"
---

# CRI-CORE Contract Compiler

The CRI-CORE Contract Compiler converts human-authored governance definitions into canonical compiled contracts used by the CRI-CORE enforcement kernel.

Its purpose is to bridge governance design and runtime enforcement by producing deterministic, machine-readable contract artifacts.

The compiler does not execute governance logic and does not participate in runtime validation. It exists purely to compile governance structure into a form that can be consumed by enforcement systems.

---

## Installation

Install from PyPI:

```
pip install cricore-contract-compiler
```

Requires Python 3.10 or later.

---

## CLI Usage

Compile a governance policy into a compiled contract artifact:

```
cricore-compile-policy policy.json compiled_contract.json
```

This produces a deterministic compiled contract artifact suitable for use by CRI-CORE.

---

## Python Usage

The compiler can also be used programmatically.

```python
from compiler.compile_policy import compile_policy

policy = {
    "contract_id": "finance-policy",
    "contract_version": "0.1.0"
}

compiled_contract = compile_policy(policy)
```

---

## Position in the Governance Pipeline

The compiler sits upstream of the runtime enforcement system.

```
Governance Policy
        ↓
Contract Compiler
        ↓
Compiled Contract
        ↓
Proposal Wrapper
        ↓
CRI-CORE Kernel
        ↓
Commit Decision
```

The compiled contract defines the structural governance requirements that must be satisfied before a state mutation can be committed.

---

## Responsibilities

The compiler is responsible for producing canonical contract artifacts that define:

* Required roles
* Authority separation constraints
* Required governance artifacts
* Allowed lifecycle transitions
* Contract identity and versioning
* Contract hashing for reproducibility

The output of the compiler is a deterministic contract artifact that can be referenced during runtime enforcement.

---

## Non-Responsibilities

The compiler does **not**:

* Execute governance validation
* Interpret policy semantics
* Perform runtime decision logic
* Enforce governance rules

All enforcement is handled by the CRI-CORE kernel.

---

## Relationship to CRI-CORE

CRI-CORE performs structural admissibility validation during runtime.

The compiler provides the contract artifacts that define the structural governance requirements evaluated by the kernel.

---

## Project Status

Early development.

The initial implementation focuses on establishing a minimal contract compilation pipeline and defining the canonical compiled contract format used by CRI-CORE.

---

<div align="center">
  <sub>© 2026 Waveframe Labs — Independent Open-Science Research Entity • Governed under the Aurora Research Initiative (ARI)</sub>
</div>

