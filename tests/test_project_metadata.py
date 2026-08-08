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


def test_core_ref_matches_the_version_this_release_claims_to_bind():
    """The pin and the compatibility table have to agree.

    WIRESTEAD_CORE_REF is what CI actually checks out and builds against, while
    docs/compatibility.md is what users read. Nothing tied them together, so
    0.9.3 shipped a wheel built against the v0.9.2 core while the table claimed
    v0.9.3 - green CI throughout, because every existing check looked at the
    version strings and none looked at the pin.
    """
    package_version = runpy.run_path(
        str(PROJECT_ROOT / "src" / "wirestead" / "_version.py")
    )["__version__"]
    core_ref = (PROJECT_ROOT / "WIRESTEAD_CORE_REF").read_text(encoding="ascii").strip()

    table = (PROJECT_ROOT / "docs" / "compatibility.md").read_text(encoding="utf-8")
    rows = dict(
        re.findall(r"^\|\s*([0-9][^|\s]*)\s*\|\s*(v[^|\s]*)\s*\|", table, re.M)
    )

    assert package_version in rows, (
        f"docs/compatibility.md has no validated-core row for {package_version}"
    )
    assert rows[package_version] == core_ref, (
        f"WIRESTEAD_CORE_REF is {core_ref} but docs/compatibility.md says "
        f"{package_version} was validated against {rows[package_version]}"
    )
