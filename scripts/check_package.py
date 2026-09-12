"""Build a fresh sdist/wheel and validate an isolated installed package.

Install requirements/ci.txt first, then run python scripts/validate.py.
This checker can also run on its own; all work stays under .cache.
"""

import argparse
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import uuid
import zipfile

from validation_utils import run, run_suite


ROOT = Path(__file__).resolve().parents[1]


def check_package(work):
    work.mkdir(parents=True, exist_ok=False)
    distributions = work / "dist"
    # Default build builds an sdist, then a wheel FROM that sdist. No isolation:
    # the caller installed the complete hash-pinned CI/build/test toolchain.
    run(sys.executable, "-m", "build", "--no-isolation", "--outdir", distributions, cwd=ROOT)
    wheel, = distributions.glob("*.whl")
    sdist, = distributions.glob("*.tar.gz")
    assert wheel.name == "cricore_contract_compiler-0.5.0-py3-none-any.whl"
    assert sdist.name == "cricore_contract_compiler-0.5.0.tar.gz"
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (wheel, sdist)}
    (work / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for name, digest in hashes.items()), encoding="utf-8")
    schemas = {f"compiler/schemas/{name}.schema.json" for name in (
        "policy", "action_policy", "compiled_action_contract"
    )}

    def check_metadata(data):
        info = BytesParser().parsebytes(data)
        assert info["Name"] == "cricore-contract-compiler"
        assert info["Version"] == "0.5.0"
        assert info["Requires-Python"] == ">=3.9"
        assert info["License-Expression"] == "Apache-2.0"
        assert info.get_all("License-File") == ["LICENSE"]

    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert schemas <= set(names)
        for name in schemas | {"compiler/__init__.py", "compiler/_version.py", "compiler/compile_action_policy.py"}:
            assert archive.read(name) == (ROOT / "src" / name).read_bytes()
        check_metadata(archive.read("cricore_contract_compiler-0.5.0.dist-info/METADATA"))
        assert archive.read("cricore_contract_compiler-0.5.0.dist-info/licenses/LICENSE") == (ROOT / "LICENSE").read_bytes()
    with tarfile.open(sdist) as archive:
        members = {member.name.split("/", 1)[-1]: member for member in archive.getmembers() if "/" in member.name}
        assert {f"src/{name}" for name in schemas} <= set(members)
        for name in ("scripts/check_package.py", "tests/fixtures/actions/mixed.compiled.json",
                     "schema/policy.schema.json", "requirements/ci.txt", "docs/release-0.5.0.md"):
            assert name in members
        for name in schemas:
            assert archive.extractfile(members[f"src/{name}"]).read() == (ROOT / "src" / name).read_bytes()
        check_metadata(archive.extractfile(members["PKG-INFO"]).read())
    run(sys.executable, "-m", "twine", "check", "--strict", wheel, sdist, cwd=ROOT)

    environment = work / "venv"
    run(sys.executable, "-m", "venv", environment, cwd=work)
    bin_dir = environment / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    run(python, "-I", "-m", "pip", "install", "--require-hashes", "-r", ROOT / "requirements/ci.txt", cwd=work)
    run(python, "-I", "-m", "pip", "install", "--no-deps", wheel, cwd=work)
    run(python, "-I", "-m", "pip", "check", cwd=work)
    freeze = subprocess.check_output([str(python), "-I", "-m", "pip", "freeze", "--all"], cwd=work, text=True)
    (work / "installed-dependencies.txt").write_text(freeze, encoding="utf-8")

    # Copy only acceptance inputs, never source modules or source pytest config.
    acceptance = work / "acceptance"
    acceptance.mkdir()
    for directory in ("tests", "schema", "src/compiler/schemas"):
        shutil.copytree(ROOT / directory, acceptance / directory, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / "scripts/check_contracts.py", acceptance / "check_contracts.py")
    (acceptance / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    run(python, "-I", acceptance / "check_contracts.py", acceptance, work / "contracts", cwd=acceptance)
    counts = run_suite(python, acceptance, work / "installed-tests.xml", installed=True)

    cli = bin_dir / ("cricore-compile-policy.exe" if os.name == "nt" else "cricore-compile-policy")
    run(cli, "--help", cwd=acceptance)
    output = work / "legacy.json"
    for source in sorted((acceptance / "tests/fixtures/legacy").glob("*.policy.json")):
        historical = json.loads(source.with_name(source.name.replace(".policy.", ".artifact.")).read_bytes())
        assert historical["_compiler"]["version"] == "0.4.0"
        historical["_compiler"]["version"] = "0.5.0"
        expected = (json.dumps(historical, indent=2, sort_keys=True) + "\n").encode("utf-8")
        for attempt in range(2):
            run(cli, source, output, cwd=acceptance)
            assert output.read_bytes().replace(b"\r\n", b"\n") == expected
    retained = output.read_bytes()
    policy = json.loads((acceptance / "tests/fixtures/actions/mixed.policy.json").read_text(encoding="utf-8"))
    invalid = [policy, {k: v for k, v in policy.items() if k != "schema_version"},
               {**policy, "schema_version": "unknown.v1"}, {**policy, "targets": {}},
               {"schema_version": None}, {"contract_id": "bad", "contract_version": "1.0.0", "targets": {}},
               {"contract_id": "bad", "contract_version": "1.0.0", "targets": {"allow": "bad"}}, {}]
    rejected = work / "rejected.json"
    errors = []
    for index, value in enumerate([json.dumps(value) for value in invalid] + ["{invalid JSON"]):
        rejected.write_text(value, encoding="utf-8")
        for destination in (output, work / "must-not-exist.json"):
            result = subprocess.run([str(cli), str(rejected), str(destination)], cwd=acceptance, capture_output=True, text=True)
            assert result.returncode != 0
            if index < 5:
                assert "compile_action_policy" in result.stderr
            assert output.read_bytes() == retained
            assert not (work / "must-not-exist.json").exists()
            errors.append({"input": value, "exit_code": result.returncode, "stderr": result.stderr})
    (work / "cli-rejections.json").write_text(json.dumps(errors, indent=2) + "\n", encoding="utf-8")
    evidence = {"distributions": hashes, "installed_tests": counts, "pip_check": "passed",
                "public_api_schemas": "passed", "cli": "passed", "cli_rejections": len(errors)}
    (work / "package.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"Package acceptance passed. Artifacts: {distributions}", flush=True)
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".cache" / f"package-check-{uuid.uuid4().hex}")
    check_package(parser.parse_args().output.resolve())
