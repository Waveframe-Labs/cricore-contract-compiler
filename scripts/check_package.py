"""Build distributions and verify the actual wheel in a fresh environment.

Run from a checkout with build and twine installed:
    python scripts/check_package.py
All artifacts and the clean environment stay under this repository's .cache.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import uuid
import zipfile


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".cache" / f"package-check-{uuid.uuid4().hex}"


def run(*args, cwd=ROOT):
    subprocess.run([str(arg) for arg in args], cwd=cwd, check=True)


def main():
    WORK.mkdir(parents=True)
    distributions = WORK / "dist"
    # build's default builds the wheel from a freshly built sdist.
    run(sys.executable, "-m", "build", "--outdir", distributions)
    wheel, = distributions.glob("*.whl")
    sdist, = distributions.glob("*.tar.gz")
    schemas = {f"compiler/schemas/{name}.schema.json" for name in (
        "policy", "action_policy", "compiled_action_contract"
    )}
    with zipfile.ZipFile(wheel) as archive:
        assert schemas <= set(archive.namelist())
        assert "compiler/compile_action_policy.py" in archive.namelist()
    with tarfile.open(sdist) as archive:
        names = {name.split("/", 1)[-1] for name in archive.getnames()}
        assert {f"src/{name}" for name in schemas} <= names
        assert "scripts/check_package.py" in names
        assert "tests/fixtures/actions/mixed.compiled.json" in names
        assert "schema/policy.schema.json" in names
    run(sys.executable, "-m", "twine", "check", "--strict", wheel, sdist)

    environment = WORK / "venv"
    run(sys.executable, "-m", "venv", environment)
    bin_dir = environment / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    run(python, "-I", "-m", "pip", "install", wheel, "pytest>=7")
    run(python, "-I", "-m", "pip", "check")

    # Run outside the source tree's import path, with Python isolation enabled.
    acceptance = WORK / "acceptance.py"
    acceptance.write_text('''import json
from importlib.resources import files
from pathlib import Path
import sys
import compiler
from compiler import compile_action_policy
from jsonschema import Draft202012Validator

root = Path(sys.argv[1])
assert Path(compiler.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
print("Installed public API:", compiler.__file__)
for name in ("create-only", "modify-only", "mixed"):
    fixtures = root / "tests/fixtures/actions"
    policy = json.loads((fixtures / f"{name}.policy.json").read_text())
    expected = json.loads((fixtures / f"{name}.compiled.json").read_text())
    compiled = compile_action_policy(policy)
    assert compiled == expected
    for schema_name, value in (("action_policy", policy), ("compiled_action_contract", compiled)):
        schema = json.loads(files("compiler").joinpath(f"schemas/{schema_name}.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
print(json.dumps(compiled, indent=2, sort_keys=True))
''', encoding="utf-8")
    run(python, "-I", acceptance, ROOT, cwd=WORK)
    run(python, "-I", "-m", "pytest", "-q", "-o", "pythonpath=", "--import-mode=importlib", "tests")

    # Exercise the installed console script as a subprocess, including exit status.
    cli = bin_dir / ("cricore-compile-policy.exe" if os.name == "nt" else "cricore-compile-policy")
    output = WORK / "legacy.json"
    run(cli, ROOT / "tests/fixtures/legacy/minimal.valid.policy.json", output, cwd=WORK)
    expected = (ROOT / "tests/fixtures/legacy/minimal.valid.artifact.json").read_bytes()
    assert output.read_bytes().replace(b"\r\n", b"\n") == expected.replace(b"\r\n", b"\n")
    policy = json.loads((ROOT / "tests/fixtures/actions/mixed.policy.json").read_text())
    for extra in [policy, {k: v for k, v in policy.items() if k != "schema_version"},
                  {**policy, "schema_version": "unknown.v1"}, {**policy, "targets": {}}]:
        source = WORK / "rejected.json"
        source.write_text(json.dumps(extra), encoding="utf-8")
        result = subprocess.run([str(cli), str(source), str(output)], cwd=WORK, capture_output=True, text=True)
        assert result.returncode != 0
        assert "compile_action_policy" in result.stderr
        assert output.read_bytes().replace(b"\r\n", b"\n") == expected.replace(b"\r\n", b"\n")
    print(f"Package acceptance passed. Artifacts: {distributions}")


if __name__ == "__main__":
    main()
