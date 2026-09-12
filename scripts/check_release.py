"""Fail on divergent current release, build, and producer metadata."""

from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def check_release(root):
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == "0.5.0"
    assert project["project"]["requires-python"] == ">=3.9"
    assert project["project"]["license"] == "Apache-2.0"
    assert project["project"]["license-files"] == ["LICENSE"]
    version_text = (root / "src/compiler/_version.py").read_text(encoding="utf-8")
    assert re.search(r'^__version__ = "0\.5\.0"$', version_text, re.MULTILINE)
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert 'version: "0.5.0"' in changelog
    assert 'status: "Unreleased candidate"' in changelog
    assert re.findall(r"^## \[.*", changelog, re.MULTILINE)[0] == "## [0.5.0] - Unreleased candidate"
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "Compiler 0.5.0 is an unreleased candidate" in readme
    assert '"version": "0.5.0"' in readme
    assert '"version": "0.4.0"' not in readme
    handoff = (root / "docs/release-0.5.0.md").read_text(encoding="utf-8")
    assert "Proposed tag: `v0.5.0`" in handoff
    assert "Status: **unreleased candidate**" in handoff
    print("Release, Python floor, Apache-2.0, and producer metadata agree: 0.5.0.", flush=True)


if __name__ == "__main__":
    check_release(Path(__file__).resolve().parents[1])
