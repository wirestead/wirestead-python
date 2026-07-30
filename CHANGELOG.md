# Changelog

All notable changes to Wirestead Python are documented in this file.

## Unreleased

### Changed

- Use the runtime `_version.py` value as the package, CMake, test, and wheel
  validation version source, and centralize the compatible core Git ref in
  `WIRESTEAD_CORE_REF`.
- Validate synchronous, asyncio, and installed-wheel UDS loopback behavior on
  Windows instead of excluding Windows from the UDS test suite.

### Added

- Expanded the wheel build matrix to CPython 3.8, 3.9, 3.10, 3.11, 3.12, and
  3.13 across the declared Linux, macOS, and Windows wheel targets.
- Added installed-wheel consumer smoke validation that installs the built wheel
  into a fresh virtual environment from a downloaded artifact, verifies the
  imported module is not coming from the source tree, checks the public version,
  and runs TCP and UDP loopback over `127.0.0.1`.
- Added UDP loopback integration coverage for the Python bindings.

### Changed

- Aligned PyPI metadata URLs, Python classifiers, README support tables, and CI
  build dependency pins with the current 0.9.x support policy.
- Re-enabled vcpkg package consumption in CI now that `wirestead` is available
  from the official vcpkg registry.

## v0.9.1

Release aligned with Wirestead C++ core 0.9.1.

### Added

- Published `wirestead` to PyPI. Prebuilt wheels are available for Linux
  (manylinux x86_64 and aarch64), macOS (arm64), and Windows (amd64) on
  Python 3.8, 3.10, and 3.12; `pip install wirestead` no longer requires a
  local C++ toolchain or Wirestead core checkout.

### Removed

- Removed the `unilink` and `unilink_py` source compatibility shims. Import
  `wirestead` instead.

## v0.9.0

Release aligned with Wirestead C++ core 0.9.0.

### Changed

- Renamed the canonical Python distribution and import package to `wirestead`.
- Moved the compiled extension to `wirestead._core`.
- Updated the build to consume the canonical Wirestead C++ package, target, and
  headers.

### Compatibility

- Kept `import unilink` and `import unilink_py` as source compatibility shims
  that re-export the `wirestead` package.
- Kept `UNILINK_CORE_SOURCE_DIR` as a build-time fallback for
  `WIRESTEAD_CORE_SOURCE_DIR`.

## v0.7.4

Release aligned with unilink C++ core 0.7.4.

### Changed

- Synced Python package metadata, runtime version, tests, documentation, and
  CI validation with the unilink C++ core 0.7.4 release line.
- Kept build and release dependency installation aligned with pybind11 2.x.

## v0.7.3

### Changed

- Synced Python package metadata with the unilink C++ core 0.7.3 release line.
- Updated CI to validate against unilink core `v0.7.3`.
- Clarified minor-line compatibility policy for `unilink-python`.

## v0.7.2

Initial split release aligned with unilink C++ core 0.7.2.

### Added

- pybind11 bindings migrated from the unilink core repository.
- scikit-build-core packaging for the `unilink` Python package.
- Local unilink core source build mode through `UNILINK_CORE_SOURCE_DIR`.
- Installed unilink CMake package build mode through `CMAKE_PREFIX_PATH`.
- Compatibility import shim for `unilink_py`.
- Import and API smoke tests.
- Linux, macOS, and Windows CI for Python 3.8, 3.10, and 3.12.

### Notes

- The Python API remains experimental while the unilink C++ public API is
  pre-1.0.
- unilink-python follows the unilink core minor release line. The 0.7.x Python
  package line targets the 0.7.x core line.
- Patch releases may contain Python-only packaging, CI, documentation, or
  binding fixes as long as they remain compatible with the same core minor
  release line.
