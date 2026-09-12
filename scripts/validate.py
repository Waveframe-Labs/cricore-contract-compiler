"""Run every source and installed-package gate and retain commit provenance."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import uuid

from check_package import check_package
from check_release import check_release
from validation_utils import run, run_suite


ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-commit", default=os.environ.get("EXPECTED_COMMIT"))
    parser.add_argument("--output", type=Path, default=ROOT / ".cache" / f"validation-{uuid.uuid4().hex}")
    args = parser.parse_args()
    commit = git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain")
    if args.expected_commit:
        assert re.fullmatch(r"[0-9a-fA-F]{40}", args.expected_commit), "Expected commit must be a full SHA"
        assert commit == args.expected_commit.lower(), (commit, args.expected_commit)
        assert not dirty, f"Exact-head validation requires a clean checkout: {dirty}"
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    evidence = {
        "commit": commit, "dirty": bool(dirty), "python": sys.version,
        "executable": sys.executable, "platform": platform.platform(),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "github_event": os.environ.get("GITHUB_EVENT_NAME"),
        "status": "running",
    }
    report = output / "provenance.json"
    report.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2), flush=True)
    freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze", "--all"], text=True)
    (output / "source-dependencies.txt").write_text(freeze, encoding="utf-8")
    try:
        check_release(ROOT)
        run(sys.executable, "-m", "pip", "check", cwd=ROOT)
        evidence["source_tests"] = run_suite(sys.executable, ROOT, output / "source-tests.xml")
        run(sys.executable, ROOT / "scripts/check_contracts.py", ROOT, output / "source-contracts", "--source", cwd=ROOT)
        evidence.update(check_package(output / "package"))
        assert evidence["source_tests"] == evidence["installed_tests"]
        assert (output / "source-contracts/contracts.json").read_bytes() == (output / "package/contracts/contracts.json").read_bytes()
        evidence["status"] = "passed"
    except Exception:
        evidence["status"] = "failed"
        raise
    finally:
        report.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"Complete validation passed at {commit}. Evidence: {output}", flush=True)


if __name__ == "__main__":
    main()
