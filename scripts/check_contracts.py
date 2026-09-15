"""Representative byte/hash acceptance shared by source and isolated installs."""

import argparse
import hashlib
from importlib import metadata
from importlib.resources import files
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.source:
        sys.path.insert(0, str(root / "src"))

    import compiler
    from compiler import compile_action_policy
    from compiler.compile_policy import compile_policy
    from compiler.compile_policy_file import compile_policy_file
    from jsonschema import Draft202012Validator

    expected_root = root / "src" if args.source else Path(sys.prefix).resolve()
    assert Path(compiler.__file__).resolve().is_relative_to(expected_root)
    assert compiler.__version__ == "0.5.0"
    if not args.source:
        assert metadata.version("cricore-contract-compiler") == compiler.__version__
    print("Validated import:", compiler.__file__, flush=True)

    schemas = {}
    for name in ("policy", "action_policy", "compiled_action_contract"):
        resource = files("compiler").joinpath(f"schemas/{name}.schema.json")
        schemas[name] = json.loads(resource.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schemas[name])
        assert schemas[name] == json.loads((root / f"src/compiler/schemas/{name}.schema.json").read_text(encoding="utf-8"))

    args.output.mkdir(parents=True, exist_ok=True)
    evidence = {}
    for family, api in (("actions", compile_action_policy), ("legacy", compile_policy)):
        policies = sorted((root / "tests/fixtures" / family).glob("*.policy.json"))
        assert len(policies) == (3 if family == "actions" else 6)
        for source in policies:
            name = source.name.removesuffix(".policy.json")
            expected_path = source.with_name(f"{name}.compiled.json")
            expected = expected_path.read_text(encoding="utf-8")
            results = []
            for attempt in range(2):
                policy = json.loads(source.read_text(encoding="utf-8"))
                compiled = api(policy)
                rendered = json.dumps(compiled, indent=2) + "\n"
                assert rendered == expected, source
                unsigned = {k: v for k, v in compiled.items() if k != "contract_hash"}
                assert hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest() == compiled["contract_hash"]
                if family == "actions":
                    assert set(compiled) == {"schema_version", "contract_id", "contract_version", "action_requirements", "contract_hash"}
                    Draft202012Validator(schemas["action_policy"]).validate(policy)
                    Draft202012Validator(schemas["compiled_action_contract"]).validate(compiled)
                else:
                    historical_bytes = source.with_name(f"{name}.artifact.json").read_bytes().replace(b"\r\n", b"\n")
                    historical = json.loads(historical_bytes)
                    assert historical["_compiler"]["version"] == "0.4.0"
                    destination = args.output / f"{family}-{name}-{attempt}.artifact.json"
                    compile_policy_file(source, destination)
                    written = json.loads(destination.read_bytes())
                    assert written["_compiler"]["version"] == compiler.__version__
                    written["_compiler"]["version"] = "0.4.0"
                    assert (json.dumps(written, indent=2, sort_keys=True) + "\n").encode("utf-8") == historical_bytes
                    if attempt:
                        assert destination.read_bytes() == (args.output / f"{family}-{name}-0.artifact.json").read_bytes()
                data = rendered.encode("utf-8")
                (args.output / f"{family}-{name}-{attempt}.compiled.json").write_bytes(data)
                results.append(data)
            assert results[0] == results[1]
            evidence[f"{family}/{name}"] = {
                "contract_hash": compiled["contract_hash"],
                "compiled_bytes_sha256": hashlib.sha256(results[0]).hexdigest(),
            }
    (args.output / "contracts.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print("All nine representative outputs and hashes are byte-stable.", flush=True)


if __name__ == "__main__":
    main()
