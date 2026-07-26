# Wirestead Python

Python bindings for the Wirestead C++ communication library.

This repository contains the Python package and pybind11 bindings. The C++ core
lives in the main Wirestead repository.

- Core library: https://github.com/wirestead/wirestead
- Python bindings: https://github.com/wirestead/wirestead-python

## Package Layout

- Python package: `wirestead`
- Compiled extension: `wirestead._core`

## Documentation

- Installation: [docs/installation.md](docs/installation.md)
- API overview: [docs/api.md](docs/api.md)
- Compatibility: [docs/compatibility.md](docs/compatibility.md)
- Packet Probe Viewer IPC Example: [docs/packet-probe-viewer-ipc.md](docs/packet-probe-viewer-ipc.md)
- Packaging & PyInstaller Notes: [docs/packaging.md](docs/packaging.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Release policy: [docs/release.md](docs/release.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

The first split release keeps the existing binding API surface. It does not add
new transport functionality.

## Installation

### PyPI (recommended)

Prebuilt wheels are published for Linux (manylinux x86_64 and aarch64), macOS
(arm64), and Windows (amd64) on Python 3.8, 3.10, and 3.12. No C++ toolchain
or Wirestead core checkout is required.

```bash
pip install wirestead
```

The remaining installation methods below build the extension locally and are
meant for contributors, other Python versions/platforms, or consuming a
custom core build.

### Development mode with local core source

```bash
git clone https://github.com/wirestead/wirestead.git
git clone https://github.com/wirestead/wirestead-python.git

cd wirestead-python

python -m pip install -U pip
python -m pip install -e . \
  -Ccmake.define.WIRESTEAD_CORE_SOURCE_DIR=../wirestead
```

### Installed core package

```bash
cmake -S ../wirestead -B ../wirestead-build \
  -DCMAKE_BUILD_TYPE=Release \
  -DWIRESTEAD_BUILD_TESTS=OFF \
  -DWIRESTEAD_BUILD_DOCS=OFF

cmake --build ../wirestead-build --parallel
cmake --install ../wirestead-build --prefix ../wirestead-install

cd ../wirestead-python
python -m pip install . \
  -Ccmake.define.CMAKE_PREFIX_PATH=../wirestead-install
```

### vcpkg core package

The repository includes a `vcpkg.json` manifest that depends on
`wirestead`.

```bash
export VCPKG_ROOT=/path/to/vcpkg

python -m pip install . \
  -Ccmake.define.CMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

## Import Smoke

```bash
python -c "import wirestead; print(wirestead.__version__)"
```

## Tests

```bash
python -m pytest -q -m "not serial"
```

Real TCP loopback coverage is marked as `integration` and is disabled unless
explicitly requested:

```bash
WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 python -m pytest -q -m "integration"
```

For local validation across supported core consumption paths, use:

```bash
scripts/verify.sh --core-source ../wirestead
```

Set `VCPKG_ROOT` to enable the vcpkg path, or pass `--skip-vcpkg` when it is
not applicable. Add `--installed-prefix /path/to/wirestead/install` to validate
against an installed core package.

## Compatibility

Wirestead Python follows the same minor release line as the Wirestead C++ core.

| Wirestead Python | Wirestead core |
|---|---|
| 0.9.x | 0.9.x |

Patch versions may differ when Python-only packaging, binding, documentation, or
CI fixes do not require a matching core patch release.

The Python package is currently experimental until the C++ public API reaches a
stable release line.
