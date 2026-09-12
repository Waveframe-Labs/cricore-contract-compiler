"""Shared subprocess and no-skips suite checks for release validation."""

import subprocess
import xml.etree.ElementTree as ET


def run(*args, cwd):
    print("+ " + " ".join(str(arg) for arg in args), flush=True)
    subprocess.run([str(arg) for arg in args], cwd=cwd, check=True)


def run_suite(python, root, report, installed=False):
    isolation = ["-I"] if installed else []
    options = ["-c", root / "pytest.ini", "-o", "pythonpath=", "--import-mode=importlib"] if installed else []
    run(python, *isolation, "-m", "pytest", "-q", *options, "--junitxml", report, "tests", cwd=root)
    suites = ET.parse(report).getroot().iter("testsuite")
    counts = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
    for suite in suites:
        for key in counts:
            counts[key] += int(suite.get(key, 0))
    assert counts["tests"] > 0, counts
    assert counts["failures"] == counts["errors"] == counts["skipped"] == 0, counts
    return counts
