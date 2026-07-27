# Installation

## PyPI (recommended)

Prebuilt wheels are published for Python 3.8 through 3.13 on Linux
(`manylinux_2_28` x86_64 and aarch64), macOS (arm64), and Windows (amd64).
No C++ toolchain or Wirestead core checkout is required.

```bash
pip install wirestead
```

The methods below build the extension locally and are meant for contributors,
other Python versions/platforms, or consuming a custom core build.

## Development install with local core source

```bash
git clone https://github.com/wirestead/wirestead.git
git clone https://github.com/wirestead/wirestead-python.git

cd wirestead-python

python -m pip install -U pip
python -m pip install -e . \
  -Ccmake.define.WIRESTEAD_CORE_SOURCE_DIR=../wirestead
```

## Install with an installed Wirestead core package

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

## Install with vcpkg

The repository includes a `vcpkg.json` manifest that depends on
`wirestead`. This path requires a vcpkg checkout that contains the official
`wirestead` port for the matching 0.9.x release line.

```bash
export VCPKG_ROOT=/path/to/vcpkg

python -m pip install . \
  -Ccmake.define.CMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

## Smoke test

```bash
python -c "import wirestead; print(wirestead.__version__)"
```

## Local verification

```bash
scripts/verify.sh --core-source ../wirestead
```

Set `VCPKG_ROOT` to run vcpkg validation, or pass `--skip-vcpkg`. Add
`--installed-prefix /path/to/wirestead/install` to validate against an installed
core package.
