import json
import re
import runpy
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_vcpkg_manifest_matches_package_version():
    package_version = runpy.run_path(
        str(PROJECT_ROOT / "src" / "wirestead" / "_version.py")
    )["__version__"]
    manifest = json.loads((PROJECT_ROOT / "vcpkg.json").read_text(encoding="utf-8"))

    assert manifest["version-string"] == package_version


def test_core_ref_is_a_single_tag():
    core_ref = (PROJECT_ROOT / "WIRESTEAD_CORE_REF").read_text(encoding="ascii")
    lines = core_ref.splitlines()

    assert len(lines) == 1
    assert lines[0] == lines[0].strip()
    assert lines[0].startswith("v")


def test_vcpkg_baseline_is_a_single_full_commit_sha():
    baseline = (PROJECT_ROOT / "VCPKG_BASELINE").read_text(encoding="ascii")
    lines = baseline.splitlines()

    assert len(lines) == 1
    assert lines[0] == lines[0].strip()
    # A branch name or short SHA here would silently reintroduce the drift the
    # pin exists to prevent, so require a full 40-character commit SHA.
    assert re.fullmatch(r"[0-9a-f]{40}", lines[0])
