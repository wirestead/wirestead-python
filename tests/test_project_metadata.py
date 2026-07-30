import json
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
