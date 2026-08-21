---
title: "CRI-CORE Contract Compiler - Changelog"
filetype: "documentation"
type: "changelog"
domain: "governance-tooling"
version: "0.4.0"
doi: "TBD-0.4.0"
status: "Active"
created: "2026-03-11"
updated: "2026-08-21"

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

anchors:
  - "CRI-CORE-CONTRACT-COMPILER-CHANGELOG-v0.4.0"
---

# Changelog

## [Unreleased]

## [0.4.0] - 2026-08-21

### Added
- Deterministic target allow/deny scope.
- Exact and literal prefix match declarations.
- `target_requirements` included in contract identity.

### Safety
- Empty scopes rejected.
- Malformed or blank rules rejected.
- No glob, regex, or implicit normalization.
- Legacy target-free output and hashes unchanged.

### Compatibility
- Existing policies remain valid.
- Existing compiled contracts remain valid.
- Runtime enforcement requires a Guard version supporting `target_requirements`.
- No migration is required.

## [0.3.0] - 2026-05-03

### Changed
- Aligned the compiler with the CRI-CORE structured execution protocol and documented deterministic contract identity behavior.
- Clarified the compiler's role relative to CRI-CORE, proposal normalization, and pass-through contract handling.
- Standardized release documentation around protocol-aligned `0.3.0` metadata and status.

### Added
- Explicit documentation for contract identity guarantees, pass-through requirements, protocol role, and forward compatibility behavior.
- Test coverage asserting that compiled contracts always include `contract_id`, `contract_version`, and `contract_hash`.

## [0.2.1] - 2026-04-23

### Added
- Support for `approvals.thresholds` in input policies and `approval_requirements.thresholds` in compiled contracts.
- Compiler test coverage for approval threshold compilation and invalid approval threshold types.
- Schema fixture coverage for valid approval-threshold policies.

### Changed
- Expanded the policy schema to recognize approval threshold definitions.
- Extended the fixed compiled contract shape to always include `approval_requirements`.
- Preserved approval threshold data in deterministic compiled artifacts alongside existing invariants and hash generation.

## [0.2.0] - 2026-04-22

### Changed
- Populated compiled authority, artifact, and stage requirement sections from policy schema fields.
- Preserved separation-of-duties invariants through explicit constraint compilation.
- Removed legacy compilation of `authority.separation_of_duties` into authority requirements.
- Canonicalized compiled contract structures before hashing for stable deterministic contract hashes.
- Kept compiled contract section keys present even when sections are empty.

### Added
- Minimal compile-time type validation for required roles, required artifacts, allowed transitions, and contract versions.
- Negative compiler coverage for invalid authority role definitions.

## [0.1.0] - 2026-03-11

### Added
- Initial CRI-CORE governance policy compiler.
- Deterministic policy-to-contract compilation.
- Canonical contract hashing.
- CLI interface for compiling policy files.
- Schema validation tests.
