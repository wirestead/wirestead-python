# Changelog

All notable changes to Wirestead Python are documented in this file.

## Unreleased

### Added

- Expanded the wheel build matrix to CPython 3.11 and 3.13, so wheels now cover
  CPython 3.10 through 3.13 across the declared Linux, macOS, and Windows wheel
  targets. v0.9.1 shipped 3.8, 3.10, and 3.12.
- Added a CI check that resolves the `test` extra against the installed
  package's own metadata for the running interpreter, so a dependency floor
  with no distribution for a supported Python version fails CI instead of
  reaching PyPI.
- Added a CI job that builds the source distribution and installs it against a
  Wirestead core checkout. The source distribution is published to PyPI and is
  what `pip` falls back to on platforms without a wheel, but nothing installed
  it before, so a file missing from it would have surfaced only for users.
- Added installed-wheel consumer smoke validation that installs the built wheel
  into a fresh virtual environment from a downloaded artifact, verifies the
  imported module is not coming from the source tree, checks the public version,
  and runs TCP and UDP loopback over `127.0.0.1`.
- Added UDP loopback integration coverage for the Python bindings.

### Changed

- Use the runtime `_version.py` value as the package, CMake, test, and wheel
  validation version source, and centralize the compatible core Git ref in
  `WIRESTEAD_CORE_REF`.
- Validate synchronous, asyncio, and installed-wheel UDS loopback behavior on
  Windows instead of excluding Windows from the UDS test suite.
- Aligned PyPI metadata URLs, Python classifiers, README support tables, and CI
  build dependency pins with the current 0.9.x support policy.
- Re-enabled vcpkg package consumption in CI now that `wirestead` is available
  from the official vcpkg registry.

### Removed

- Dropped support for Python 3.8 and 3.9. `requires-python` is now `>=3.10`,
  and the wheel, CI, and consumer-smoke matrices no longer build those
  interpreters. Both are past upstream end-of-life (3.8 in October 2024, 3.9 in
  October 2025), the C++ core targets C++20 toolchains that the distributions
  shipping those interpreters do not provide by default, and PyPI download data
  for v0.9.0 and v0.9.1 recorded no installs on either version. `pip` resolves
  existing 3.8 and 3.9 environments to v0.9.1, so they are pinned rather than
  broken.

### Fixed

- A source build that cannot find a Wirestead C++ core now explains why and
  how to supply one, instead of failing with a bare `find_package` error. This
  is the failure users hit when `pip` falls back to the source distribution on
  a platform with no matching wheel.
- Fixed the `test` extra pinning a `pytest-asyncio` floor with no distribution
  for every supported interpreter, which made `pip install wirestead[test]`
  fail to resolve on the Python 3.8 and 3.9 wheels published in v0.9.1.

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
