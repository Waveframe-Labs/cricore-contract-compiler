# Compiler 0.5.0 release handoff

Status: **unreleased candidate**. Proposed tag: `v0.5.0` (not created).

This candidate is stacked on draft #6, branch `feat/issue-5-action-policy`, at
`3b91fcc03c804804b2ace7302f37340a787496d9`. The base head must remain intact.
The stacked draft PR records the final exact head, CI links, selected wheel
and sdist SHA-256 values, and the outcomes of all four validation jobs. Keeping
those final identifiers in the PR avoids a self-referential commit hash here.

## Candidate behavior

Use `from compiler import compile_action_policy` for independent create/modify
restrictions. The reviewed `action_policy.v1` and `compiled_action_contract.v1`
schemas, five-field result, canonicalization, and committed action hashes are
unchanged. The CLI remains legacy-only and rejects action/discriminator inputs.
Ledger must require this named API without fallback. Sibling dependency pin
changes and integration work belong to subsequent tasks.

New legacy artifacts use `_compiler.version = "0.5.0"`. That wrapper field is
outside the hashed compiled contract. All historical 0.4.0 fixtures remain
unchanged; validation restores only the producer version for a byte comparison
with each historical artifact, allowing the existing platform newline difference.
Existing retained artifacts are never migrated or rewritten.

## Reproduce validation

Use a fresh virtual environment with Python 3.9 or 3.14, from this checkout:

```text
python -m pip install --require-hashes -r requirements/ci.txt
python scripts/validate.py --expected-commit FULL_40_CHARACTER_HEAD_SHA
```

The driver runs release consistency, `pip check`, the complete source suite,
and nine representative compilations twice. Tests cover create-only, modify-only,
mixed actions, independent restrictions, malformed inputs, legacy allow/deny,
overlapping deny-precedence inputs, empty/malformed scopes, and target-free
contracts. It rejects skipped tests and compares compiled bytes and hashes.

The existing package checker builds a fresh sdist, then a wheel **from that
sdist**, using `build --no-isolation` in the pinned validation environment.
It runs `twine check --strict`, checks both archives' metadata and schemas,
verifies the wheel's public API and Apache-2.0 license, and installs into a
fresh venv. Acceptance inputs are copied to a separate working directory
without source modules or source pytest configuration; Python uses `-I`,
the public API's location must be under the fresh venv, and the complete suite
runs with importlib import mode and an empty pythonpath. Both source and
installed suite counts must match with zero failures, errors, or skips.

All six legacy policies run twice through the installed console script.
Action/discriminator payloads, invalid scope, and malformed JSON must fail
without creating a new output or overwriting an existing artifact. The clean
environment passes `pip check`. The action API is exercised directly through
its public import, with packaged schemas and exact reviewed output fixtures.

## Toolchain and CI

`requirements/ci.in` lists the direct toolchain pins; `requirements/ci.txt`
locks all transitive dependencies and distribution hashes across platforms.
It was generated with uv 0.8.22:

```text
uv pip compile requirements/ci.in --universal --python-version 3.9 --generate-hashes --output-file requirements/ci.txt
```

Python 3.9 uses pip 25.2 (25.3 requires Python 3.10). Python 3.14 uses pip 25.3.
Both use pytest 8.4.2, build 1.3.0, twine 6.2.0, setuptools 77.0.3, wheel 0.45.1,
and jsonschema 4.25.1. Python <3.11 uses tomli 2.2.1. The generated lock also
selects interpreter-compatible transitive pins, notably referencing 0.36.2 /
0.37.0, rpds-py 0.27.1 / 2026.6.3, and readme-renderer 44.0 / 46.0 for
3.9 / 3.14. These are validation constraints, not a raised package Python floor.
Setuptools 77.0.3 supports the SPDX license metadata used for strict checks;
the [setuptools documentation](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
describes support introduced in 77.0.0. Apache-2.0 terms are unchanged.

The workflow validates PRs targeting `main` or the stacked base, pushes to
`main`, and manual full-SHA requests. It uses read-only repository permissions,
SHA-pinned actions, cancellation of superseded runs, and a non-fail-fast
Windows 2022 / Ubuntu 24.04 × Python 3.9 / 3.14 matrix. PR runs explicitly check
out the PR head rather than GitHub's synthetic merge commit. Provenance checks
the actual checkout SHA and clean status against the requested commit.

Once this new workflow is available to GitHub's manual-dispatch mechanism:

```text
gh workflow run validate.yml --ref BRANCH --field commit=FULL_40_CHARACTER_HEAD_SHA
```

Per-job CI artifacts retain 30 days of provenance (actual Python, platform,
commit, run/attempt), source/installed JUnit reports and dependency versions,
representative compiled outputs and hashes, CLI rejection evidence, wheel,
sdist, and `SHA256SUMS`. Archive hashes identify specific builds; archive bytes
need not match between jobs because of packaging timestamps and platform
newlines. Compiled contract bytes and hashes must match the reviewed fixtures.

## Remaining release gates

1. Review both draft PRs and approve the compiler candidate. Neither is merged
   or marked ready by this task. Configure required validation checks in branch
   protection through the repository's normal administrative review if needed.
2. Advance Ledger to require the new API with no fallback, then prepare and
   validate Ledger, Guard, and Cloud with explicit reviewed compiler pins in
   their separate tasks. Current sibling development pins remain unchanged.
3. Complete the coordinated creation-release checklist in
   [Cloud #143](https://github.com/Waveframe-Labs/Waveframe-Cloud/issues/143), including
   downstream integration/acceptance and release authorization. Publication
   remains blocked until those gates are satisfied.
4. At actual release time, revalidate the approved release commit, finalize
   release dates/status and artifact selection, retain the final hashes beyond
   CI expiry, then separately authorize merge, tag, GitHub/PyPI publication,
   deployment, and activation. None of those actions is part of this task.

Deletion, rename, macOS, new schema versions, policy semantics, path grammar,
and runtime evaluation remain outside this candidate.
