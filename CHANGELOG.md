---
title: "CRI-CORE Contract Compiler — Changelog"
filetype: "documentation"
type: "changelog"
domain: "governance-tooling"
version: "0.2.1"
doi: "TBD-0.2.1"
status: "Active"
created: "2026-03-11"
updated: "2026-04-23"

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
  - "CRI-CORE-CONTRACT-COMPILER-CHANGELOG-v0.2.1"
---

# Changelog

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

## [0.1.0] – 2026-03-11

### Added
- Initial CRI-CORE governance policy compiler
- Deterministic policy → contract compilation
- Canonical contract hashing
- CLI interface for compiling policy files
- Schema validation tests
